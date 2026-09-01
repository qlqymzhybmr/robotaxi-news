"""压缩 weekly_overrides.json 里内联的 base64 图片。

周报里的图片是粘贴时经 FileReader.readAsDataURL 内联进 JSON 的，原始 PNG
未经优化。base64 会让体积再涨 33%，而且 PNG 已压缩过、gzip 几乎无效
（实测压缩比仅 1.3x），所以这个文件会成为网页加载的最大负担：
2026-09-01 时它 1.56MB，其中 99.6% 是两张图，实际传输 1181KB，占全站 61%。

转成 WebP 后实测省 90%+，文字放大 2 倍仍清晰。

因为粘贴路径没变，新贴的图仍是 PNG，所以这个脚本设计成**可重复运行**：
每次跑只压缩尚未压缩的图，已经是 WebP 的跳过。

用法：
    python scripts/compress_weekly_images.py            # 预览，不写入
    python scripts/compress_weekly_images.py --apply    # 实际写入
"""
import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image

TARGET = Path("docs/data/weekly_overrides.json")
QUALITY = 90  # 实测 q90 文字边缘无可见伪影；再低会开始糊
DATA_URI = re.compile(r"data:image/(\w+);base64,([A-Za-z0-9+/=]+)")


def main() -> int:
    ap = argparse.ArgumentParser(description="压缩 weekly_overrides.json 内联图片")
    ap.add_argument("--apply", action="store_true", help="实际写入（默认只预览）")
    ap.add_argument("--quality", type=int, default=QUALITY)
    ap.add_argument("--target", default=str(TARGET))
    args = ap.parse_args()

    path = Path(args.target)
    if not path.exists():
        print(f"找不到 {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    before = len(text)
    matches = list(DATA_URI.finditer(text))
    if not matches:
        print("没有找到内联图片，无需处理。")
        return 0

    print(f"{path}  当前 {before/1024:.0f}KB，内联图片 {len(matches)} 张\n")

    stats = {"converted": 0, "skipped": 0, "failed": 0, "saved": 0}

    def convert(m: re.Match) -> str:
        fmt, payload = m.group(1).lower(), m.group(2)
        if fmt == "webp":
            stats["skipped"] += 1
            return m.group(0)
        try:
            raw = base64.b64decode(payload)
            im = Image.open(io.BytesIO(raw))
            buf = io.BytesIO()
            im.convert("RGB").save(buf, format="WEBP", quality=args.quality)
            new_payload = base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception as exc:  # 坏图不应该毁掉整个文件
            print(f"  ! 第 {stats['converted']+stats['failed']+1} 张转换失败，保持原样：{exc}")
            stats["failed"] += 1
            return m.group(0)

        if len(new_payload) >= len(payload):  # 压不动就别换
            stats["skipped"] += 1
            return m.group(0)

        stats["converted"] += 1
        stats["saved"] += len(payload) - len(new_payload)
        print(f"  图{stats['converted']}: {im.width}x{im.height} {fmt.upper()} "
              f"{len(payload)/1024:.0f}KB -> WEBP {len(new_payload)/1024:.0f}KB "
              f"(省 {(1-len(new_payload)/len(payload))*100:.1f}%)")
        return f"data:image/webp;base64,{new_payload}"

    out = DATA_URI.sub(convert, text)

    # 写回前必须确认仍是合法 JSON，否则网页会整个白屏
    try:
        json.loads(out)
    except json.JSONDecodeError as exc:
        print(f"\n中止：替换后 JSON 非法（{exc}），未写入任何内容。")
        return 1

    after = len(out)
    print(f"\n转换 {stats['converted']} 张，跳过 {stats['skipped']} 张，失败 {stats['failed']} 张")
    print(f"{before/1024:.0f}KB -> {after/1024:.0f}KB  （省 {(1-after/before)*100:.1f}%）")

    if not args.apply:
        print("\n预览模式，未写入。加 --apply 实际生效。")
        return 0

    path.write_text(out, encoding="utf-8")
    print(f"已写入 {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
