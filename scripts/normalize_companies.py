# -*- coding: utf-8 -*-
"""Migration: collapse the company name and company_slug variants in the stored JSON.

Usage:
    python scripts/normalize_companies.py            # dry run, prints what would change
    python scripts/normalize_companies.py --apply    # rewrite the JSON files

Background: before scripts/publish_daily.py was committed, each run re-invented both
fields, so 理想 appeared as 理想 / 理想汽车 / 理想 (Li Auto) with slugs liauto / lixiang /
li-auto / li_auto, and headlines sometimes landed in the company field
("Tesla Cybercab 路线规划翻车"). The website builds its company filter from `company`,
so those variants each took their own row in the dropdown.

`company` is rewritten through docs/data/company_aliases.json; `company_slug` is then
re-derived from the canonical name where that name is known, and otherwise put through
the slug alias table below. No other field is touched - the script asserts that.
"""
import glob
import json
import sys
from collections import Counter, defaultdict

ALIASES = "docs/data/company_aliases.json"

FILES = ["docs/data/daily.json", "docs/data/daily-archive.json",
         "docs/data/weekly.json", "docs/data/weekly_overrides.json"] + sorted(glob.glob("data/reports/*.json"))

# Exact company name -> slug. Wins over everything else; used where one slug is shared by
# several real companies (huawei, waymo, ...) so a slug-only rule would be wrong.
NAME_EXACT = {
    "Reddit/Waymo": "reddit-waymo",
    "Reddit/SelfDrivingCars": "reddit-selfdriving",
    "UNECE": "unece",
    "华为 (Huawei)": "huawei",
    "极狐": "arcfox",
    "引望智能": "yinwang",
    "引望智能 (华为)": "yinwang",
    "Uber / Wayve": "uber-wayve",
    "Uber / WeRide": "uber-weride",
    "一汽奥迪": "faw-audi",
    "L3政策": "policy",
    # 跨公司主题条目：主语是比亚迪的智驾兜底，萝卜快跑只是同条里的另一半，保持 byd
    "比亚迪 / 萝卜快跑": "byd",
    # 埃安 N60 联合文远知行，按自动驾驶提供方归到 weride
    "埃安 / 文远知行": "weride",
    "埃安 (广汽) / 文远知行": "weride",
}

# Substring in the company name -> slug. Checked in order, after NAME_EXACT.
NAME_CONTAINS = [
    ("鸿蒙智行", "harmonyos-auto"),
    ("萝卜快跑", "apollo"),
]

# Plain slug aliases, applied when no name rule matched.
SLUG_ALIAS = {
    "aurora-innovation": "aurora",
    "horizonrobotics": "horizon",
    "horizon-robotics": "horizon",
    "horizon_robotics": "horizon",
    "xiaomi_auto": "xiaomi",
    "xiaomi-auto": "xiaomi",
    "ponyai": "xiaoma",
    "pony": "xiaoma",
    "pony-ai": "xiaoma",
    "pony_ai": "xiaoma",
    "voyah": "lantu",
    "landu": "lantu",
    "wenyuan": "weride",
    "luobo": "apollo",
    "apollogo": "apollo",
    "apollo-go": "apollo",
    "luobo-kuaipao": "apollo",
    "lixiang": "liauto",
    "li-auto": "liauto",
    "li_auto": "liauto",
    "caocao-chuxing": "caocao",
    "qcraft": "qingzhou",
    "great_wall": "gwm",
    "yushikeji": "uisee",
    "yushi-tech": "uisee",
    "驭势科技": "uisee",
    "xingdao": "xiangdao",
    "faw_audi": "faw-audi",
    "aito": "harmonyos-auto",
    "harmonyos-smart": "harmonyos-auto",
    "harmonyos-intelligent": "harmonyos-auto",
    "huawei_hm": "harmonyos-auto",
    "hmzx": "harmonyos-auto",
    "l3-policy": "policy",
}


_alias_doc = json.load(open(ALIASES, encoding="utf-8"))
NAME_ALIAS = _alias_doc["alias"]
NAME_TO_SLUG = _alias_doc["name_to_slug"]


def canonical_name(name):
    return NAME_ALIAS.get(name, name)


def canonical(name, slug):
    """Slug for an item, given its ALREADY canonical company name."""
    if name in NAME_TO_SLUG:          # the name the publisher knows -> its slug
        return NAME_TO_SLUG[name]
    if name in NAME_EXACT:
        return NAME_EXACT[name]
    for needle, target in NAME_CONTAINS:
        if needle in (name or ""):
            return target
    return SLUG_ALIAS.get(slug, slug)


def walk(node, changes):
    """Rewrite company_slug in place, recording (name, old, new) for the report."""
    if isinstance(node, dict):
        if "company_slug" in node:
            raw_name, old = node.get("company", ""), node["company_slug"]
            name = canonical_name(raw_name)
            if name != raw_name:
                node["company"] = name
                changes.append(("name", raw_name, name))
            new = canonical(name, old)
            if new != old:
                node["company_slug"] = new
                changes.append(("slug", old, new))
        for v in node.values():
            walk(v, changes)
    elif isinstance(node, list):
        for v in node:
            walk(v, changes)


def strip_parens(name):
    """Same normalization the website applies when building the company filter."""
    out, depth = [], 0
    for ch in name or "":
        if ch in "(（":
            depth += 1
        elif ch in ")）":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return " ".join("".join(out).split())


def families(data):
    """normalized company name -> Counter of slugs, to spot leftovers."""
    fam = defaultdict(Counter)

    def rec(node):
        if isinstance(node, dict):
            if "company_slug" in node:
                fam[node.get("company", "")][node["company_slug"]] += 1
            for v in node.values():
                rec(v)
        elif isinstance(node, list):
            for v in node:
                rec(v)

    rec(data)
    return fam


def main():
    apply = "--apply" in sys.argv
    total_changes, before_all, after_all = 0, defaultdict(Counter), defaultdict(Counter)

    for path in FILES:
        raw = open(path, encoding="utf-8").read()
        data = json.loads(raw)
        skeleton_before = json.dumps(data, ensure_ascii=False, sort_keys=True).replace('"company_slug"', '"__s__"')

        for fam, counts in families(data).items():
            before_all[fam].update(counts)

        changes = []
        walk(data, changes)
        total_changes += len(changes)

        for fam, counts in families(data).items():
            after_all[fam].update(counts)

        # only company / company_slug values may differ
        skeleton_after = json.dumps(data, ensure_ascii=False, sort_keys=True).replace('"company_slug"', '"__s__"')
        assert len(skeleton_before) - len(skeleton_after) == sum(
            len(o) - len(n) for _, o, n in changes), ("除公司字段外还有内容被改动：%s" % path)

        if changes:
            n_name = sum(1 for kind, _, _ in changes if kind == "name")
            print("%s：公司名 %d 处 / slug %d 处" % (path, n_name, len(changes) - n_name))
        if apply and changes:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            json.load(open(path, encoding="utf-8"))  # 写完立即验证

    print("\n合计 %d 处 %s" % (total_changes, "已写入" if apply else "（dry-run，未写盘）"))

    fixed = sum(1 for fam in before_all if len(before_all[fam]) > 1 and len(after_all[fam]) == 1)
    left = {fam: dict(c) for fam, c in after_all.items() if len(c) > 1}
    print("公司（按网页口径归一后）共 %d 个；本次消除一名多 slug %d 个" % (len(after_all), fixed))
    if left:
        print("仍存在一名多 slug（需人工判断）：")
        for fam, c in sorted(left.items()):
            print("    %-24s %s" % (fam, c))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
