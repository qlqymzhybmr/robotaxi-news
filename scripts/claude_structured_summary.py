import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


CN_TZ = timezone(timedelta(hours=8))
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"


def resolve_api_url() -> str:
    explicit = os.environ.get("ANTHROPIC_MESSAGES_URL")
    if explicit:
        return explicit.rstrip("/")

    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    if base.endswith("/v1/messages"):
        return base
    if base.endswith("/v1"):
        return f"{base}/messages"
    return f"{base}/v1/messages"


def resolve_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", MODEL)


def load_items(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("items", []), data.get("meta", {})


def group_by_company(items):
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get("company", "Unknown")].append(item)
    return grouped


def build_prompt(company: str, items: list, run_date: str) -> str:
    payload = []
    for it in items:
        payload.append(
            {
                "title": it.get("title", ""),
                "published_at": it.get("published_at", ""),
                "source": it.get("source", ""),
                "url": it.get("url", ""),
                "summary": it.get("summary", ""),
                "lang": it.get("lang", ""),
            }
        )

    return (
        f"你是自动驾驶行业分析师。请对公司 {company} 的候选新闻做去重与结构化总结。\n"
        f"运行日期: {run_date}\n"
        "要求:\n"
        "1) 先去重: 同一事件多源报道合并为 1 条; 保留主来源和辅助来源。\n"
        "2) 输出 0~5 条最重要新闻。\n"
        "3) 每条严格输出 JSON 对象字段:\n"
        "   - title_cn\n"
        "   - importance(1-3)\n"
        "   - summary_cn(120~220字,客观、信息密度高)\n"
        "   - event_date(YYYY-MM-DD,未知则空字符串)\n"
        "   - primary_source{name,url}\n"
        "   - secondary_sources[{name,url}]\n"
        "4) 仅返回 JSON 数组,不要 markdown,不要解释。\n"
        f"候选新闻:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def call_claude(prompt: str, api_key: str) -> str:
    body = {
        "model": resolve_model(),
        "max_tokens": 2200,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = Request(
        resolve_api_url(),
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    text_blocks = payload.get("content", [])
    if not text_blocks:
        return "[]"
    return text_blocks[0].get("text", "[]")


def safe_parse_json_array(raw_text: str):
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()
    start = raw_text.find("[")
    end = raw_text.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        return json.loads(raw_text[start : end + 1])
    except Exception:
        return []


def mock_company_summary(items: list):
    out = []
    for it in sorted(items, key=lambda x: x.get("published_at", ""), reverse=True)[:5]:
        date = (it.get("published_at", "") or "")[:10]
        out.append(
            {
                "title_cn": it.get("title", "")[:120],
                "importance": 2,
                "summary_cn": (it.get("summary", "") or it.get("title", ""))[:220],
                "event_date": date,
                "primary_source": {
                    "name": it.get("source", "source"),
                    "url": it.get("url", ""),
                },
                "secondary_sources": [],
            }
        )
    return out


def to_markdown(grouped_summary: dict, run_date: str, window_start: str, window_end: str) -> str:
    lines = [
        f"# Robotaxi Daily {run_date}",
        "",
        f"> 覆盖窗口: {window_start} ~ {window_end} (北京时间)",
        "",
    ]

    for company in sorted(grouped_summary.keys()):
        lines.append(f"### {company}")
        items = grouped_summary[company]
        if not items:
            lines.append("(过去24h无相关新闻。)")
            lines.append("")
            continue

        for it in items:
            stars = "⭐" * int(it.get("importance", 1))
            title = it.get("title_cn", "")
            summary = it.get("summary_cn", "")
            event_date = it.get("event_date", "")
            primary = it.get("primary_source", {}) or {}
            secondary = it.get("secondary_sources", []) or []

            lines.append(f"- [ ] {stars} **{company}:{event_date},{title}**")
            lines.append("")
            lines.append(f"  {summary}")
            lines.append("")
            lines.append(f"  - 原始发布日期:{event_date}")
            if primary.get("name") and primary.get("url"):
                lines.append(f"  - 权威源: [{primary.get('name')}]({primary.get('url')})")
            if secondary:
                sec_links = "、".join(
                    [f"[{s.get('name','source')}]({s.get('url','')})" for s in secondary if s.get("url")]
                )
                if sec_links:
                    lines.append(f"  - 辅助源: {sec_links}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Claude structured summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--mock", action="store_true", help="Use local mock summary without Claude API")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not args.mock and not api_key:
        raise SystemExit("ANTHROPIC_API_KEY is required (or use --mock for offline test)")

    items, meta = load_items(Path(args.input))
    grouped = group_by_company(items)

    result = {}
    for company, news in grouped.items():
        if args.mock:
            result[company] = mock_company_summary(news)
            continue

        prompt = build_prompt(company, news, args.date)
        try:
            raw = call_claude(prompt, api_key)
            parsed = safe_parse_json_array(raw)
            result[company] = parsed
        except HTTPError as e:
            raise SystemExit(f"Claude API error: {e.code} {e.reason}. Check ANTHROPIC_API_KEY.")

    md = to_markdown(
        result,
        run_date=args.date,
        window_start=meta.get("window_start", ""),
        window_end=meta.get("window_end", ""),
    )

    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)

    Path(args.output_md).write_text(md, encoding="utf-8")
    Path(args.output_json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    total_items = sum(len(v) for v in result.values())
    mode = "mock" if args.mock else "claude"
    print(f"done mode={mode} companies={len(result)} items={total_items} md={args.output_md} json={args.output_json}")


if __name__ == "__main__":
    main()
