import os
import requests
from datetime import datetime
import urllib.parse
import feedparser
import time
import re
import base64
from google import genai

# ================= 配置区 =================
APP_ID = os.environ.get("FEISHU_APP_ID")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET")
DOCUMENT_ID = os.environ.get("FEISHU_DOCUMENT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ==========================================

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
        return res.json().get("tenant_access_token")
    except: return None

def extract_companies_from_feishu(token):
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{DOCUMENT_ID}/blocks"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        blocks = res.json().get("data", {}).get("items", [])
    except: return []
    
    companies = []
    type_keys = {2: "text", 3: "heading1", 4: "heading2", 5: "heading3", 11: "bullet", 12: "ordered"}
    for block in blocks:
        if block.get("block_type") == 22: break
        bt = block.get("block_type")
        if bt in type_keys:
            elements = block.get(type_keys[bt], {}).get("elements", [])
            content = "".join([el["text_run"]["content"] for el in elements if "text_run" in el]).strip()
            if content and "清单" not in content:
                parts = re.split(r'[、，\s;；|,|\t|\n|\|]+', content)
                for p in parts:
                    clean_p = p.strip()
                    if len(clean_p) >= 2 and re.search(r'[\u4e00-\u9fa5a-zA-Z0-9]', clean_p):
                        companies.append(clean_p)
    return list(set(companies))

def fetch_raw_news_dict(companies):
    yesterday = datetime.now().timestamp() - 24 * 3600
    news_dict = {}
    total_found = 0
    search_configs = [
        {"name": "中文版", "lang": "zh-CN", "geo": "CN", "ceid": "CN:zh-Hans", "keywords": "自动驾驶 OR 无人驾驶 OR 智驾 OR Robotaxi"},
        {"name": "英文版", "lang": "en-US", "geo": "US", "ceid": "US:en", "keywords": "autonomous driving OR self-driving OR Robotaxi OR FSD"}
    ]
    for config in search_configs:
        for company in companies:
            query = urllib.parse.quote(f'"{company}" ({config["keywords"]})')
            url = f"https://news.google.com/rss/search?q={query}&hl={config['lang']}&gl={config['geo']}&ceid={config['ceid']}"
            try:
                feed = feedparser.parse(url)
                count = 0
                for entry in feed.entries:
                    if entry.published_parsed and time.mktime(entry.published_parsed) > yesterday:
                        if company not in news_dict: news_dict[company] = []
                        source = entry.get('source', {}).get('title', 'Global Source')
                        news_dict[company].append(f"来源：{source} | 标题：{entry.title} | 链接：{entry.link}")
                        count += 1
                        total_found += 1
                        if count >= 3: break
            except: pass
            time.sleep(0.05)
    return news_dict, total_found

def decode_google_url(url):
    try:
        if "articles/" not in url: return url
        s = url.split("articles/")[1].split("?")[0]
        s = s + '=' * (4 - len(s) % 4)
        decoded = base64.urlsafe_b64decode(s)
        real_url_match = re.search(rb'(https?://[^\x00-\x20"\'<>]+)', decoded)
        if real_url_match:
            return real_url_match.group(1).decode('utf-8', errors='ignore')
    except: pass
    return url

def summarize_batch_with_retry(batch_news):
    if not batch_news: return ""
    client = genai.Client(api_key=GEMINI_API_KEY)
    raw_text = ""
    for comp, news_list in batch_news.items():
        raw_text += f"【{comp}】\n" + "\n".join(news_list) + "\n\n"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # V20 核心提示词：确保深度与格式
            prompt = f"""你现在是自动驾驶行业的高级首席分析师。请对素材进行深度跨语言整合分析。
            
            任务要求：
            1. 按公司分类，标题格式：==== 【公司名】 ====
            2. 每家公司直接使用 Bullet Points (•) 分点描述动态，严禁写大段核心总结。
            3. 格式统一：每条动态必须且仅以“• ”开头（严禁使用星号 *），紧跟加粗标题。
            4. 内容深度：每个 bullet 的内容总结必须非常详细、深入，包含其技术细节或行业影响分析。
            5. 结构化标记：总结标题：详细分析内容@@@媒体名称：新闻标题@@@URL地址
            
            ⚠️ 全文必须中文。总结标题与内容之间用“：”分割，后面用“@@@”连接。严禁使用 ** 加粗。
            素材：\n{raw_text}"""
            
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                time.sleep(65)
                continue
            return ""
    return ""

def parse_to_feishu_elements(text):
    """V20 解析引擎：强制星号清洗 + 标题锚点超链接"""
    final_blocks = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 强制清洗开头的星号、点号等多余符号
        line = re.sub(r'^[*•·\s]+', '', line)
        
        # 1. 公司名抬头加粗逻辑
        if re.match(r'====\s*【.*?】\s*====', line):
            comp_name = re.search(r'【.*?】', line).group()
            final_blocks.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": f"==== {comp_name} ====", "text_element_style": {"bold": True}}}]}})
        
        # 2. 核心动态行解析：通过 @@@ 实现超链接缝合
        elif "@@@" in line:
            parts = line.split("@@@")
            if len(parts) >= 3:
                analysis_part = parts[0].strip() # 总结标题：详细分析内容
                title_info = parts[1].strip()     # 媒体：标题
                url_raw = parts[2].strip()        # Google链接
                real_url = decode_google_url(url_raw) 
                
                elements = []
                # 冒号前总结标题强制加粗
                if "：" in analysis_part:
                    sub_split = analysis_part.split("：", 1)
                    elements.append({"text_run": {"content": "• " + sub_split[0] + "：", "text_element_style": {"bold": True}}})
                    elements.append({"text_run": {"content": sub_split[1] + " "}})
                else:
                    elements.append({"text_run": {"content": "• " + analysis_part + " "}})
                
                # 标题缝合超链接 (锚点化)
                elements.append({"text_run": {
                    "content": f"[{title_info}]",
                    "text_element_style": {"text_color": 4, "link": {"url": real_url}}
                }})
                final_blocks.append({"block_type": 2, "text": {"elements": elements}})
        else:
            final_blocks.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": "• " + line}}]}})
            
    return final_blocks

def main():
    token = get_feishu_token()
    if not token: return
    companies = extract_companies_from_feishu(token)
    if not companies: return
    news_dict, news_count = fetch_raw_news_dict(companies)
    
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{DOCUMENT_ID}/blocks/{DOCUMENT_ID}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 页眉统计
    requests.post(url, headers=headers, json={"children": [
        {"block_type": 22, "divider": {}},
        {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": f"🌐 {today} 全球智驾颗粒化深度研报 (V20)"}}]}},
        {"block_type": 2, "text": {"elements": [{"text_run": {"content": f"📊 监测 {len(companies)} 家企业，深度整合 {news_count} 条研判动态。", "text_element_style": {"bold": True}}}]}}
    ]})

    all_keys = list(news_dict.keys())
    batch_size = 20
    for i in range(0, len(all_keys), batch_size):
        batch_keys = all_keys[i:i + batch_size]
        batch_news = {k: news_dict[k] for k in batch_keys}
        batch_summary = summarize_batch_with_retry(batch_news)
        if batch_summary:
            blocks = parse_to_feishu_elements(batch_summary)
            for j in range(0, len(blocks), 10):
                requests.post(url, headers=headers, json={"children": blocks[j : j + 10]})
                time.sleep(1)
        time.sleep(10)

if __name__ == "__main__":
    main()
