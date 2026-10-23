#!/usr/bin/env bash
# 每日定时抓取入口（由 crontab 在 JST 10:30 调用，安装见 scripts/setup_local_env.sh）。
# 北京时间 09:00 窗口截止 = JST 10:00，10:30 启动留出 30 分钟余量。
# 日志：data/tmp/cron/YYYY-MM-DD.log（data/tmp 已 gitignore）
set -uo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)         # 按脚本位置推算，迁移目录后无需改
export HOME=${HOME:-/root}                       # cron 会设 HOME；git/gh/claude 的登录都在 HOME 下
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

cd "$REPO" || exit 1
DATE=$(TZ=Asia/Shanghai date +%F)          # 日报日期按北京时间
LOG_DIR="$REPO/data/tmp/cron"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$DATE.log"

# 防重入：上一次还没跑完就跳过
exec 9>"$LOG_DIR/.lock"
if ! flock -n 9; then
  echo "$(date '+%F %T %Z') 上一次任务仍在运行，跳过" >> "$LOG"
  exit 0
fi

PROMPT="跑今日 robotaxi 新闻（定时任务，无人值守，日报日期 ${DATE}）。

严格按 SKILL.md 和 workflows/daily-fetch.md 执行完整默认流程 Phase 1–6（含 4b）：
- 开工前 git pull --ff-only origin main
- 覆盖窗口：北京时间前一日 09:00 ~ ${DATE} 09:00，抓取命令用 --date ${DATE}
- 写入 data/daily/${DATE}.md，Phase 3 用 scripts/publish_daily.py 发布到 docs/data/daily.json
- 写作风格遵守 style-guide.md，评级参考 important-examples.md
- 全程自动，不要等待或询问用户；无法核实的条目按规则暂缓并写进运行统计
- 结束前确认 JSON 校验通过、git diff 只是新增当日数据，然后 git add -A && git commit -m \"daily ${DATE}\" && git push（push 冲突先 pull 再推，禁止 force push）
- 德州 DMV 汇总在日报文件和汇报里都放在全部新闻之后，不要混在新闻中间
- 最后按「结束动作」模板输出汇报（critical 告警放最顶部）"

{
  echo "===== $(date '+%F %T %Z') 开始 daily ${DATE} ====="
  # 本地 RSSHub（X 源 + 国内媒体源）没起来就先拉起，最多等 60 秒
  if ! curl -sf -m 5 http://127.0.0.1:1200/healthz >/dev/null; then
    echo "RSSHub 未响应，尝试 docker start rsshub"
    docker start rsshub >/dev/null 2>&1
    for _ in $(seq 1 30); do curl -sf -m 3 http://127.0.0.1:1200/healthz >/dev/null && break; sleep 2; done
  fi
  curl -sf -m 5 http://127.0.0.1:1200/healthz >/dev/null && echo "RSSHub OK" || echo "RSSHub 仍不可用（抓取会报 RSSHUB_DOWN 告警）"
  timeout 3h claude -p "$PROMPT" \
    --permission-mode acceptEdits \
    --allowedTools "Bash" "Read" "Edit" "Write" "Glob" "Grep" "WebSearch" "WebFetch"
  rc=$?
  echo "===== $(date '+%F %T %Z') 结束，退出码 ${rc} ====="
} >> "$LOG" 2>&1
