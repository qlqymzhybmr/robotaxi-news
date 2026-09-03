"""追踪德州 DMV 登记的自动驾驶车队规模（12 家运营方）。

德州要求自动驾驶运营方在 TxMCCS 逐辆登记车辆，页面会列出每辆车的 VIN / 年份 /
车型。这是**唯一公开、逐车、官方**的各家车队规模数据源——媒体极少报道车队数量
变化，但它是判断扩张节奏最直接的指标（比如某车型首次出现、或某天一次性新增几十辆），
而且**可以横向对比各家**。

页面是 JS 渲染的，但底层 API 无需认证且一次返回全部车辆，所以直接打 API：
    https://txmccs.txdmv.gov/api/TruckStop/companies/<id>/automated-motor-vehicles

存储策略：完整 VIN 集合只保留最新一份用于比对，历史里只记数量与当日新增/移除的
VIN，避免文件随天数线性膨胀。

用法：
    python scripts/track_tx_av_registrations.py            # 每日：抓取、比对、写入
    python scripts/track_tx_av_registrations.py --no-save  # 只看，不写
    python scripts/track_tx_av_registrations.py --discover # 每季度：普查有无新运营方
"""
import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN_TZ = timezone(timedelta(hours=8))
STORE = Path("data/tx_av_registrations.json")
API = "https://txmccs.txdmv.gov/api/TruckStop/companies/{cid}/automated-motor-vehicles"

# 2026-09-03 全量普查结果：用 searchType=company_name 搜遍已知 AV 玩家，
# 再逐个打 automated-motor-vehicles 端点，筛出真正有车辆登记的实体。
# 非 AV 公司该端点返回空数组（不是 404），所以判据是「车辆数 > 0」。
#
# 想加新公司：
#   curl 'https://txmccs.txdmv.gov/api/TruckStop/companies?searchValue=<名字>&searchType=company_name'
# 取 businessEntityId 填进来即可。
COMPANIES = {
    "Waymo":            "07ebbc43-ae5b-42ca-a712-d9d5ce5b3516",
    "Tesla Robotaxi":   "81edcff1-8a6e-4ed0-be1f-60668515e223",
    "Avride":           "fd52bbf8-a94f-409e-a821-28dacd4d8bdd",
    "Aurora":           "e2ec8d3a-51c0-47fd-8172-49b1ca545ad3",
    "Gatik AI":         "c7252bd3-9b9a-4dfe-98e2-db205010f93c",
    "Nuro":             "a073be41-e321-4074-9515-01279a9f36d7",
    "Zoox":             "b5672c35-0996-4364-8ac7-080ea0333d2c",
    "Kodiak Robotics":  "51e635a0-1649-419d-86b4-76a3107e3240",
    "Torc Robotics":    "fcf5ffd0-e90d-4aa6-9afa-6c002c2cf511",
    "May Mobility":     "2fb8d9e8-5add-4c1e-b746-58494b3661d8",
    "Waabi Logistics":  "43448d49-5ea9-4769-afcb-ffc5ca3f3cbb",
    "Bot Auto TX":      "a984e056-d778-416b-af45-03188239089c",
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SEARCH = "https://txmccs.txdmv.gov/api/TruckStop/companies"

# --discover 用的检索词。新公司拿到 AV 授权不会有任何通知，只能靠定期普查发现。
# 覆盖已知玩家 + 通用词（robotics / autonomous / driverless 等）以捞出没听过的。
DISCOVERY_TERMS = [
    "waymo", "zoox", "avride", "nuro", "aurora", "motional", "cruise",
    "may mobility", "kodiak", "gatik", "torc", "waabi", "einride", "plus",
    "tesla", "uber", "lyft", "pony", "weride", "apollo", "bot auto",
    "stack av", "applied intuition", "wayve", "pronto", "outrider",
    "robotics", "autonomous", "driverless", "self-driving", "robotaxi",
]


def fetch(company_id: str) -> list[dict]:
    req = urllib.request.Request(
        API.format(cid=company_id),
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30,
                                context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode("utf-8")).get("vehicles", [])


def discover() -> int:
    """普查德州所有登记了自动驾驶车辆的运营方，报出 COMPANIES 里还没有的。

    两个接口上的坑（踩过，别再踩）：
      1. 搜索**必须同时带 searchType**，只给 searchValue 会一律返回 0 条，
         连确实存在的公司也查不到，看起来像「德州没有这家」。
      2. 车辆端点对非 AV 公司返回**空数组而不是 404**，所以判据只能是
         「车辆数 > 0」，不能靠 HTTP 状态码。
    """
    import time
    import urllib.parse

    known_ids = set(COMPANIES.values())
    seen: set[str] = set()
    new_hits: list[tuple[str, str, int, dict]] = []

    print(f"普查 {len(DISCOVERY_TERMS)} 个检索词…\n")
    for term in DISCOVERY_TERMS:
        url = (f"{SEARCH}?searchValue={urllib.parse.quote(term)}"
               f"&searchType=company_name")
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=25,
                                        context=ssl.create_default_context()) as r:
                results = json.loads(r.read().decode("utf-8")).get("results", [])
        except Exception as exc:
            print(f"  ! 检索「{term}」失败：{type(exc).__name__}")
            continue

        for c in results:
            bid, nm = c.get("businessEntityId"), c.get("companyName", "")
            if not bid or bid in seen:
                continue
            seen.add(bid)
            try:
                vs = fetch(bid)
            except Exception:
                continue
            if vs and bid not in known_ids:
                by = dict(Counter(v.get("model", "?") for v in vs))
                new_hits.append((nm, bid, len(vs), by))
                print(f"  🆕 {nm[:50]:52} {len(vs):>5} 辆  {by}")
            time.sleep(0.1)
        time.sleep(0.15)

    print()
    print("=" * 66)
    print(f"扫描 {len(seen)} 家公司；已在追踪 {len(COMPANIES)} 家；"
          f"**新发现 {len(new_hits)} 家**")
    print("=" * 66)
    if not new_hits:
        print("  没有新运营方，COMPANIES 无需改动。")
        return 0
    print("\n把下面几行加进脚本顶部的 COMPANIES 即可开始追踪：\n")
    for nm, bid, n, _ in sorted(new_hits, key=lambda x: -x[2]):
        short = nm.split(",")[0].strip()[:18]
        print(f'    "{short}":{" " * max(1, 18 - len(short))}"{bid}",   # {n} 辆')
    return 0


def load_store() -> dict:
    if not STORE.exists():
        return {
            "_comment": "德州 DMV 自动驾驶车辆登记追踪。latest 保存最新完整 VIN 集合用于比对；"
                        "history 只记数量与当日增减，避免文件膨胀。由 "
                        "scripts/track_tx_av_registrations.py 维护。",
            "companies": {},
        }
    return json.loads(STORE.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="追踪德州 DMV 自动驾驶车辆登记数")
    ap.add_argument("--no-save", action="store_true", help="只显示，不写入")
    ap.add_argument("--discover", action="store_true",
                    help="普查有无新的 AV 运营方（约每季度跑一次）")
    ap.add_argument("--date", default=datetime.now(CN_TZ).strftime("%Y-%m-%d"))
    args = ap.parse_args()

    if args.discover:
        return discover()

    store = load_store()
    summary = []      # (公司, 总数, 净变化 or None) 供末尾汇总
    failures = []

    for name, cid in COMPANIES.items():
        try:
            vehicles = fetch(cid)
        except Exception as exc:
            # 抓不到要显式报错，不能静默当成 0 辆——那会被误读成车队清零。
            # 单家失败不应中断其余 11 家，所以记下来继续。
            print(f"❌ {name}: 抓取失败 {type(exc).__name__}: {exc}")
            print("   （该公司本次不写入。抓取失败 ≠ 车队为空）\n")
            failures.append(name)
            continue

        by_model = dict(Counter(v.get("model", "?") for v in vehicles))
        vins = sorted(v["vin"] for v in vehicles if v.get("vin"))
        rec = store["companies"].setdefault(name, {"latest": None, "history": []})
        prev = rec["latest"]

        print("=" * 66)
        print(f"{name}   {args.date}")
        print("=" * 66)
        print(f"  总数 {len(vehicles)}")
        for m, n in sorted(by_model.items(), key=lambda kv: -kv[1]):
            print(f"    {m:14} {n}")

        if prev is None:
            print("\n  （首次抓取，无历史可比对）")
            added_vins, removed_vins = [], []
            delta = {}
        else:
            pv = set(prev["vins"])
            cv = set(vins)
            added_vins, removed_vins = sorted(cv - pv), sorted(pv - cv)
            vin_model = {v["vin"]: v.get("model", "?") for v in vehicles}
            delta = {
                "added_by_model": dict(Counter(vin_model[v] for v in added_vins)),
                "removed_count": len(removed_vins),
            }
            print(f"\n  对比 {prev['date']}（{prev['total']} 辆）：")
            if not added_vins and not removed_vins:
                print("    无变化")
            else:
                if added_vins:
                    for m, n in sorted(delta["added_by_model"].items(), key=lambda kv: -kv[1]):
                        print(f"    +{n} {m}")
                if removed_vins:
                    print(f"    -{len(removed_vins)} 辆（VIN 已从登记中移除）")
                print(f"    净变化 {len(vehicles) - prev['total']:+d}")
                # 车型首次出现值得单独提示
                for m in delta["added_by_model"]:
                    if m not in (prev.get("by_model") or {}):
                        print(f"    ⭐ 新车型首次出现：{m}")

        summary.append((name, len(vehicles),
                        None if prev is None else len(vehicles) - prev["total"],
                        by_model))

        if not args.no_save:
            rec["history"].append({
                "date": args.date, "total": len(vehicles), "by_model": by_model,
                "added_vins": added_vins[:200], "removed_vins": removed_vins[:200],
                **({"delta": delta} if delta else {}),
            })
            rec["latest"] = {"date": args.date, "total": len(vehicles),
                             "by_model": by_model, "vins": vins}

    # 汇总表：按车队规模排序，一眼看清各家体量与当日变化
    print("=" * 66)
    print(f"汇总  {args.date}")
    print("=" * 66)
    print(f"  {'公司':<18}{'总数':>7}  {'较昨日':>8}   车型分布")
    changed = []
    for name, total, delta, by_model in sorted(summary, key=lambda x: -x[1]):
        d = "基线" if delta is None else (f"{delta:+d}" if delta else "—")
        if delta:
            changed.append((name, delta))
        models = " / ".join(f"{m} {n}" for m, n in
                            sorted(by_model.items(), key=lambda kv: -kv[1]))
        print(f"  {name:<18}{total:>7}  {d:>8}   {models}")
    print(f"  {'合计':<18}{sum(s[1] for s in summary):>7}")

    if changed:
        print("\n  ⚠️ 今日有变化：" +
              "，".join(f"{n} {d:+d}" for n, d in changed))
    if failures:
        print(f"\n  ❌ 抓取失败（未写入）：{', '.join(failures)}")

    if not args.no_save:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        STORE.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
        print(f"\n已写入 {STORE}")
    else:
        print("\n（--no-save，未写入）")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
