"""把 daily.json 里的旧日期滚动到 daily-archive.json，让首屏只需加载近期数据。

背景：daily.json 是累积型文件，每天涨约 14KB。到 2026-09-01 已经 141 天 /
1.87MB，gzip 后仍有 667KB，是网页首屏最大的单个负担，且会无限增长。

做法不是丢数据，而是拆成两个文件、网页两个都加载：
    docs/data/daily.json          近 N 天（首屏渲染用，daily-publish 仍然只写这里）
    docs/data/daily-archive.json  更早的全部历史（首屏渲染后台补齐）

安全性：本脚本对「新闻条目总数」做守恒校验，拆分前后总数不一致就中止且不写入
任何文件——daily.json 是 append-only 的累积数据，宁可不拆也不能丢。

用法：
    python scripts/roll_daily_archive.py                # 预览
    python scripts/roll_daily_archive.py --apply        # 实际写入
    python scripts/roll_daily_archive.py --keep-days 60 --apply
"""
import argparse
import json
import sys
from pathlib import Path

RECENT = Path("docs/data/daily.json")
ARCHIVE = Path("docs/data/daily-archive.json")
KEEP_DAYS = 90


def load(path: Path) -> list:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def count_items(entries: list) -> int:
    return sum(len(e.get("items") or []) for e in entries)


def main() -> int:
    ap = argparse.ArgumentParser(description="滚动 daily.json 历史到归档文件")
    ap.add_argument("--apply", action="store_true", help="实际写入（默认只预览）")
    ap.add_argument("--keep-days", type=int, default=KEEP_DAYS,
                    help=f"daily.json 保留最近多少个日期条目（默认 {KEEP_DAYS}）")
    args = ap.parse_args()

    recent, archive = load(RECENT), load(ARCHIVE)

    # 合并后按日期倒序统一重排，这样重复运行是幂等的
    by_date = {}
    for entry in archive + recent:          # recent 后放，同日期以 recent 为准
        if isinstance(entry, dict) and entry.get("date"):
            by_date[entry["date"]] = entry
    merged = sorted(by_date.values(), key=lambda e: e["date"], reverse=True)

    total_before = count_items(recent) + count_items(
        [e for e in archive if e.get("date") not in {r.get("date") for r in recent}])
    new_recent, new_archive = merged[:args.keep_days], merged[args.keep_days:]

    # 守恒校验：绝不允许在拆分过程中丢掉任何一条新闻
    total_after = count_items(new_recent) + count_items(new_archive)
    if total_after != total_before:
        print(f"中止：条目总数不一致（拆分前 {total_before}，拆分后 {total_after}），未写入。")
        return 1
    if len(by_date) != len(new_recent) + len(new_archive):
        print("中止：日期条目数不一致，未写入。")
        return 1

    print(f"合计 {len(merged)} 天 / {total_after} 条新闻")
    print(f"  daily.json          保留最近 {len(new_recent):>3} 天"
          f"（{new_recent[-1]['date'] if new_recent else '-'} ~ "
          f"{new_recent[0]['date'] if new_recent else '-'}）")
    print(f"  daily-archive.json  归档     {len(new_archive):>3} 天"
          f"（{new_archive[-1]['date'] if new_archive else '-'} ~ "
          f"{new_archive[0]['date'] if new_archive else '-'}）")

    r_txt = json.dumps(new_recent, ensure_ascii=False, indent=2)
    a_txt = json.dumps(new_archive, ensure_ascii=False, indent=2)
    print(f"\n体积：daily.json {len(r_txt.encode())/1024:.0f}KB，"
          f"daily-archive.json {len(a_txt.encode())/1024:.0f}KB")

    if not args.apply:
        print("\n预览模式，未写入。加 --apply 实际生效。")
        return 0

    RECENT.write_text(r_txt, encoding="utf-8")
    ARCHIVE.write_text(a_txt, encoding="utf-8")
    print(f"\n已写入 {RECENT} 和 {ARCHIVE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
