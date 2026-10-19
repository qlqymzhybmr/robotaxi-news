#!/usr/bin/env bash
# 迁移 / 新机器一键准备（Ubuntu / Debian）。可重复运行：已就绪的步骤会跳过。
#
#   scripts/setup_local_env.sh            安装依赖 + 启动本地 RSSHub + 安装每日定时任务 + 体检
#   scripts/setup_local_env.sh --check    只体检，不安装、不改任何东西
#
# 做不了、需要人手动完成的三件事（脚本会在体检里提示）：
#   1. scripts/set_twitter_token.sh   填 X 的 auth_token（不进 git）
#   2. claude 登录                    运行一次 claude，按提示登录
#   3. gh auth login                  GitHub 登录（定时任务要 push）
set -uo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
ENV_FILE=/root/.config/rsshub/rsshub.env
IMAGE=diygod/rsshub:latest
CRON_LINE_TAG="cron_daily_fetch.sh"
CHECK_ONLY=0; [ "${1:-}" = "--check" ] && CHECK_ONLY=1
export HOME=${HOME:-/root}
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

say()  { printf '\n== %s\n' "$*"; }
apt_install() {
  local missing=()
  for p in "$@"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
  [ ${#missing[@]} -eq 0 ] && return 0
  echo "安装：${missing[*]}"
  $SUDO apt-get update -qq && DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq "${missing[@]}"
}

if [ $CHECK_ONLY -eq 0 ]; then
  say "1/4 系统依赖（Python 抓取脚本 + Docker）"
  # 系统 Python 是 externally-managed，依赖走 apt 而不是 pip
  apt_install python3 python-is-python3 python3-feedparser python3-pil docker.io curl git gh cron
  $SUDO systemctl enable --now docker cron >/dev/null 2>&1

  say "2/4 本地 RSSHub（X 源 + 国内媒体源，监听 127.0.0.1:1200）"
  $SUDO mkdir -p "$(dirname "$ENV_FILE")"; $SUDO chmod 700 "$(dirname "$ENV_FILE")"
  if [ ! -f "$ENV_FILE" ]; then
    printf '# RSSHub 本地实例环境变量（不进 git）\nNODE_ENV=production\nCACHE_TYPE=memory\nCACHE_EXPIRE=300\nTWITTER_AUTH_TOKEN=\n' | $SUDO tee "$ENV_FILE" >/dev/null
    $SUDO chmod 600 "$ENV_FILE"
  fi
  if ! $SUDO docker inspect rsshub >/dev/null 2>&1; then
    $SUDO docker pull -q "$IMAGE"
    $SUDO docker run -d --name rsshub --restart unless-stopped \
      -p 127.0.0.1:1200:1200 --env-file "$ENV_FILE" "$IMAGE" >/dev/null
  else
    $SUDO docker start rsshub >/dev/null
  fi
  for _ in $(seq 1 30); do curl -sf -m 3 http://127.0.0.1:1200/healthz >/dev/null && break; sleep 2; done

  say "3/4 每日定时任务（JST 10:30 = 北京 09:30）"
  # cron 按系统时区解释时间，所以把 JST 10:30 换算成本机时区
  read -r CRON_H CRON_M < <(python3 - <<'EOF'
from datetime import datetime
from zoneinfo import ZoneInfo
t = datetime.now(ZoneInfo("Asia/Tokyo")).replace(hour=10, minute=30, second=0).astimezone()
print(t.hour, t.minute)
EOF
)
  chmod +x "$REPO"/scripts/*.sh
  ( crontab -l 2>/dev/null | grep -v "$CRON_LINE_TAG" | grep -v '^# robotaxi daily fetch'
    echo "# robotaxi daily fetch — 每天 JST 10:30（本机时区 $(timedatectl show -p Timezone --value 2>/dev/null || date +%Z) 下为 ${CRON_H}:$(printf %02d "$CRON_M")）"
    echo "$CRON_M $CRON_H * * * $REPO/scripts/cron_daily_fetch.sh"
  ) | crontab -
  if [ "$(date +%z)" != "+0900" ]; then
    echo "⚠️ 本机时区不是 JST，已换算为本地 ${CRON_H}:$(printf %02d "$CRON_M")；若本机时区有夏令时，切换后需重跑本脚本"
  fi

  say "4/4 让 git 用 gh 的登录凭证（定时任务 push 需要）"
  gh auth status >/dev/null 2>&1 && gh auth setup-git >/dev/null 2>&1 && echo "已配置 gh 为 git 凭证助手"
fi

# ---------------------------------------------------------------- 体检
say "体检"
ok=1
chk() { if eval "$2" >/dev/null 2>&1; then printf '  ✅ %s\n' "$1"; else printf '  ❌ %s → %s\n' "$1" "$3"; ok=0; fi; }
chk "Python + feedparser"         "python3 -c 'import feedparser'"        "apt install python3-feedparser"
chk "Docker 运行中"               "$SUDO docker info"                      "systemctl start docker"
chk "RSSHub 健康（127.0.0.1:1200）" "curl -sf -m 5 http://127.0.0.1:1200/healthz" "docker start rsshub；看 docker logs rsshub"
chk "X token 已填"                "$SUDO grep -q '^TWITTER_AUTH_TOKEN=.\+' $ENV_FILE" "运行 scripts/set_twitter_token.sh"
chk "X 能取到 7 天内的推文"        "python3 - <<'EOF'
import calendar, feedparser, time, sys
f = feedparser.parse('http://127.0.0.1:1200/twitter/user/Tesla')
ts = [e.published_parsed for e in f.entries if getattr(e, 'published_parsed', None)]
sys.exit(0 if ts and time.time() - calendar.timegm(max(ts)) < 7 * 86400 else 1)
EOF" "token 失效或未填：运行 scripts/set_twitter_token.sh"
chk "定时任务已安装"              "crontab -l | grep -q $CRON_LINE_TAG"   "重跑本脚本（不带 --check）"
chk "cron 服务运行中"             "systemctl is-active cron"              "systemctl enable --now cron"
chk "claude CLI 可用"             "command -v claude"                     "安装 Claude Code 并运行一次 claude 登录"
chk "GitHub 登录（gh）"           "gh auth status"                        "gh auth login，然后重跑本脚本"
chk "git 能推送到 origin"          "git -C $REPO push --dry-run origin HEAD" "检查 gh auth / 远程地址"
[ $ok -eq 1 ] && echo -e "\n全部就绪。" || echo -e "\n有未就绪项，按 → 后面的提示处理后重跑：scripts/setup_local_env.sh --check"
