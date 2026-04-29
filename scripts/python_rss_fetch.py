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



def normalize_url(url: str, source_href: str = "") -> str:
    if not url:
        return source_href or url

    # 按当前策略：优先保留 Google News 文章链接，确保可跳转
    if "news.google.com/rss/articles/" in url:
        return re.sub(r"([?&](hl|gl|ceid)=[^&]*)", "", url).rstrip("?&")

    cleaned = re.sub(r"([?&](utm_[^=&]+|ved|ei)=[^&]*)", "", url).rstrip("?&")
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

                link = normalize_url(getattr(entry, "link", ""), source_href=source_href)
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
    seen = set()
    out = []
    for item in sorted(items, key=lambda x: x.get("published_at", ""), reverse=True):
        key = (item.get("company_key"), item.get("title", "").strip().lower(), item.get("url", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Robotaxi Python RSS fetcher")
    parser.add_argument("--competitors", default="competitors.md")
    parser.add_argument("--group", choices=["all", "overseas", "china"], default="all")
    parser.add_argument("--date", default=datetime.now(CN_TZ).strftime("%Y-%m-%d"))
    parser.add_argument("--window-start-hour", type=int, default=10)
    parser.add_argument("--output", default="data/tmp/raw_news.json")
    args = parser.parse_args()

    run_date = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=CN_TZ)
    window_end = run_date.replace(hour=args.window_start_hour, minute=0, second=0, microsecond=0)
    if datetime.now(CN_TZ) < window_end:
        window_end = datetime.now(CN_TZ)
    window_start = window_end - timedelta(hours=24)

    companies, keywords = parse_competitors_md(Path(args.competitors))
    if args.group != "all":
        companies = [c for c in companies if c.region == args.group]

    all_items: List[dict] = []
    all_errors: List[str] = []

    for company in companies:
        items, errors = fetch_company_news(company, keywords, window_start, window_end)
        all_items.extend(items)
        all_errors.extend(errors)

    deduped = dedupe_news(all_items)

    result = {
        "meta": {
            "generated_at": datetime.now(CN_TZ).isoformat(),
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "group": args.group,
            "companies_total": len(companies),
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
        f"done group={args.group} companies={len(companies)} raw={len(all_items)} "
        f"deduped={len(deduped)} errors={len(all_errors)} output={output_path}"
    )


if __name__ == "__main__":
    main()
