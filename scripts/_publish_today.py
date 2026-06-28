# -*- coding: utf-8 -*-
# Publish 2026-06-23 to docs/data/daily.json
import json, re

TODAY = "2026-06-28"
JSON_PATH = "docs/data/daily.json"
ITEMS_PATH = "data/tmp/items_2026-06-28.json"

with open(ITEMS_PATH, encoding="utf-8") as f:
    raw = json.load(f)
items = raw["items"] if isinstance(raw, dict) else raw

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

removed = sum(1 for e in data if e.get("date") == TODAY)
data = [e for e in data if e.get("date") != TODAY]
data.insert(0, {"date": TODAY, "items": items})

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

r3 = sum(1 for i in items if i["rating"] == 3)
r2 = sum(1 for i in items if i["rating"] == 2)
r1 = sum(1 for i in items if i["rating"] == 1)
print("removed=%d total=%d today=%d ratings=%dx3/%dx2/%dx1" % (removed, len(data), len(items), r3, r2, r1))
