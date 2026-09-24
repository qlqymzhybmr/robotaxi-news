# -*- coding: utf-8 -*-
"""Phase 3: publish data/daily/<DATE>.md into docs/data/daily.json.

Usage:
    python scripts/publish_daily.py 2026-09-24
    python scripts/publish_daily.py 2026-09-24 --dry-run

Implements workflows/daily-publish.md:
  - every item is published regardless of rating or checkbox state
  - items whose 原始发布日期 is more than 2 days from DATE are dropped
  - body markdown becomes the summary_html the website renders
  - the whole file is serialized with json.dump, never hand-built

Item schema consumed by docs/index.html - keep it in sync with ITEM_KEYS below:
    id, date, company, company_slug, group, sub_group, title,
    summary_html, source_name, source_url, published_at, rating, lang
"""
import json
import re
import sys
from datetime import date

if hasattr(sys.stdout, "reconfigure"):  # Windows console defaults to GBK
    sys.stdout.reconfigure(encoding="utf-8")

OUT = "docs/data/daily.json"
ALIASES = "docs/data/company_aliases.json"
MAX_DAY_GAP = 2

# `## ` headings -> (group, sub_group)
SECTION = {
    "国内 L4 / 智驾方案商": ("国内", "国内 L4"),
    "国内 L4": ("国内", "国内 L4"),
    "国内智驾方案商": ("国内", "国内智驾方案商"),
    "国内出行平台": ("国内", "国内出行平台"),
    "国内新势力 / 传统 OEM": ("国内", "国内新势力 / 传统 OEM"),
    "国内华为系 / 互联网大厂": ("国内", "国内华为系 / 互联网大厂"),
    "国外 L4": ("国外", "国外 L4"),
    "国外出行平台": ("国外", "国外出行平台"),
    "国外 OEM / Tier1 / 自动驾驶技术公司": ("国外", "国外 OEM / Tier1"),
    "社区热帖 (Reddit)": ("国外", "社区热帖"),
    "德州 DMV 车队登记（Phase 5）": ("国外", "国外 L4"),
}

# `### ` headings -> (company, company_slug).
# Slugs follow what docs/data/daily.json already uses most often; older entries
# carry legacy variants (weride/wenyuan, xiaoma/pony-ai, ...) that are not
# rewritten here. Add a company here rather than guessing at publish time.
COMPANY = {
    "监管 / 政策": ("行业", "industry"),
    "行业实测": ("行业", "industry"),
    "行业": ("行业", "industry"),
    # 国外 L4 / 出行平台
    "Waymo": ("Waymo", "waymo"),
    "Tesla": ("Tesla", "tesla"),
    "Zoox": ("Zoox", "zoox"),
    "Cruise": ("Cruise", "cruise"),
    "Nuro": ("Nuro", "nuro"),
    "Motional": ("Motional", "motional"),
    "May Mobility": ("May Mobility", "maymobility"),
    "Aurora": ("Aurora", "aurora"),
    "Waabi": ("Waabi", "waabi"),
    "Kodiak": ("Kodiak", "kodiak"),
    "Gatik": ("Gatik", "gatik"),
    "Avride": ("Avride", "avride"),
    "Einride": ("Einride", "einride"),
    "Tensor": ("Tensor", "tensor"),
    "Uber": ("Uber", "uber"),
    "Lyft": ("Lyft", "lyft"),
    "Grab": ("Grab", "grab"),
    "Bolt": ("Bolt", "bolt"),
    "Lucid / Bolt": ("Lucid / Bolt", "lucid"),
    "Lucid": ("Lucid", "lucid"),
    "Rivian": ("Rivian", "rivian"),
    "Wayve": ("Wayve", "wayve"),
    "Mobileye": ("Mobileye", "mobileye"),
    "NVIDIA": ("NVIDIA", "nvidia"),
    "Applied Intuition": ("Applied Intuition", "applied-intuition"),
    "Stellantis": ("Stellantis", "stellantis"),
    "大众": ("大众", "volkswagen"),
    "MOIA": ("MOIA", "moia"),
    "现代": ("现代", "hyundai"),
    "42dot": ("42dot", "42dot"),
    # 国内 L4 / 出行平台
    "小马智行": ("小马智行", "xiaoma"),
    "文远知行": ("文远知行", "weride"),
    "萝卜快跑": ("萝卜快跑", "apollo"),
    "百度": ("百度", "baidu"),
    "驭势科技": ("驭势科技", "uisee"),
    "元戎启行": ("元戎启行", "deeproute"),
    "轻舟智航": ("轻舟智航", "qingzhou"),
    "卓驭科技": ("卓驭科技", "zhuoyu"),
    "曹操出行": ("曹操出行", "caocao"),
    "如祺出行": ("如祺出行", "ruqi"),
    "享道出行": ("享道出行", "xiangdao"),
    "哈啰": ("哈啰", "hellobike"),
    "滴滴": ("滴滴", "didi"),
    "高德地图": ("高德地图", "amap"),
    "T3 出行": ("T3 出行", "t3"),
    # 国内 OEM / 方案商
    "Momenta": ("Momenta", "momenta"),
    "地平线": ("地平线", "horizon"),
    "华为 / 赛力斯": ("华为 / 赛力斯", "huawei"),
    "鸿蒙智行": ("鸿蒙智行", "harmonyos-auto"),
    "引望智能": ("引望智能", "yinwang"),
    "赛力斯": ("赛力斯", "seres"),
    "蔚来": ("蔚来", "nio"),
    "理想": ("理想", "liauto"),
    "理想 / 小鹏": ("理想", "liauto"),
    "小鹏": ("小鹏", "xpeng"),
    "小米": ("小米", "xiaomi"),
    "零跑": ("零跑", "leapmotor"),
    "比亚迪": ("比亚迪", "byd"),
    "长安": ("长安", "changan"),
    "长城": ("长城", "gwm"),
    "奇瑞": ("奇瑞", "chery"),
    "吉利": ("吉利", "geely"),
    "极氪": ("极氪", "zeekr"),
    "岚图": ("岚图", "lantu"),
    "极狐": ("极狐", "arcfox"),
    "智己": ("智己", "zhiji"),
    "埃安": ("埃安", "aion"),
    "广汽": ("广汽", "gac"),
    "上汽": ("上汽", "saic"),
    "一汽": ("一汽", "faw"),
    "一汽-大众": ("一汽-大众", "faw-vw"),
    "宁德时代": ("宁德时代", "catl"),
}

# 公司名归一表：网页与本脚本共用，保证筛选列表不再被同一家公司拆成多格
_alias_doc = json.load(open(ALIASES, encoding="utf-8"))
NAME_ALIAS = _alias_doc["alias"]
NAME_TO_SLUG = _alias_doc["name_to_slug"]

ITEM_KEYS = {"id", "date", "company", "company_slug", "group", "sub_group", "title",
             "summary_html", "source_name", "source_url", "published_at", "rating", "lang"}

ITEM_RE = re.compile(r"^- (?:\[[ xX]\] )?(⭐+) \*\*(.+?)\*\*\s*$")
SOURCE_RE = re.compile(r"\[(.+?)\]\((.+?)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
LINK_RE = re.compile(r"\[(.+?)\]\((.+?)\)")


def parse(md_path):
    """Walk the daily markdown and return one dict per news item."""
    items, cur = [], None
    group = sub_group = company = slug = None
    in_stats = False

    def flush():
        nonlocal cur
        if cur and cur["paras"]:
            items.append(cur)
        cur = None

    for ln in open(md_path, encoding="utf-8").read().split("\n"):
        if ln.startswith("## "):
            flush()
            head = ln[3:].strip()
            in_stats = head.startswith("📊")
            if head in SECTION:
                group, sub_group = SECTION[head]
                # the DMV block has no ### heading of its own
                company, slug = ("行业", "industry") if head.startswith("德州 DMV") else (None, None)
            continue
        if in_stats:
            continue
        if ln.startswith("### "):
            flush()
            head = NAME_ALIAS.get(ln[4:].strip(), ln[4:].strip())
            if head in COMPANY:
                company, slug = COMPANY[head]
            elif head in NAME_TO_SLUG:
                company, slug = head, NAME_TO_SLUG[head]
            else:
                raise SystemExit("未知公司小标题：%s（补进 scripts/publish_daily.py 的 COMPANY，"
                                 "或 docs/data/company_aliases.json 的 name_to_slug）" % head)
            continue

        m = ITEM_RE.match(ln)
        if m:
            flush()
            cur = {"rating": len(m.group(1)), "title": m.group(2), "group": group,
                   "sub_group": sub_group, "company": company, "company_slug": slug,
                   "paras": [], "sources": [], "published_at": None}
            continue
        if cur is None:
            continue

        line = ln.strip()
        if not line:
            continue
        if line.startswith("- **原始发布日期**"):
            raw = line.split("：", 1)[1].strip()
            hit = re.search(r"\d{4}-\d{2}-\d{2}", raw)
            cur["published_at"] = hit.group(0) if hit else None
            continue
        if line.startswith("- 权威源：") or line.startswith("- 辅助源："):
            hit = SOURCE_RE.search(line)
            if hit:
                cur["sources"].append((hit.group(1), hit.group(2)))
            continue
        if line.startswith("候选图："):
            continue
        cur["paras"].append(line)

    flush()
    return items


def to_html(paras):
    """Markdown paragraphs -> the <p>/<b> HTML docs/index.html renders.

    Markdown tables (the DMV fleet table) are dropped: the website shows prose only.
    """
    html = []
    for para in paras:
        stripped = para.replace("|", "").strip()
        if para.startswith("|") or (stripped and set(stripped) <= set("-: ")):
            continue
        text = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = LINK_RE.sub(lambda m: '<a href="%s" target="_blank">%s</a>' % (m.group(2), m.group(1)), text)
        text = BOLD_RE.sub(lambda m: "<b>%s</b>" % m.group(1), text)
        html.append("<p>%s</p>" % text)
    return "".join(html)


def strip_outlet(link_text):
    """'Headline - KVUE' -> 'Headline'.

    Source links in the daily markdown end with ' - <媒体名>'; daily.json stores the
    headline alone. Only the trailing segment is dropped, so headlines containing
    ' - ' keep everything before the last one.
    """
    head, sep, tail = link_text.rpartition(" - ")
    return head if sep and head else link_text


def day_gap(a, b):
    ya, ma, da = (int(x) for x in a.split("-"))
    yb, mb, db = (int(x) for x in b.split("-"))
    return abs((date(ya, ma, da) - date(yb, mb, db)).days)


def build(items, run_date):
    """Apply the date filter and turn parsed items into published records."""
    records, dropped = [], []
    for item in items:
        published = item["published_at"]
        if not published:
            dropped.append((item["title"], "缺少原始发布日期"))
            continue
        if day_gap(published, run_date) > MAX_DAY_GAP:
            dropped.append((item["title"], "原始发布日期 %s 超出 ±%d 天" % (published, MAX_DAY_GAP)))
            continue
        name, url = item["sources"][0] if item["sources"] else ("", "")
        name = strip_outlet(name)
        records.append({
            "id": "%s-%03d" % (run_date, len(records) + 1),
            "date": run_date,
            "company": item["company"],
            "company_slug": item["company_slug"],
            "group": item["group"],
            "sub_group": item["sub_group"],
            "title": item["title"],
            "summary_html": to_html(item["paras"]),
            "source_name": name,
            "source_url": url,
            "published_at": published,
            "rating": item["rating"],
            "lang": "zh" if item["group"] == "国内" else "en",
        })
    return records, dropped


def check(records):
    for r in records:
        assert set(r) == ITEM_KEYS, ("字段与网站期望不符：%s 多/少 %s" % (r["id"], set(r) ^ ITEM_KEYS))
        assert r["summary_html"].startswith("<p>") and r["summary_html"].endswith("</p>"), ("正文 HTML 异常", r["id"])
        assert "**" not in r["summary_html"], ("markdown 粗体未转换", r["id"])
        assert r["source_name"] and r["source_url"], ("缺源名称或链接", r["id"], r["title"])
        assert r["company"] and r["company_slug"], ("缺公司", r["id"], r["title"])
        assert r["company_slug"].isascii(), ("slug 非 ascii", r["id"], r["company_slug"])
        assert r["group"] in ("国内", "国外"), ("分区异常", r["id"])
        assert r["rating"] in (1, 2, 3), ("评级异常", r["id"])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    if len(args) != 1:
        raise SystemExit("用法：python scripts/publish_daily.py YYYY-MM-DD [--dry-run]")
    run_date = args[0]

    items = parse("data/daily/%s.md" % run_date)
    records, dropped = build(items, run_date)
    if not records:
        print("今日无条目，%s 未更改。" % OUT)
        return
    check(records)

    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)
    replaced = sum(1 for e in data if e.get("date") == run_date)
    data = [e for e in data if e.get("date") != run_date]
    data.insert(0, {"date": run_date, "items": records})
    data.sort(key=lambda e: e["date"], reverse=True)

    if not dry_run:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        json.load(open(OUT, encoding="utf-8"))  # 步骤 6.5：写完立刻验证

    ratings = {r: sum(1 for x in records if x["rating"] == r) for r in (3, 2, 1)}
    print("%s%d 条已写入（⭐⭐⭐ %d / ⭐⭐ %d / ⭐ %d），覆盖旧记录 %d 条" % (
        "[dry-run] " if dry_run else "", len(records), ratings[3], ratings[2], ratings[1], replaced))
    print("分区：国内 %d / 国外 %d" % (
        sum(1 for r in records if r["group"] == "国内"), sum(1 for r in records if r["group"] == "国外")))
    if dropped:
        print("%d 条因日期不在窗口内被过滤：" % len(dropped))
        for title, why in dropped:
            print("  -", title[:40], "→", why)
    for r in records:
        print("  %s | %s/%s | %s(%s) | r%d | %s" % (
            r["id"], r["group"], r["sub_group"], r["company"], r["company_slug"], r["rating"], r["title"][:40]))


if __name__ == "__main__":
    main()
