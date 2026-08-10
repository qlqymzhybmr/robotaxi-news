import argparse
import json
import re
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.request import Request, urlopen

import feedparser


CN_TZ = timezone(timedelta(hours=8))


@dataclass
class Company:
    name: str
    is_focus: bool
    region: str  # overseas | china


@dataclass
class DirectFeed:
    company: str
    region: str
    is_focus: bool
    url: str


DIRECT_FEED_SECTIONS = {
    "## 直接订阅 RSS",
    "## X（Twitter）RSS 订阅（via 自部署 RSSHub）",
    "## 社区 / 媒体 RSS（Reddit 热帖）",
}

# Reddit blocks non-browser UAs; use a full Chrome UA to avoid 403
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

# Reddit AV relevance: title must contain at least one of these keywords
REDDIT_AV_KEYWORDS = [
    "autonomous", "self-driving", "self driving", "robotaxi", "driverless",
    "waymo", "zoox", "cruise", "aurora", "wayve", "nuro", "mobileye", "motional",
    "tesla fsd", "full self-driving", "cybercab", "autopilot",
    "recall", "crash", "accident", "collision", "incident", "investigation",
    "regulation", "citation", "permit", "approval", "lawsuit", "fine",
    "trial", "expand", "launch", "deploy", "partnership", "milestone",
    "lidar", "adas", "level 4", "level4", "l4",
    "自动驾驶", "无人驾驶",
]


def is_reddit_feed(url: str) -> bool:
    return "reddit.com" in url


def is_reddit_relevant(title: str) -> bool:
    """Reddit posts: title must contain at least one AV keyword (stricter than is_relevant)."""
    t = title.lower()
    return any(k in t for k in REDDIT_AV_KEYWORDS)


def parse_direct_feeds(path: Path) -> List[DirectFeed]:
    """Parse all direct-feed sections from competitors.md."""
    text = path.read_text(encoding="utf-8")
    feeds: List[DirectFeed] = []
    in_section = False
    for raw in text.splitlines():
        line = raw.strip()
        # Enter a recognized section
        if any(line.startswith(s) for s in DIRECT_FEED_SECTIONS):
            in_section = True
            continue
        # Leave section on any other ## heading (but keep scanning for more sections)
        if line.startswith("## "):
            in_section = False
            continue
        if in_section and line.startswith("-") and "|" in line:
            parts = [p.strip() for p in line.lstrip("-").split("|")]
            if len(parts) < 4:
                continue
            company, region, focus_raw, url = parts[0], parts[1], parts[2], parts[3]
            feeds.append(DirectFeed(
                company=company.strip(),
                region=region.strip(),
                is_focus="⭐" in focus_raw,
                url=url.strip(),
            ))
    return feeds


def is_twitter_rsshub_feed(url: str) -> bool:
    """Detect if this is a RSSHub Twitter/X feed URL."""
    return "/twitter/user/" in url


def check_twitter_auth(url: str) -> str | None:
    """
    Check if a RSSHub Twitter feed returns an auth error.
    Returns an error string if auth is expired/invalid, None if OK.
    """
    try:
        parsed = feedparser.parse(url)
    except Exception:
        return None  # network error, not auth error

    # RSSHub returns a bozo feed or specific error title when auth fails
    feed_obj = parsed.get("feed") if hasattr(parsed, "get") else getattr(parsed, "feed", {})
    feed_title = (feed_obj.get("title", "") if hasattr(feed_obj, "get") else getattr(feed_obj, "title", "")) or ""
    # Check for RSSHub error indicators in feed title or description
    error_indicators = [
        "not configured",
        "twitter api",
        "authentication",
        "unauthorized",
        "error",
    ]
    if any(ind in feed_title.lower() for ind in error_indicators):
        return f"TWITTER_AUTH_EXPIRED: {url} → feed title: {feed_title!r}"

    # feedparser sets bozo=True when feed is malformed (e.g. RSSHub error HTML/JSON)
    if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", []):
        bozo_exc = str(getattr(parsed, "bozo_exception", ""))
        return f"TWITTER_AUTH_EXPIRED: {url} → parse failed ({bozo_exc})"

    return None


def fetch_direct_feed(
    feed: DirectFeed,
    window_start: datetime,
    window_end: datetime,
) -> Tuple[List[dict], List[str]]:
    """Fetch a direct RSS feed (company blog/newsroom) and filter by time window."""
    errors: List[str] = []
    items: List[dict] = []
    is_reddit = is_reddit_feed(feed.url)
    if is_reddit:
        time.sleep(3)  # Reddit rate-limit: space requests at least 3s apart
    try:
        req_headers = {"User-Agent": BROWSER_UA} if is_reddit else {}
        parsed = feedparser.parse(feed.url, request_headers=req_headers)
    except Exception as e:
        errors.append(f"{feed.company} [direct] parse_error: {e}")
        return items, errors

    # Reddit 403 detection: report explicitly rather than silently returning 0 items
    if is_reddit:
        http_status = parsed.get("status", 0)
        if http_status == 403:
            errors.append(
                f"⚠️ [REDDIT_403] {feed.company}: {feed.url} 返回 403，"
                f"Reddit 已屏蔽该请求（UA 或 IP 被封）"
            )
            return items, errors
        if http_status == 429:
            errors.append(
                f"⚠️ [REDDIT_429] {feed.company}: {feed.url} 返回 429，触发限速"
            )
            return items, errors

    # Twitter/X RSSHub auth expiry detection
    if is_twitter_rsshub_feed(feed.url):
        auth_err = check_twitter_auth(feed.url)
        if auth_err:
            errors.append(
                f"⚠️ [TWITTER_AUTH_EXPIRED] {feed.company}: RSSHub 返回异常，"
                f"请到 Railway Variables 更新 TWITTER_AUTH_TOKEN。详情: {auth_err}"
            )
            return items, errors
    # Safe accessor for feed metadata (handles both FeedParserDict and legacy _Feed objects)
    _feed_meta = parsed.get("feed", {}) if hasattr(parsed, "get") else getattr(parsed, "feed", {}) or {}
    _feed_title = _feed_meta.get("title", feed.company) if hasattr(_feed_meta, "get") else getattr(_feed_meta, "title", feed.company)

    for entry in getattr(parsed, "entries", []):
        if not getattr(entry, "published_parsed", None):
            continue
        published = datetime.fromtimestamp(
            time.mktime(entry.published_parsed), tz=timezone.utc
        ).astimezone(CN_TZ)
        if not (window_start <= published <= window_end):
            continue

        title = getattr(entry, "title", "")

        # Reddit: title must contain AV keyword, skip pure social/discussion posts
        if is_reddit and not is_reddit_relevant(title):
            continue

        link = normalize_url(getattr(entry, "link", ""))
        items.append({
            "company": feed.company,
            "company_key": clean_company_name(feed.company),
            "region": feed.region,
            "is_focus": feed.is_focus,
            "lang": "en",
            "title": title,
            "published_at": published.isoformat(),
            "source": _feed_title,
            "source_home": feed.url,
            "url": link,
            "summary": getattr(entry, "summary", ""),
            "query": f"direct:{feed.url}",
        })

    return items, errors


def parse_competitors_md(path: Path) -> Tuple[List[Company], Dict[str, List[str]]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    region = None
    in_keywords = False
    zh_keywords: List[str] = []
    en_keywords: List[str] = []
    companies: List[Company] = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if line.startswith("## 搜索关键词"):
            in_keywords = True
            continue

        if line.startswith("## 国外组"):
            region = "overseas"
            in_keywords = False
            continue

        if line.startswith("## 国内组"):
            region = "china"
            in_keywords = False
            continue

        if in_keywords:
            if line.startswith("### 全局中文关键词"):
                current_kw = "zh"
                continue
            if line.startswith("### 全局英文关键词"):
                current_kw = "en"
                continue
            if line.startswith("###"):
                current_kw = None
                continue
            if line.startswith("-"):
                kw = line[1:].strip()
                if not kw:
                    continue
                if "current_kw" in locals() and current_kw == "zh":
                    zh_keywords.append(kw)
                elif "current_kw" in locals() and current_kw == "en":
                    en_keywords.append(kw)
            continue

        if line.startswith("-") and region in {"overseas", "china"}:
            item = line[1:].strip()
            if not item or item.startswith("--"):
                continue
            is_focus = item.startswith("⭐")
            if is_focus:
                item = item.replace("⭐", "", 1).strip()
            if item and item != "---":
                companies.append(Company(name=item, is_focus=is_focus, region=region))

    keywords = {
        "zh": zh_keywords,
        "en": en_keywords,
    }
    return companies, keywords


def build_query(company: str, keywords: List[str], compact: bool = False) -> str:
    if not keywords:
        return f'"{company}"'
    kw = keywords[:6] if compact else keywords[:10]
    joined = " OR ".join(kw)
    return f'"{company}" ({joined})'


def rss_url(query: str, lang: str) -> str:
    cfg = {
        "zh": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"},
        "en": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
    }[lang]
    q = urllib.parse.quote(query)
    return (
        f"https://news.google.com/rss/search?q={q}"
        f"&hl={cfg['hl']}&gl={cfg['gl']}&ceid={cfg['ceid']}"
    )


def clean_company_name(name: str) -> str:
    return re.split(r"\s*\(", name, maxsplit=1)[0].strip()


def extract_parenthetical(name: str) -> str:
    m = re.search(r"\((.*?)\)", name)
    return m.group(1).strip() if m else ""


def pick_query_name(company_name: str, lang: str) -> str:
    base = clean_company_name(company_name)
    paren = extract_parenthetical(company_name)

    base_has_zh = bool(re.search(r"[一-鿿]", base))
    paren_has_ascii = bool(re.search(r"[A-Za-z]", paren))

    if lang == "en":
        if base_has_zh and paren_has_ascii:
            # e.g. 小马智行 (Pony.ai) -> Pony.ai
            return re.split(r"[/,]", paren)[0].strip()
        return base

    # zh
    if base_has_zh:
        return base
    return base



def _make_search_url(title: str, lang: str = "en", site: str = "") -> str:
    """
    Build a permanent, findable search URL for an article.

    - Chinese articles (lang="zh"): use Baidu — far better coverage of
      Chinese outlets (汽车之家, 新浪汽车, 盖世汽车, 搜狐 etc.) than Google News.
    - English articles (lang="en"): use Google News search.
    - `site` (optional): scope results to a specific domain (Track A local-media).
    """
    query = title[:100]
    if site:
        query = f"{query} site:{site}"
    q = urllib.parse.quote(query)
    if lang == "zh":
        return f"https://www.baidu.com/s?wd={q}"
    params = ("en-US", "US", "US:en")
    return f"https://news.google.com/search?q={q}&hl={params[0]}&gl={params[1]}&ceid={params[2]}"


def normalize_url(url: str, source_href: str = "") -> str:
    if not url:
        return source_href or url
    cleaned = re.sub(r"([?&](utm_[^=&]+|ved|ei|oc)=[^&]*)", "", url).rstrip("?&")
    return cleaned or (source_href or url)

def is_relevant(company_name: str, title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
    base = clean_company_name(company_name)
    paren = extract_parenthetical(company_name)

    aliases = [base]
    if paren:
        aliases.extend([a.strip() for a in re.split(r"[/,]", paren) if a.strip()])

    alias_hit = False
    for a in aliases:
        if re.search(r"[A-Za-z]", a):
            if a.lower() in text:
                alias_hit = True
                break
        else:
            if a in (title + " " + summary):
                alias_hit = True
                break

    if not alias_hit:
        return False

    ad_kw = [
        "autonomous", "self-driving", "robotaxi", "driverless", "adas", "fsd", "noa", "lidar",
        "自动驾驶", "无人驾驶", "智驾", "robotaxi", "高阶智驾", "端到端", "激光雷达",
    ]
    return any(k in text for k in ad_kw)


def fetch_company_news(
    company: Company,
    keywords: Dict[str, List[str]],
    window_start: datetime,
    window_end: datetime,
) -> Tuple[List[dict], List[str]]:
    errors: List[str] = []
    items: List[dict] = []

    langs = ["zh", "en"] if company.is_focus else (["zh"] if company.region == "china" else ["en"])
    max_per_lang = 10 if company.is_focus else 5

    company_key = clean_company_name(company.name)

    for lang in langs:
        query_name = pick_query_name(company.name, lang)
        query_candidates = [
            build_query(query_name, keywords[lang], compact=False),
            build_query(query_name, keywords[lang], compact=True),
            f'"{query_name}"',
        ]

        collected_this_lang = 0
        seen_local = set()

        for query in query_candidates:
            if collected_this_lang >= max_per_lang:
                break

            url = rss_url(query, lang)
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                errors.append(f"{company.name} [{lang}] parse_error: {e}")
                continue

            for entry in getattr(feed, "entries", []):
                if collected_this_lang >= max_per_lang:
                    break

                if not getattr(entry, "published_parsed", None):
                    continue

                published = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc).astimezone(CN_TZ)
                if not (window_start <= published <= window_end):
                    continue

                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                if not is_relevant(company.name, title, summary):
                    continue

                source = ""
                source_href = ""
                if hasattr(entry, "source") and isinstance(entry.source, dict):
                    source = entry.source.get("title", "")
                    source_href = entry.source.get("href", "")

                raw_link = normalize_url(getattr(entry, "link", ""), source_href=source_href)
                # Google News RSS article URLs (CBMi…) expire within days.
                # Replace with a permanent Google News search URL for the title.
                if "news.google.com" in raw_link:
                    link = _make_search_url(title, lang=lang)
                else:
                    link = raw_link
                local_key = (title, link)

                items.append(
                    {
                        "company": company.name,
                        "company_key": company_key,
                        "region": company.region,
                        "is_focus": company.is_focus,
                        "lang": lang,
                        "title": getattr(entry, "title", ""),
                        "published_at": published.isoformat(),
                        "source": source,
                        "source_home": source_href,
                        "url": link,
                        "summary": getattr(entry, "summary", ""),
                        "query": query,
                    }
                )
                collected_this_lang += 1

            time.sleep(0.05)

    return items, errors


def dedupe_news(items: List[dict]) -> List[dict]:
    seen_keys = set()
    seen_urls: set = set()
    out = []
    for item in sorted(items, key=lambda x: x.get("published_at", ""), reverse=True):
        key = (item.get("company_key"), item.get("title", "").strip().lower(), item.get("url", ""))
        url = item.get("url", "")
        if key in seen_keys:
            continue
        # Also dedup by raw URL so Track-A and Track-B duplicates collapse
        if url and url in seen_urls:
            continue
        seen_keys.add(key)
        if url:
            seen_urls.add(url)
        out.append(item)
    return out


# ── Track A: local-media site-specific queries ─────────────────────────────────

def load_local_media(path: Path) -> dict:
    """Load company→sites mapping from data/local_media.json."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    # Strip the _comment key if present
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def is_relevant_local_media(company_name: str, title: str) -> bool:
    """Lighter relevance check for local-media articles.

    For a targeted site: query the company name in the title is sufficient signal;
    we don't require an AV keyword because local TV headlines often use plain
    language ("Waymo car floods road") that lacks technical jargon.
    """
    base = clean_company_name(company_name)
    paren = extract_parenthetical(company_name)
    aliases = [base]
    if paren:
        aliases.extend([a.strip() for a in re.split(r"[/,]", paren) if a.strip()])
    title_lower = title.lower()
    for alias in aliases:
        if re.search(r"[A-Za-z]", alias):
            if alias.lower() in title_lower:
                return True
        else:
            if alias in title:
                return True
    return False


def fetch_local_media_news(
    company_name: str,
    sites: List[dict],
    window_start: datetime,
    window_end: datetime,
) -> tuple[List[dict], List[str]]:
    """Track A: query each local outlet via Google News site: operator.

    Query format: "<CompanyName>" site:outlet.com
    No AV keywords added—the site: scope already narrows to a trusted source,
    and is_relevant_local_media() does a title-level check on the result.
    """
    errors: List[str] = []
    items: List[dict] = []
    company_key = clean_company_name(company_name)
    # Use English query name (handles cases like 小马智行 (Pony.ai) → Pony.ai)
    query_name = pick_query_name(company_name, "en")

    for site_info in sites:
        site = site_info["site"]
        site_name = site_info.get("name", site)
        city = site_info.get("city", "")

        query = f'"{query_name}" site:{site}'
        url = rss_url(query, "en")

        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            errors.append(f"{company_name} [local:{site}] parse_error: {exc}")
            continue

        for entry in getattr(feed, "entries", []):
            if not getattr(entry, "published_parsed", None):
                continue
            published = datetime.fromtimestamp(
                time.mktime(entry.published_parsed), tz=timezone.utc
            ).astimezone(CN_TZ)
            if not (window_start <= published <= window_end):
                continue

            title = getattr(entry, "title", "")
            if not is_relevant_local_media(company_name, title):
                continue

            raw_link = normalize_url(getattr(entry, "link", ""))
            # Replace expiring Google News RSS URLs with a permanent site-scoped search URL.
            if "news.google.com" in raw_link:
                link = _make_search_url(title, lang="en", site=site)
            else:
                link = raw_link
            items.append({
                "company": company_name,
                "company_key": company_key,
                "region": "overseas",
                "is_focus": True,
                "lang": "en",
                "title": title,
                "published_at": published.isoformat(),
                "source": site_name,
                "source_home": f"https://{site}",
                "url": link,
                "summary": getattr(entry, "summary", ""),
                "query": f"local_media:{site}",
                "city": city,
            })

        time.sleep(0.05)

    return items, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Robotaxi Python RSS fetcher")
    parser.add_argument("--competitors", default="competitors.md")
    parser.add_argument("--group", choices=["all", "overseas", "china"], default="all")
    parser.add_argument("--date", default=datetime.now(CN_TZ).strftime("%Y-%m-%d"))
    parser.add_argument("--window-start-hour", type=int, default=9)
    parser.add_argument("--output", default="data/tmp/raw_news.json")
    parser.add_argument("--local-media", default="data/local_media.json",
                        help="Path to local_media.json config (Track A)")
    args = parser.parse_args()

    run_date = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=CN_TZ)
    window_end = run_date.replace(hour=args.window_start_hour, minute=0, second=0, microsecond=0)
    if datetime.now(CN_TZ) < window_end:
        window_end = datetime.now(CN_TZ)
    window_start = window_end - timedelta(hours=24)

    competitors_path = Path(args.competitors)
    companies, keywords = parse_competitors_md(competitors_path)
    direct_feeds = parse_direct_feeds(competitors_path)

    if args.group != "all":
        companies = [c for c in companies if c.region == args.group]
        direct_feeds = [f for f in direct_feeds if f.region == args.group]

    all_items: List[dict] = []
    all_errors: List[str] = []

    # ── Track B: Google News general RSS (existing logic) ──────────────────────
    for company in companies:
        items, errors = fetch_company_news(company, keywords, window_start, window_end)
        all_items.extend(items)
        all_errors.extend(errors)

    for feed in direct_feeds:
        items, errors = fetch_direct_feed(feed, window_start, window_end)
        all_items.extend(items)
        all_errors.extend(errors)

    # ── Track A: local-media site-specific queries (overseas only) ─────────────
    local_media_items_total = 0
    if args.group in ("all", "overseas"):
        local_media = load_local_media(Path(args.local_media))
        for company_name, sites in local_media.items():
            items, errors = fetch_local_media_news(
                company_name, sites, window_start, window_end
            )
            all_items.extend(items)
            all_errors.extend(errors)
            local_media_items_total += len(items)

    deduped = dedupe_news(all_items)

    result = {
        "meta": {
            "generated_at": datetime.now(CN_TZ).isoformat(),
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "group": args.group,
            "companies_total": len(companies),
            "local_media_raw_total": local_media_items_total,
            "raw_items_total": len(all_items),
            "deduped_items_total": len(deduped),
            "errors_total": len(all_errors),
        },
        "keywords": keywords,
        "items": deduped,
        "errors": all_errors,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"done group={args.group} companies={len(companies)} "
        f"track_b_raw={len(all_items) - local_media_items_total} "
        f"track_a_raw={local_media_items_total} "
        f"deduped={len(deduped)} errors={len(all_errors)} output={output_path}"
    )


if __name__ == "__main__":
    main()
