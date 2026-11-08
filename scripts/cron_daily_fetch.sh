#!/usr/bin/env bash
# 每日定时抓取入口（由 crontab 调用，安装见 scripts/setup_local_env.sh）。
#
#   cron_daily_fetch.sh            JST 10:30 正常运行：抓取当天（北京时间日期）的日报
#   cron_daily_fetch.sh --retry    每小时运行：补跑因 Claude 用量上限失败的日期（无待办则立即退出，不调用 Claude）
#
# 北京时间 09:00 窗口截止 = JST 10:00，10:30 启动留出 30 分钟余量。
# 撞到用量上限（"You've hit your weekly/session limit"）时，把该日期写进 data/tmp/cron/pending_retry，
# 之后每小时重试一次，直到成功或超过 7 天（Google News 日期限定查询可回溯，再久召回会明显变差）。
# 日志：data/tmp/cron/YYYY-MM-DD.log（data/tmp 已 gitignore）
set -uo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)         # 按脚本位置推算，迁移目录后无需改
export HOME=${HOME:-/root}                       # cron 会设 HOME；git/gh/claude 的登录都在 HOME 下
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

cd "$REPO" || exit 1
LOG_DIR="$REPO/data/tmp/cron"
PENDING="$LOG_DIR/pending_retry"
mkdir -p "$LOG_DIR"
touch "$PENDING"
TODAY=$(TZ=Asia/Shanghai date +%F)         # 日报日期按北京时间
LIMIT_RE="hit your .*limit|usage limit|weekly limit|session limit"
MAX_AGE_DAYS=7

MODE=normal
[ "${1:-}" = "--retry" ] && MODE=retry

# 重试模式：没有待办就直接退出（每小时都会被调用，这里必须零开销）
if [ "$MODE" = retry ] && ! grep -q . "$PENDING"; then
  exit 0
fi

# 防重入：正常运行与重试共用一把锁，上一次还没跑完就跳过
exec 9>"$LOG_DIR/.lock"
if ! flock -n 9; then
  echo "$(date '+%F %T %Z') 上一次任务仍在运行，跳过（mode=$MODE）" >> "$LOG_DIR/$TODAY.log"
  exit 0
fi

pending_add()    { grep -qx "$1" "$PENDING" || echo "$1" >> "$PENDING"; }
pending_remove() { grep -vx "$1" "$PENDING" > "$PENDING.tmp" || true; mv "$PENDING.tmp" "$PENDING"; }

ensure_rsshub() {
  # 本地 RSSHub（X 源 + 国内媒体源）没起来就先拉起，最多等 60 秒
  if ! curl -sf -m 5 http://127.0.0.1:1200/healthz >/dev/null; then
    echo "RSSHub 未响应，尝试 docker start rsshub"
    docker start rsshub >/dev/null 2>&1
    for _ in $(seq 1 30); do curl -sf -m 3 http://127.0.0.1:1200/healthz >/dev/null && break; sleep 2; done
  fi
  curl -sf -m 5 http://127.0.0.1:1200/healthz >/dev/null && echo "RSSHub OK" || echo "RSSHub 仍不可用（抓取会报 RSSHUB_DOWN 告警）"
}

build_prompt() {
  local d=$1 backfill=$2 extra=""
  if [ "$backfill" = yes ]; then
    extra="
这是补跑（原定时任务因 Claude 用量上限失败，补跑时间 $(TZ=Asia/Shanghai date '+%F %H:%M') 北京时间）：
- 日报开头的「运行模式」写明补跑及原因；Reddit 与官方新闻室 RSS 只保留最近若干条，补跑召回偏少，在运行统计里注明
- 德州 DMV 不可回溯：不要运行 track_tx_av_registrations.py，DMV 一节写明本期不可回溯
- 若 data/daily/ 里已有晚于 ${d} 的日报，先读它的「首发早于窗口」和「核查后暂缓」，避免与之重复或遗漏
- Uber CEO 访谈 / Bolt 进展：若更晚日期的日报已覆盖回看窗口则不再单独查，在统计里注明"
  fi
  cat <<EOF
跑 robotaxi 新闻（定时任务，无人值守，日报日期 ${d}）。

严格按 SKILL.md 和 workflows/daily-fetch.md 执行完整默认流程 Phase 1–6（含 4b）：
- 开工前 git pull --ff-only origin main
- 覆盖窗口：北京时间 ${d} 前一日 09:00 ~ ${d} 09:00，抓取命令用 --date ${d}
- 写入 data/daily/${d}.md，Phase 3 用 scripts/publish_daily.py ${d} 发布到 docs/data/daily.json
- 写作风格遵守 style-guide.md，评级参考 important-examples.md
- 全程自动，不要等待或询问用户；无法核实的条目按规则暂缓并写进运行统计
- 结束前确认 JSON 校验通过、git diff 只是新增当日数据，然后 git add -A && git commit -m "daily ${d}" && git push（push 冲突先 pull 再推，禁止 force push）
- 德州 DMV 汇总在日报文件和汇报里都放在全部新闻之后，不要混在新闻中间
- 最后按「结束动作」模板输出汇报（critical 告警放最顶部）${extra}
EOF
}

# 跑一天的日报；撞额度上限 → 记入待重跑；成功 → 从待重跑移除
run_daily() {
  local d=$1 backfill=$2 log="$LOG_DIR/$1.log" out rc
  out=$(mktemp)
  {
    echo "===== $(date '+%F %T %Z') 开始 daily ${d}（mode=$MODE, backfill=$backfill） ====="
    ensure_rsshub
  } >> "$log" 2>&1
  timeout 3h claude -p "$(build_prompt "$d" "$backfill")" \
    --permission-mode acceptEdits \
    --allowedTools "Bash" "Read" "Edit" "Write" "Glob" "Grep" "WebSearch" "WebFetch" > "$out" 2>&1
  rc=$?
  cat "$out" >> "$log"
  if grep -Eqi "$LIMIT_RE" "$out"; then
    pending_add "$d"
    echo "===== $(date '+%F %T %Z') 结束，退出码 ${rc}：撞到 Claude 用量上限，已加入待重跑（每小时重试） =====" >> "$log"
  elif [ "$rc" -eq 0 ]; then
    pending_remove "$d"
    echo "===== $(date '+%F %T %Z') 结束，退出码 0 =====" >> "$log"
  else
    echo "===== $(date '+%F %T %Z') 结束，退出码 ${rc}（非额度原因，不自动重跑） =====" >> "$log"
  fi
  rm -f "$out"
}

if [ "$MODE" = normal ]; then
  run_daily "$TODAY" no
else
  # 逐个补跑待办日期（按日期从旧到新）；过期的放弃并记日志
  for d in $(sort -u "$PENDING"); do
    age=$(( ( $(date -d "$TODAY" +%s) - $(date -d "$d" +%s) ) / 86400 ))
    if [ "$age" -gt "$MAX_AGE_DAYS" ]; then
      echo "$(date '+%F %T %Z') ${d} 已超过 ${MAX_AGE_DAYS} 天仍未补跑成功，放弃，请手动处理" >> "$LOG_DIR/$d.log"
      pending_remove "$d"; continue
    fi
    # 已有人手动补过（文件已在 git 里）就不再跑
    if git ls-files --error-unmatch "data/daily/${d}.md" >/dev/null 2>&1; then
      echo "$(date '+%F %T %Z') data/daily/${d}.md 已存在于仓库，移出待重跑" >> "$LOG_DIR/$d.log"
      pending_remove "$d"; continue
    fi
    backfill=yes; [ "$d" = "$TODAY" ] && backfill=no
    run_daily "$d" "$backfill"
    # 仍然撞上限就不再继续跑后面的日期，等下一个小时
    grep -qx "$d" "$PENDING" && break
  done
fi
