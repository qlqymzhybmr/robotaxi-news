"""Build structured data for weekly report generation."""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/data/daily.json', encoding='utf-8') as f:
    daily = json.load(f)

with open('docs/data/selections.json', encoding='utf-8') as f:
    sel = json.load(f)

# build index by item ID
idx = {}
for day in daily:
    for item in (day.get('items') or []):
        idx[item['id']] = item

# collect selected IDs for W20: 2026-05-12 ~ 2026-05-18
week_start = '2026-05-12'
week_end   = '2026-05-18'

selected = []
for date in sorted(sel.keys()):
    if week_start <= date <= week_end:
        for sid in sel[date]:
            item = idx.get(sid)
            if item:
                # strip html for text
                summary_text = re.sub(r'<[^>]+>', '', item.get('summary_html', ''))
                selected.append({
                    'id': sid,
                    'fetch_date': sid[:10],
                    'pub_date': item.get('date', ''),
                    'group': item.get('group', ''),
                    'sub_group': item.get('sub_group', ''),
                    'company': item.get('company', ''),
                    'title': item.get('title', ''),
                    'rating': item.get('rating', 0),
                    'summary': summary_text.strip(),
                    'source_name': item.get('source_name', ''),
                    'source_url': item.get('source_url', ''),
                })
            else:
                selected.append({'id': sid, 'ERROR': 'not found in daily.json'})

with open('data/tmp/weekly_w20_data.json', 'w', encoding='utf-8') as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

print(f'Wrote {len(selected)} items to data/tmp/weekly_w20_data.json')
for item in selected:
    g = item.get('group','')
    c = item.get('company','')
    r = item.get('rating','')
    t = item.get('title','')[:60]
    print(f'  [{item["id"]}] [{r}★] [{g}] {c} | {t}')
