---
name: robotaxi-news-tracking
description: 全球 Robotaxi、L2/L4 智能驾驶、政策法规的每日新闻追踪与每周简报生成。当用户说"跑今日新闻"、"跑 robotaxi daily"、"生成上周周报"等命令时触发。
---

# Robotaxi News Tracking Skill

## 这个 skill 是做什么的

这个 skill 帮 Long(DiDi 智驾产品/分析师)每天追踪全球 Robotaxi 竞品动态,并在每周一生成一份给老板看的简报。核心流程是统一主流程下的 Daily + Weekly:

1. **每日抓取(daily-fetch)**:实习生每天上午手动触发一次(包括周末),覆盖过去 24 小时新闻,Claude 自动发布所有 ⭐⭐+ 到网页
2. **周报生成(weekly-report)**:每周一,把**上周二到本周一**你勾选 `[x]` 的新闻汇总为 OneNote 可粘贴 HTML,并同步发布到网页

**关键时间逻辑**:周报的覆盖范围是**上周二 ~ 本周一**(共 7 天),以周一作为周报的结尾。所以周一的 daily 跑完后,立刻就可以生成本周周报,不需要等到周二。

---

## 触发命令

| 命令(用户怎么说) | 对应 workflow | 何时跑 |
|------|------|------|
| "跑今日 robotaxi 新闻" / "daily fetch" / "跑今天的新闻" | `workflows/daily-fetch.md`(默认:自动分两阶段) | 每天上午,实习生手动触发 |
| "只跑国外组" / "daily fetch overseas" | `workflows/daily-fetch.md`(仅 Phase 1) | 单独补跑某一组时 |
| "只跑国内组" / "daily fetch china" | `workflows/daily-fetch.md`(仅 Phase 2) | 单独补跑某一组时 |
| "生成本周周报" / "weekly report" / "做这周的简报" | `workflows/weekly-report.md` | 每周一,勾完三天 daily 之后 |
| "发布今日精选" / "publish daily" | `workflows/daily-publish.md` | 一般不用手动触发,daily-fetch 自动串接 |
| "发布本周周报到网页" / "publish weekly" | `workflows/weekly-publish.md` | 一般不用手动触发,weekly-report 自动串接 |
| "更新竞品 list" / "加一家公司到 list" | 直接编辑 `competitors.md`（Robotaxi Competitor & Keywords） | 任意时间 |
| "学习这次的判断" / "把这条加进 examples" | 直接编辑 `important-examples.md` | 每次划完重点后 |

**默认执行策略(重要)**:
- 说"跑今日新闻"时,skill **默认自动分两阶段执行**:
  - Phase 1:国外组(Python 抓取 `competitors.md` 的国外公司)
  - Phase 2:国内组(Python 抓取 `competitors.md` 的国内公司)
- 两阶段的产物**合并写入同一份文件** `data/daily/YYYY-MM-DD.md`(包含 "## 国外 L4" 和 "## 国内 L4" 等 section),实习生体感是一次跑完、一份文件
- 分阶段的好处:避免单次 tool 调用过多导致上下文或 5 小时额度问题
- 如果 Phase 1 跑完后中断(网络/额度),隔一段时间说"只跑国内组"即可补跑 Phase 2,不会覆盖已有的国外组内容

---

## 工作原理

### 信息源(如何不漏查)

这个 skill **不依赖单一搜索**,用三层策略叠加:

**第一层:Python 定向召回（主力）**
- 启动时读取 `competitors.md` 的公司清单 + `## 搜索关键词`
- 按公司执行 Python 抓取(基于 Google News RSS),严格过滤到 24 小时窗口
- 抓取配额:
  - 重点公司(⭐):中英双语各抓,每语种最多 10 条
  - 普通公司:单语抓取为主(国内中文/国外英文),每语种最多 5 条

**第二层:Claude 去重 + 结构化理解**
- 候选新闻先由 Claude 做 URL 归一化去重 + 语义去重,避免同一事件重复写入
- 去重后保留"主来源 + 辅助来源"链路,降低遗漏风险
- 再由 Claude 生成结构化总结(公司、事件、影响),输出到 daily 文件和网页 JSON

**第三层:网页投递（自动）**
- daily-publish / weekly-publish 按既有流程写入 `docs/data/*.json` 并驱动网页展示

**关于 `archive/legacy-fetch/sources.md` 与 Tier URL**:
- 旧的 Tier URL fetch 流程已下线,不再作为主流程执行
- `archive/legacy-fetch/sources.md` 仅作历史归档与应急兜底参考,默认不批量抓取

### 这个 skill 做不到的事(必读)

**为了让你和实习生有合理预期,必须明确以下限制:**

1. **没有专业新闻 API**:skill 当前主流程用的是 Python + Google News RSS 召回。**没有接入** NewsAPI、GDELT、Bloomberg Terminal、彭博社等专业新闻源
2. **微信公众号几乎抓不到**:很多中国公司新闻最早只发公众号,搜索引擎对微信内容索引很差。等到二次转载到新浪/36氪可能延迟 1-2 天
3. **X / Twitter 滞后**:搜索引擎对 X 的索引滞后明显,车主目击视频、Musk 即时推文这类内容**很可能错过**或滞后
4. **非中英文媒体覆盖差**:日韩德法的本地新闻基本要等英文转载,原始日文/德文 PR 抓不到
5. **预估覆盖率:约 70-85%**。剩余 15-30% 需要靠人工补漏

**降低漏查的措施**:
- 强烈建议实习生每天看完 daily 后,**手动扫一眼 1-2 个垂直媒体**(推荐 CnEVPost、36氪汽车)作为 backup
- 如果发现某次明显漏查,告诉 Claude 调整 competitors.md 或启用 `archive/legacy-fetch/sources.md` 做应急补漏

---

## 文件结构

```
robotaxi-news/
├── SKILL.md                     # 你正在看的这个文件
├── DEPLOY.md                    # GitHub Pages 首次部署指南
├── competitors.md               # 竞品 + 关键词维护入口
├── style-guide.md               # 写作风格规则(学自 Long 的历史周报)
├── important-examples.md        # 重要性判断规则(每次划完重点后追加)
├── workflows/
│   ├── daily-fetch.md           # 每日抓取的执行步骤(含 Phase 3 自动发布)
│   ├── weekly-report.md         # 周报生成的执行步骤(含步骤 8.5 + 11)
│   ├── daily-publish.md         # 每日精选自动发布到网页
│   └── weekly-publish.md        # 周报自动发布到网页
├── scripts/
│   ├── python_rss_fetch.py      # 主流程 Python 召回脚本(读取 competitors.md 产出结构化 JSON)
│   └── claude_structured_summary.py # Claude 去重与结构化总结脚本
├── archive/
│   └── legacy-fetch/            # 已下线的旧抓取方案归档
│       ├── sources.md           # 旧 Tier URL 白名单(仅应急兜底)
│       └── ref/                 # 旧 Python/Gemini 抓取参考实现
├── data/
│   ├── daily/                   # 每日抓取产物,文件名 YYYY-MM-DD.md
│   └── reports/                 # 周报 HTML(YYYY-Wxx.html)+ JSON 副产物(YYYY-Wxx.json)
└── docs/                        # GitHub Pages 网站根目录(固定用 /docs,GitHub 原生支持)
    ├── index.html               # 单文件网页(Tailwind CDN + 原生 JS)
    └── data/
        ├── daily.json           # 每日精选数据(Claude 自动写入)
        └── weekly.json          # 周报数据(Claude 自动写入)
```

---

## 实习生操作手册(每日 / 每周)

### 每天上班后 / 每天上午 10 点左右(20-30 分钟)

**包括周六和周日**。周末不跑的话,周一补三天工作量会很大,所以养成每天跑一次的习惯。

1. 打开 Claude Code,说:"跑今日 robotaxi 新闻"
2. Claude 会自动分两阶段跑 daily-fetch(Phase 1 国外 + Phase 2 国内),耗时约 20-30 分钟
3. 跑完后,用 VS Code / Cursor 打开 `data/daily/YYYY-MM-DD.md`(今天日期)
4. **逐条看,把认为重要的条目前面的 `[ ]` 改成 `[x]`**
5. 可以**直接修改文字**——比如觉得某条措辞不准、或者想补充事实
6. 保存文件
7. (可选)说:"学习这次的判断",让 Claude 把你的勾选规律追加到 `important-examples.md`

**提示**:如果某天 Claude Code 跑到一半卡住(网络/额度问题),等一会儿说"只跑国内组"或"只跑国外组"补跑缺失的那一半即可。两阶段都写入同一份 daily 文件,不会冲突。

### 周一上班后(额外 15-20 分钟)

周一是**特殊日子**:既要跑当天的 daily,又要补勾周末两天没勾的 daily,还要生成周报。

**先理清时间逻辑**:
- **周报覆盖范围是"上周二 ~ 本周一"**(共 7 天),以周一作为周报的结尾
- 例:本周一是 4 月 13 日,那本周发出的周报覆盖 4 月 7 日(上周二)到 4 月 13 日(周一),标题是 `无人驾驶行业0407-0413重要新闻`
- 周一 daily 跑完后,立刻就可以生成本周周报

**周一流程**(在常规的"每天跑 daily"之后追加这些步骤):
1. **先按"每天上班后"的常规流程跑一次周一的 daily 并勾选重点**(上面那 7 步)
2. 然后打开 `data/daily/` 目录,找到**上周六**和**上周日**两份 daily
3. **补勾这两天的重点**(这两天没人上班,还没来得及勾)
4. 检查上周二 ~ 上周五 四份 daily 是否都已经勾过
5. 全部勾完后,说:"生成本周周报"
6. Claude 读取上周二 ~ 本周一共 7 份 daily,生成周报到 `data/reports/YYYY-Wxx.html`
7. 浏览器双击打开 HTML 文件
8. **Ctrl+A 全选 → Ctrl+C → 在 OneNote 新建一页 → Ctrl+V 粘贴**
9. 在 OneNote 里手动**微调文字、替换/补充图片**
10. OneNote 整页截图,发老板

**周一总工作量估算**:跑 daily(20-30 分钟) + 勾周一 daily(5 分钟) + 补勾周六周日 daily(10 分钟) + 生成周报(3-5 分钟) + OneNote 粘贴微调(10 分钟) = **约 50-65 分钟**。

---

## 维护这个 skill

### 想加/删一家竞品公司
直接编辑 `competitors.md`。这是一份按组分类的 markdown list + 关键词配置,加一行公司或补充关键词即可。下次 daily-fetch 会自动覆盖。

### 想调整写作风格
编辑 `style-guide.md`。这个文件里写的是从历史周报里学到的规则(比如"日期开头"、"加粗用于事实而非情绪"、"零评论性词汇"等)。改了之后下次 weekly-report 会按新规则生成。

### 想调整重要性判断
有两种方式:
1. **被动学习**:每天划完重点后说"学习这次的判断",Claude 会把你的勾选追加到 `important-examples.md`
2. **主动编辑**:直接打开 `important-examples.md` 添加规则,比如"涉及融资金额超过 5 亿美元的一律重要"

### 想加新的信息源
当前主流程优先维护 `competitors.md` 的公司与关键词。`archive/legacy-fetch/sources.md` 仅在应急补漏时启用。

---

## Token 消耗与运行成本

| 操作 | 工具调用次数 | 预估 input tokens | 预估时长 |
|------|------|------|------|
| daily-fetch(默认两阶段 + 自动发布)| 取决于公司覆盖与新闻量 | 25万-55万 | 15-25 分钟 |
| daily-fetch(仅一组,单独跑)| 取决于公司覆盖与新闻量 | 12万-30 万 | 8-15 分钟 |
| weekly-report(含 JSON 副产物 + 自动发布)| ~8 | 5-10 万 | 3-5 分钟 |
| daily-publish(手动单独跑)| ~2 | <1 万 | <1 分钟 |
| weekly-publish(手动单独跑)| ~2 | <1 万 | <1 分钟 |

**关于 Pro 套餐限制**:
- Claude Code **和 claude.ai 共享同一个 5h 配额池**(2026 年 4 月当前情况)
- daily-fetch 默认两阶段模式会消耗较大配额,建议**跑的时候不要同时在 claude.ai 上做别的事**
- 如果某次 daily-fetch 触发了 5h 限制,等 5 小时后说"只跑国内组"补跑 Phase 2 即可
- **周一负载错峰建议**:
  - 上午跑 daily-fetch(当天的)+ 勾周一 daily
  - 补勾上周六、上周日 daily
  - **吃完午饭再说"生成本周周报"**(让 5h 配额休息一会)
  - 周一下午:粘到 OneNote、发老板
- 如果觉得 Pro 配额经常不够用,考虑升级到 Max 5x ($100/月) 或 Max 20x ($200/月)

---

## 网页展示

### 访问地址

https://qlqymzhybmr.github.io/robotaxi-news/

### 工作方式（自动串接）

1. 实习生说"跑今日新闻",Claude 跑完 daily-fetch 后自动串接 daily-publish
2. daily-publish 从今日 daily 文件里提取所有 ⭐⭐+ 条目,写入 `docs/data/daily.json`
3. 实习生运行 `git add -A && git commit -m "daily YYYY-MM-DD" && git push`,约 1-2 分钟后网页更新
4. 每周一周报生成后,weekly-report 自动串接 weekly-publish,把 `[x]` 汇总结果写入 `docs/data/weekly.json`,同样 push 后自动更新

### 网页功能

- **每日精选 tab**(默认):按日期倒序展示,支持按日期/公司/国内外筛选
- **周报 tab**:按周次浏览,渲染结构化周报正文
- 所有数据通过 JSON 文件驱动,无需后端服务器

### 首次部署

参见 `DEPLOY.md`。部署只需做一次,之后每次 push 自动发布。

---

## 已知问题与改进方向

- [ ] 图片自动下载到本地(目前是引用在线 URL,OneNote 粘贴时会自动嵌入,但理论上有图被原站删除的风险)
- [ ] 自动调度(目前是实习生每天手动触发一次。未来可研究用 Windows 任务计划程序 + 休眠唤醒,或云 VPS 部署的方案)
- [ ] 微信公众号源接入(技术难度高,待研究)
- [ ] X / Twitter 实时监控(需要 API,目前不可行)
- [ ] 接入专业新闻 API(NewsAPI / GDELT 等,需要预算)

如果有新的需求或发现 bug,直接编辑这个 SKILL.md 文件记录下来。

---

## 重要教训与避坑指南

### ⚠️ 关键错误：覆盖 daily.json 导致历史数据丢失（2026-04-23）

**问题描述**：
在执行 Phase 3（daily-publish）时，Claude 直接用 `Write` 工具覆盖了整个 `docs/data/daily.json` 文件，导致所有历史数据（10天的新闻记录）全部丢失。同时还遗漏了 JSON 数组的闭合方括号 `]`，导致 JSON 格式错误，网页无法正常显示。

**根本原因**：
1. **未遵循 daily-publish.md 的规则**：应该先读取现有 JSON，然后插入或替换今日数据，而不是直接覆盖整个文件
2. **Write 工具使用不当**：对于需要追加/更新的 JSON 文件，应该先 Read → 修改 → Write，而不是直接 Write

**正确做法**（参考 `workflows/daily-publish.md` 步骤 4-5）：
```javascript
// 1. 读取现有 daily.json
const existingData = require('./docs/data/daily.json');

// 2. 构建今日 entry
const newEntry = { date: "YYYY-MM-DD", items: [...] };

// 3. 插入或替换
// - 如果数组里已有 date == 今天的 entry，替换它
// - 否则，插入到数组开头（保持日期倒序）
const existingIndex = existingData.findIndex(e => e.date === newEntry.date);
if (existingIndex >= 0) {
  existingData[existingIndex] = newEntry; // 替换
} else {
  existingData.unshift(newEntry); // 插入到开头
}

// 4. 写回文件
fs.writeFileSync('docs/data/daily.json', JSON.stringify(existingData, null, 2));
```

**防范措施**：
- ✅ **Phase 3 开始前**：必须先 `Read` 现有的 `docs/data/daily.json`
- ✅ **写入前验证**：用 `node -e "require('./docs/data/daily.json')"` 验证 JSON 格式
- ✅ **提交前检查**：确认 git diff 显示的是"新增今日数据"而不是"删除所有历史数据"
- ✅ **备份意识**：重要的数据文件操作前，可以先用 `git show HEAD:path/to/file` 备份

**恢复方法**（如果再次发生）：
```bash
# 1. 从上次提交恢复历史数据
git show HEAD~1:docs/data/daily.json > docs/data/daily_backup.json

# 2. 用 Node.js 合并新旧数据
node -e "
const old = require('./docs/data/daily_backup.json');
const newEntry = { /* 今日数据 */ };
const merged = [newEntry, ...old];
require('fs').writeFileSync('docs/data/daily.json', JSON.stringify(merged, null, 2));
"

# 3. 验证并提交
node -e "require('./docs/data/daily.json'); console.log('✅ JSON 格式正确')"
git add docs/data/daily.json && git commit -m "fix: 恢复历史数据" && git push
```

**影响范围**：
- 网页无法显示任何新闻（JSON 解析失败）
- 历史数据全部丢失（需要从 git 历史恢复）
- 需要额外的修复提交和推送

**总结**：
对于 `docs/data/daily.json` 和 `docs/data/weekly.json` 这类**累积型数据文件**，永远不要直接 `Write` 覆盖，必须先 `Read` → 修改 → `Write`。这是 daily-publish 和 weekly-publish 流程的核心规则。
