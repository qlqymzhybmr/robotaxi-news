"""Phase 3: parse today's daily markdown and write to docs/data/daily.json."""
import json, re, sys
from pathlib import Path

TODAY = '2026-05-18'
DAILY_MD = Path('data/daily/2026-05-18.md')
DAILY_JSON = Path('docs/data/daily.json')

# ── slug mapping ──────────────────────────────────────────────────────────────
SLUG_MAP = {
    'Waymo': 'waymo', 'Tesla': 'tesla', 'Wayve': 'wayve', 'Cruise': 'cruise',
    'Zoox': 'zoox', 'Aurora Innovation': 'aurora', 'May Mobility': 'may-mobility',
    'Motional': 'motional', 'Nuro': 'nuro', 'Uber': 'uber', 'Lyft': 'lyft',
    'NVIDIA': 'nvidia', '文远知行': 'wenyuan', '文远知行 (WeRide)': 'wenyuan',
    '小马智行': 'xiaoma', '萝卜快跑': 'luobo', '享道出行': 'xiangdao',
    '曹操出行': 'caocao', '哈啰出行': 'hello', '如祺出行': 'ruqi',
    '高德地图': 'amap', '理想 (Li Auto)': 'liauto', '理想': 'liauto',
    '小鹏 (XPeng)': 'xpeng', '小鹏': 'xpeng', '比亚迪 (BYD)': 'byd', '比亚迪': 'byd',
    '小米 (Xiaomi)': 'xiaomi', '小米': 'xiaomi', '长安': 'changan',
    '蔚来': 'nio', '零跑': 'leapmotor', '极氪': 'zeekr', '极狐': 'arcfox',
    '智己': 'zhiji', '岚图': 'lantu', '奇瑞': 'chery', '一汽': 'faw',
    '长城': 'gwm', '赛力斯': 'seres', '埃安': 'aion',
    'Momenta': 'momenta', '地平线': 'horizon', '卓驭科技': 'zhuoyu',
    '元戎启行': 'deeproute', '毫末智行': 'haomo', '鸿蒙智行 / 华为': 'hongmeng',
    '鸿蒙智行': 'hongmeng', '引望智能': 'yinwang', '商汤绝影': 'sensetime',
    'Reddit/Waymo': 'reddit-waymo', 'Reddit/SelfDrivingCars': 'reddit-selfdriving',
}

def get_slug(company):
    if company in SLUG_MAP:
        return SLUG_MAP[company]
    return re.sub(r'[^a-z0-9-]', '', company.lower().replace(' ', '-')) or 'unknown'

# ── parse markdown ─────────────────────────────────────────────────────────────
content = DAILY_MD.read_text(encoding='utf-8')
lines = content.split('\n')

items = []
current_group = None
current_subgroup = None
current_company = None
current_item = None
body_lines = []
item_seq = 0

def md_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text

def flush():
    global current_item, body_lines, item_seq
    if not current_item:
        return

    body = '\n'.join(body_lines).strip()

    # extract pub date
    dm = re.search(r'\*\*原始发布日期\*\*[：:]\s*(\d{4}-\d{2}-\d{2})', body)
    pub_date = dm.group(1) if dm else ''

    # date filter: must be within 2 days of TODAY
    if pub_date:
        from datetime import datetime
        d = datetime.strptime(pub_date, '%Y-%m-%d').date()
        t = datetime.strptime(TODAY, '%Y-%m-%d').date()
        if abs((t - d).days) > 2:
            current_item = None
            body_lines = []
            return
    else:
        current_item = None
        body_lines = []
        return

    # extract source
    sm = re.search(r'权威源:\s*\[([^\]]+)\]\(([^)]+)\)', body)
    source_name = ''
    source_url = ''
    if sm:
        source_name = re.sub(r'\s+\d{4}-\d{2}-\d{2}$', '', sm.group(1)).strip()
        source_url = sm.group(2)

    # build summary_html
    html_parts = []
    for ln in body_lines:
        s = ln.strip()
        if not s:
            continue
        if re.match(r'- \*\*原始发布日期\*\*', s):
            continue
        if re.match(r'- 权威源', s):
            continue
        if re.match(r'- 辅助源', s):
            continue
        html_parts.append('<p>' + md_to_html(s) + '</p>')

    summary_html = '\n'.join(html_parts)

    item_seq += 1
    items.append({
        'id': f'{TODAY}-{item_seq:03d}',
        'date': pub_date,
        'company': current_item['company'],
        'company_slug': get_slug(current_item['company']),
        'group': current_item['group'],
        'sub_group': current_item['sub_group'],
        'title': current_item['title'],
        'rating': current_item['rating'],
        'summary_html': summary_html,
        'source_name': source_name,
        'source_url': source_url,
    })
    current_item = None
    body_lines = []

for line in lines:
    # section headers
    if line.startswith('## '):
        flush()
        sec = line[3:].strip()
        if '国外 L4' in sec:
            current_group, current_subgroup = '国外', '国外 L4'
        elif '国外出行平台' in sec:
            current_group, current_subgroup = '国外', '国外出行平台'
        elif '国外 OEM' in sec or 'Tier1' in sec:
            current_group, current_subgroup = '国外', '国外 OEM / Tier1'
        elif '社区热帖' in sec:
            current_group, current_subgroup = '国外', '社区热帖'
        elif '国内 L4' in sec:
            current_group, current_subgroup = '国内', '国内 L4'
        elif '国内出行平台' in sec:
            current_group, current_subgroup = '国内', '国内出行平台'
        elif '国内新势力' in sec or '传统 OEM' in sec:
            current_group, current_subgroup = '国内', '国内新势力 / 传统 OEM'
        elif '国内智驾' in sec:
            current_group, current_subgroup = '国内', '国内智驾方案商'
        elif '华为系' in sec or '互联网' in sec:
            current_group, current_subgroup = '国内', '国内华为系 / 互联网大厂'
        elif '统计' in sec or '失败' in sec or '抓取' in sec:
            current_group = None

    # company headers
    elif line.startswith('### '):
        flush()
        current_company = line[4:].strip()

    # news item lines
    elif re.match(r'- \[[ xX]\] ⭐', line):
        flush()
        rating = 3 if '⭐⭐⭐' in line else (2 if '⭐⭐' in line else 1)
        tm = re.search(r'\*\*(.+?)\*\*', line)
        title_raw = tm.group(1) if tm else line
        # strip "CompanyName：date，" prefix
        title = re.sub(r'^[^：:]+[：:]\s*', '', title_raw, count=1)
        current_item = {
            'company': current_company or '',
            'group': current_group or '',
            'sub_group': current_subgroup or '',
            'title': title,
            'rating': rating,
        }
        body_lines = []

    # body / detail lines
    elif current_item is not None:
        if line.startswith('  ') or line.startswith('\t'):
            body_lines.append(line.strip())
        elif line.strip() == '':
            body_lines.append('')

flush()

print(f'Parsed {len(items)} items from {DAILY_MD}')
for it in items:
    print(f'  {it["id"]} [{it["rating"]}★] [{it["group"]}] {it["company"]} | {it["title"][:50]}')

# ── load existing daily.json ───────────────────────────────────────────────────
if DAILY_JSON.exists():
    with open(DAILY_JSON, encoding='utf-8') as f:
        data = json.load(f)
else:
    data = []

# remove today's entry if exists, then insert at front
data = [e for e in data if e.get('date') != TODAY]
new_entry = {'date': TODAY, 'items': items}
data.insert(0, new_entry)

# ── write back ────────────────────────────────────────────────────────────────
with open(DAILY_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Written {len(items)} items to {DAILY_JSON}')

# ── validate ──────────────────────────────────────────────────────────────────
with open(DAILY_JSON, encoding='utf-8') as f:
    json.load(f)
print('JSON OK')
