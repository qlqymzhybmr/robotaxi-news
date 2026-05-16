#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 3: 把 daily markdown 全量写入 docs/data/daily.json"""

import json
import re
from datetime import date

DAILY_MD = 'data/daily/2026-05-16.md'
DAILY_JSON = 'docs/data/daily.json'
TODAY = '2026-05-16'
TODAY_DATE = date(2026, 5, 16)
MAX_DAYS_DIFF = 2

SLUG_MAP = {
    'Waymo': 'waymo', 'Tesla': 'tesla', 'Zoox': 'zoox', 'Wayve': 'wayve',
    'Cruise': 'cruise', 'Uber': 'uber', 'Lyft': 'lyft', 'Grab': 'grab',
    'Rivian': 'rivian', 'Lucid': 'lucid', 'NVIDIA': 'nvidia',
    'Woven Planet': 'woven-planet', 'Motional': 'motional', '42dot': '42dot',
    'MOIA': 'moia', 'Aurora Innovation': 'aurora', 'Aurora': 'aurora',
    'May Mobility': 'may-mobility', 'SWM': 'swm', 'Sonnet.ai': 'sonnetai',
    'Nuro': 'nuro', 'Waabi': 'waabi', 'Tensor': 'tensor',
    '小马智行': 'xiaoma', '文远知行': 'wenyuan', '萝卜快跑': 'luobo',
    '曹操出行': 'caocao', '哈啰出行': 'hello', '高德地图': 'amap',
    '如祺出行': 'ruqi', '享道出行': 'xiangdao', '蔚来': 'nio',
    '理想': 'liauto', '小鹏': 'xpeng', '小米': 'xiaomi', '零跑': 'leapmotor',
    '赛力斯': 'seres', '极氪': 'zeekr', '岚图': 'lantu', '极狐': 'arcfox',
    '智己': 'zhiji', '埃安': 'aion', '比亚迪': 'byd', '长安': 'changan',
    '一汽': 'faw', '长城': 'gwm', '奇瑞': 'chery', 'Momenta': 'momenta',
    '地平线': 'horizon', '轻舟智航': 'qingzhou', '元戎启行': 'deeproute',
    '千里科技': 'qianli', '毫末智行': 'haomo', '大卓智能': 'dazuo',
    '卓驭科技': 'zhuoyu', '鸿蒙智行': 'hongmeng', '引望智能': 'yinwang',
    '商汤绝影': 'sensetime', 'GM': 'gm', 'Valeo': 'valeo',
    'Reddit': 'reddit-selfdriving',
}

def get_slug(company):
    for key, slug in SLUG_MAP.items():
        if key in company:
            return slug
    return re.sub(r'[^a-z0-9-]', '', company.lower().replace(' ', '-'))

def get_group(heading):
    return '国内' if '国内' in heading else '国外'

def get_sub_group(heading):
    mapping = {
        '国外 L4': '国外 L4',
        '国外出行平台': '国外出行平台',
        '国外 OEM': '国外 OEM / Tier1',
        '社区热帖': '社区热帖',
        '国内 L4': '国内 L4',
        '国内出行平台': '国内出行平台',
        '国内新势力': '国内新势力 / 传统 OEM',
        '国内智驾方案商': '国内智驾方案商',
        '国内华为系': '国内华为系 / 互联网大厂',
    }
    for key, val in mapping.items():
        if key in heading:
            return val
    return heading

def clean_company(heading):
    m = re.match(r'^(.+?)\s*[\(（]', heading)
    return m.group(1).strip() if m else heading.strip()

def parse_rating(line):
    return line.count('⭐')

def parse_original_date(body):
    m = re.search(r'原始发布日期\*\*[：:]\s*(\d{4}-\d{2}-\d{2})', body)
    return m.group(1) if m else ''

def check_date(ds):
    if not ds:
        return False
    try:
        d = date.fromisoformat(ds)
        return abs((TODAY_DATE - d).days) <= MAX_DAYS_DIFF
    except Exception:
        return False

def parse_source(body):
    m = re.search(r'权威源[：:]\s*\[([^\]]+)\]\(([^)]+)\)', body)
    if m:
        name = re.sub(r'\s+\d{4}-\d{2}-\d{2}', '', m.group(1)).strip()
        return name, m.group(2).strip()
    return '', ''

def build_summary_html(body_lines):
    filtered = []
    for line in body_lines:
        s = line.strip()
        if re.match(r'^-\s+\*\*原始发布日期\*\*', s):
            continue
        if re.match(r'^-\s+(权威源|辅助源)[：:]', s):
            continue
        if s.startswith('候选图:'):
            continue
        filtered.append(line)

    text = '\n'.join(filtered).strip()
    if not text:
        return ''

    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    paragraphs = re.split(r'\n\s*\n', text)
    parts = []
    for p in paragraphs:
        lines_p = [l.strip() for l in p.strip().split('\n') if l.strip()]
        if lines_p:
            parts.append(f'<p>{" ".join(lines_p)}</p>')
    return ''.join(parts)

# ── parse markdown ──────────────────────────────────────────────────────────────
with open(DAILY_MD, 'r', encoding='utf-8') as f:
    md_lines = f.read().split('\n')

items = []
filtered_count = 0
item_counter = 0
current_sub_group_heading = ''
current_company = ''
in_item = False
item_lines = []

def finalize(i_lines, company, sg_heading):
    global item_counter, filtered_count
    if not i_lines:
        return
    first = i_lines[0]
    rating = parse_rating(first)
    if rating == 0:
        return
    body = '\n'.join(i_lines[1:])
    orig_date = parse_original_date(body)
    if not check_date(orig_date):
        filtered_count += 1
        print(f'  [SKIP] date={orig_date!r} — {first[:60]}')
        return
    # title: text after Company： inside **...**
    m = re.search(r'\*\*[^*：:]+[：:]\s*(.*?)\*\*\s*$', first)
    title = m.group(1).strip() if m else ''
    src_name, src_url = parse_source(body)
    summary = build_summary_html(i_lines[1:])
    item_counter += 1
    company_clean = clean_company(company)
    items.append({
        'id': f'{TODAY}-{item_counter:03d}',
        'company': company_clean,
        'company_slug': get_slug(company_clean),
        'rating': rating,
        'group': get_group(sg_heading),
        'sub_group': get_sub_group(sg_heading),
        'title': title,
        'summary_html': summary,
        'source_name': src_name,
        'source_url': src_url,
        'original_date': orig_date,
    })

for line in md_lines:
    if re.match(r'^## ', line):
        if in_item and item_lines:
            finalize(item_lines, current_company, current_sub_group_heading)
            item_lines = []; in_item = False
        heading = line[3:].strip()
        current_sub_group_heading = '' if (heading.startswith('⚠️') or heading.startswith('📊')) else heading
        continue

    if re.match(r'^### ', line):
        if in_item and item_lines:
            finalize(item_lines, current_company, current_sub_group_heading)
            item_lines = []; in_item = False
        current_company = line[4:].strip()
        continue

    if line.strip() == '---':
        if in_item and item_lines:
            finalize(item_lines, current_company, current_sub_group_heading)
            item_lines = []; in_item = False
        continue

    if re.match(r'^- \[[ x]\] [⭐]', line):
        if in_item and item_lines:
            finalize(item_lines, current_company, current_sub_group_heading)
            item_lines = []
        in_item = True
        item_lines = [line]
        continue

    if in_item:
        item_lines.append(line)

if in_item and item_lines:
    finalize(item_lines, current_company, current_sub_group_heading)

r3 = sum(1 for i in items if i['rating'] == 3)
r2 = sum(1 for i in items if i['rating'] == 2)
r1 = sum(1 for i in items if i['rating'] == 1)
print(f'\n解析完成：{len(items)} 条通过日期检查，{filtered_count} 条被过滤')
print(f'3star={r3} / 2star={r2} / 1star={r1}')

# ── update daily.json ──────────────────────────────────────────────────────────
with open(DAILY_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

data = [e for e in data if e['date'] != TODAY]
data.insert(0, {'date': TODAY, 'items': items})

with open(DAILY_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n✅ docs/data/daily.json 已更新，今日 {len(items)} 条全量写入。')
