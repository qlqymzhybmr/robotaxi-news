#!/usr/bin/env bash
# 设置 / 更新本地 RSSHub 的 X(Twitter) 凭证，并重建容器、验证能抓到新推文。
# 用法：在本机终端运行 scripts/set_twitter_token.sh，粘贴 auth_token 后回车（输入不回显）。
# token 只写入 /root/.config/rsshub/rsshub.env（600 权限，不进 git）。
set -euo pipefail

ENV_FILE=/root/.config/rsshub/rsshub.env
IMAGE=diygod/rsshub:latest

read -rsp "粘贴 x.com 的 auth_token 后回车（不回显）: " TOKEN; echo
TOKEN=$(printf '%s' "$TOKEN" | tr -d '[:space:]"')
[ -n "$TOKEN" ] || { echo "token 为空，未修改"; exit 1; }

mkdir -p "$(dirname "$ENV_FILE")"; touch "$ENV_FILE"; chmod 600 "$ENV_FILE"
grep -v '^TWITTER_AUTH_TOKEN=' "$ENV_FILE" > "$ENV_FILE.tmp" || true
printf 'TWITTER_AUTH_TOKEN=%s\n' "$TOKEN" >> "$ENV_FILE.tmp"
mv "$ENV_FILE.tmp" "$ENV_FILE"; chmod 600 "$ENV_FILE"
unset TOKEN

# --env-file 只在创建容器时读取，所以必须重建而不是 restart
docker rm -f rsshub >/dev/null 2>&1 || true
docker run -d --name rsshub --restart unless-stopped \
  -p 127.0.0.1:1200:1200 --env-file "$ENV_FILE" "$IMAGE" >/dev/null
for _ in $(seq 1 30); do curl -sf -m 3 http://127.0.0.1:1200/healthz >/dev/null && break; sleep 2; done

python3 - <<'EOF'
import calendar, feedparser, time
f = feedparser.parse("http://127.0.0.1:1200/twitter/user/Tesla")
ts = [e.published_parsed for e in f.entries if getattr(e, "published_parsed", None)]
if not ts:
    print("❌ 没取到任何推文，看 docker logs rsshub"); raise SystemExit(1)
age = (time.time() - calendar.timegm(max(ts))) / 86400
print(f"@Tesla 最新推文 {time.strftime('%Y-%m-%d %H:%M', max(ts))} UTC（{age:.1f} 天前）")
print("✅ 凭证可用" if age < 7 else "❌ 仍是旧推文，token 可能无效或复制不完整")
EOF
