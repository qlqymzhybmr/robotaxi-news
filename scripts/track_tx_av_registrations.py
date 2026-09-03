"""追踪德州 DMV 登记的自动驾驶车队规模（默认 Tesla Robotaxi, LLC）。

德州要求自动驾驶运营方在 TxMCCS 逐辆登记车辆，页面会列出每辆车的 VIN / 年份 /
车型。这是**唯一公开、逐车、官方**的 Tesla Robotaxi 车队规模数据源——媒体极少
报道车队数量变化，但它是判断扩张节奏最直接的指标（比如 Cybercab 首次出现、
或某天一次性新增几十辆）。

页面是 JS 渲染的，但底层 API 无需认证且一次返回全部车辆，所以直接打 API：
    https://txmccs.txdmv.gov/api/TruckStop/companies/<id>/automated-motor-vehicles

存储策略：完整 VIN 集合只保留最新一份用于比对，历史里只记数量与当日新增/移除的
VIN，避免文件随天数线性膨胀。

用法：
    python scripts/track_tx_av_registrations.py            # 抓取、比对、写入
    python scripts/track_tx_av_registrations.py --no-save  # 只看，不写
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

# 目前只追踪 Tesla；德州还有其他 AV 运营方时按同样格式追加即可
COMPANIES = {
    "Tesla Robotaxi, LLC": "81edcff1-8a6e-4ed0-be1f-60668515e223",
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(company_id: str) -> list[dict]:
    req = urllib.request.Request(
        API.format(cid=company_id),
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30,
                                context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode("utf-8")).get("vehicles", [])


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
    ap.add_argument("--date", default=datetime.now(CN_TZ).strftime("%Y-%m-%d"))
    args = ap.parse_args()

    store = load_store()
    changed_any = False

    for name, cid in COMPANIES.items():
        try:
            vehicles = fetch(cid)
        except Exception as exc:
            # 抓不到要显式报错，不能静默当成 0 辆——那会被误读成车队清零
            print(f"❌ {name}: 抓取失败 {type(exc).__name__}: {exc}")
            print("   （不写入任何数据。抓取失败 ≠ 车队为空）")
            return 1

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

        if added_vins or removed_vins or prev is None:
            changed_any = True

        if not args.no_save:
            rec["history"].append({
                "date": args.date, "total": len(vehicles), "by_model": by_model,
                "added_vins": added_vins[:200], "removed_vins": removed_vins[:200],
                **({"delta": delta} if delta else {}),
            })
            rec["latest"] = {"date": args.date, "total": len(vehicles),
                             "by_model": by_model, "vins": vins}

    if not args.no_save:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        STORE.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
        print(f"\n已写入 {STORE}")
    else:
        print("\n（--no-save，未写入）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
