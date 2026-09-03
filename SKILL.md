---
name: robotaxi-news-tracking
description: 全球 Robotaxi、L2/L4 智能驾驶、政策法规的每日新闻追踪与每周简报生成。当用户说"跑今日新闻"、"跑 robotaxi daily"、"生成上周周报"等命令时触发。
---

# Robotaxi News Tracking Skill

## 这个 skill 是做什么的

这个 skill 帮 Long(DiDi 智驾产品/分析师)每天追踪全球 Robotaxi 竞品动态,并在每周一生成一份给老板看的简报。核心流程是统一主流程下的 Daily + Weekly:

1. **每日抓取(daily-fetch)**:实习生每天上午手动触发一次(包括周末),覆盖过去 24 小时新闻,Claude 自动把**全部条目**发布到网页
2. **周报生成(weekly-report)**:每周一,把**上周二到本周一**你在网页选稿 UI 中选定的条目汇总为 OneNote 可粘贴 HTML,并同步发布到网页

**关键时间逻辑**:周报的覆盖范围是**上周二 ~ 本周一**(共 7 天),以周一作为周报的结尾。所以周一的 daily 跑完后,立刻就可以生成本周周报,不需要等到周二。

---

## 触发命令

| 命令(用户怎么说) | 对应 workflow | 何时跑 |
|------|------|------|
| "跑今日 robotaxi 新闻" / "daily fetch" / "跑今天的新闻" | `workflows/daily-fetch.md`(默认:自动分两阶段) | 每天上午,实习生手动触发 |
| "只跑国外组" / "daily fetch overseas" | `workflows/daily-fetch.md`(仅 Phase 1) | 单独补跑某一组时 |
| "只跑国内组" / "daily fetch china" | `workflows/daily-fetch.md`(仅 Phase 2) | 单独补跑某一组时 |
| "生成本周周报" / "weekly report" / "做这周的简报" | `workflows/weekly-report.md` | 每周一,网页选稿完成之后 |
| "发布今日精选" / "publish daily" | `workflows/daily-publish.md` | 一般不用手动触发,daily-fetch 自动串接 |
| "发布本周周报到网页" / "publish weekly" | `workflows/weekly-publish.md` | 一般不用手动触发,weekly-report 自动串接 |
| "更新竞品 list" / "加一家公司到 list" | 直接编辑 `competitors.md`（Robotaxi Competitor & Keywords） | 任意时间 |
| "把这条加进 examples" | 直接编辑 `important-examples.md`（仅在发现评级明显偏差时手动补充） | 按需 |

**默认执行策略(重要)**:
- 说"跑今日新闻"时,skill **默认自动跑完 6 个 Phase**:

| Phase | 做什么 | 产出去哪 |
|------|------|------|
| 1 | 国外组抓取 | `data/daily/YYYY-MM-DD.md` 国外 section |
| 2 | 国内组抓取 | 同一文件的国内 section |
| 3 | 自动发布**全部条目**（不按 rating 过滤） | `docs/data/daily.json` |
| 4 | **Uber CEO 访谈查询** | **不写文件,单独提醒用户**(见下) |
| 5 | **抓取源健康告警** | **不写文件,单独提醒用户**(见下) |
| 6 | **德州 DMV 车队登记** | 有增减则**写进 daily**（它是真新闻） |

- Phase 1、2 的产物**合并写入同一份文件** `data/daily/YYYY-MM-DD.md`（包含 "## 国外 L4" 和 "## 国内 L4" 等 section）,体感是一次跑完、一份文件
- Phase 4、5 **刻意不写进 daily 文件**:它们不是当日新闻,也不进周报,混进去只会干扰阅读
- 分阶段的好处:避免单次 tool 调用过多导致上下文或 5 小时额度问题
- 如果 Phase 1 跑完后中断(网络/额度),隔一段时间说"只跑国内组"即可补跑 Phase 2,不会覆盖已有的国外组内容

---

## 工作原理

### 信息源(如何不漏查)

这个 skill **不依赖单一搜索**,用三层策略叠加:

**第一层:Python 定向召回（主力）**

一次运行同时跑**五类来源**,互相补漏,配置全部在 `competitors.md`:

| 来源 | 抓什么 | 链接质量 |
|------|------|------|
| Track B：Google News RSS | 按公司名 + 关键词全网搜索（主力召回） | ⚠️ 搜索链接 |
| Track A：本地媒体 site: 查询 | 各公司运营城市的地方报 / TV 台（`data/local_media.json`） | ⚠️ 搜索链接 |
| Track C：行业媒体 RSS | 综合财经科技媒体大盘源，必过主题关键词 | ✅ 真实永久链接 |
| 直接订阅 RSS | 公司官方新闻室 + X(Twitter) via 自部署 RSSHub | ✅ 真实永久链接 |
| Reddit 社区热帖 | r/SelfDrivingCars、r/Waymo、r/teslamotors | ✅ 真实链接 |

- 严格过滤到 24 小时窗口
- 抓取配额（Track A / B）:
  - 重点公司(⭐):中英双语各抓,每语种最多 10 条
  - 普通公司:单语抓取为主(国内中文/国外英文),每语种最多 5 条

**Track C 为什么单独存在**(2026-09-01 新增):Track B 是**按公司名检索**的,所以**不含公司名的监管/政策类新闻会被结构性漏掉**。实测 2026-08-31「商务部等三部门发布车联网及自动驾驶数据合规指引」只有 Track C 抓到,Track B 全漏。同时 Track C 返回发布方真实永久链接,不受下面的链接失效问题影响。

**关于链接（重要,别再重复踩坑）**:Google News RSS 给的是几天后就失效的包装 URL,**还原成真实链接的路子已全部实测排除**——base64 解码、Google `batchexecute` 私有接口、302 跳转、Bing News RSS、DuckDuckGo 全部不可行(细节见 `workflows/daily-fetch.md` 的「链接策略」)。因此 Track A/B 的条目存的是**精心构造的搜索链接**(去发布方后缀 + 精确短语引号 + `site:` 限定 + 走网页索引而非新闻索引),目标是"每次点开都能稳定找到同一篇"。**同一事件若 Track C 也抓到,优先用 Track C 的真实链接。**

**第二层:Claude 去重 + 结构化理解**
- 候选新闻先由 Claude 做 URL 归一化去重 + 语义去重,避免同一事件重复写入
- 去重后保留"主来源 + 辅助来源"链路,降低遗漏风险
- 再由 Claude 生成结构化总结(公司、事件、影响),直接写入 daily 文件(无中间 JSON 产物)

**第三层:网页投递（自动）**
- daily-publish / weekly-publish 按既有流程写入 `docs/data/*.json` 并驱动网页展示

**关于 `archive/legacy-fetch/sources.md` 与 Tier URL**:
- 旧的 Tier URL fetch 流程已下线,不再作为主流程执行
- `archive/legacy-fetch/sources.md` 仅作历史归档与应急兜底参考,默认不批量抓取

### 每天自动盯着的两件事(Phase 4 / Phase 5)

这两件都是**每天 daily 跑完自动执行、有情况才提醒**,不需要单独触发,也不写进 daily 文件。

**Phase 4:Uber CEO Dara Khosrowshahi 访谈**
- 覆盖 YouTube、Spotify、Apple Podcasts、媒体专访、现场活动 —— 不只是 YouTube
- **强制核实发布日期**:搜索摘要里出现"2026"不算数,必须打开页面确认真实上传/发布日期,确认不了就不报
- 只报**距今 ≤ 14 天**的新访谈
- 去重台账 `data/uber_ceo_interviews.json`:报过的不再报,避免同一期天天弹。不想再被某条打扰,手动加进 `seen` 即可

**Phase 5:抓取源健康告警**
- 抓取脚本在输出 JSON 的顶层 `health` 字段里做好分级,命令行也会打印
- **critical**(凭证过期、IP 被封)→ 提到最终回复**最顶部**,因为只有用户能修
- **warning**(限速、瞬时错误)→ 结束动作里列一行
- **silent_feeds**(请求成功但返回 0 条)→ 单独列出,这是最隐蔽的故障类型
- 为什么要专门做这个:**源静默失效不会报错**,只会让某个源"今天恰好没新闻",不主动播报可能几周没人发现

典型的 critical 长这样:

```
🚨 X(Twitter) 抓取凭证已失效,22 个 X 源当前抓不到任何内容。
   → 到 Railway → rsshub 服务 → Variables 更新 TWITTER_AUTH_TOKEN
     取值:DevTools → Application → Cookies → x.com → 复制 auth_token 的 Value
```

### 每天自动跟的第三件事：德州 DMV 车队登记（Phase 6）

德州要求自动驾驶运营方在 TxMCCS **逐辆登记**车辆。这是目前**唯一公开、逐车、官方**的各家车队规模数据源——媒体几乎不报道车队数量变化，但它是判断扩张节奏最直接的指标，而且**可以横向对比各家**。

```bash
python scripts/track_tx_av_registrations.py
```

**基线（2026-09-03）**：共 **12 家运营方 / 2,111 辆**。前三名 **Waymo 988**（I-PACE 767 + RT 221）、**Tesla 420**（Model Y 375 + Cybercab 45）、**Avride 344**（Ioniq 5）。完整表见 `workflows/daily-fetch.md` 的 Phase 6。

与 Phase 4/5 不同，**有增减就写进 daily 文件**（它是当日发生、可核实的行业事实，属于新闻）；新车型首次出现或单日 +50 辆以上评 ⭐⭐⭐。抓取失败时脚本会**拒绝写入**（失败 ≠ 车队清零）。

### 🔁 抓到「地域动作」必须当场刷新本地媒体清单

**这是每日流程里的强制检查。** 只要新闻里出现**新开城 / 扩区 / 转入商业运营 / 开始路测 / 开始测绘**,就要立刻核对 `data/local_media.json` 里该公司在该城市是否已有条目,没有就补上并**当场验证能抓到东西**。

**为什么必须当场做**:Track A 靠这份清单发起 `site:` 查询。清单里没有的城市,**该地所有本地报道都会被结构性漏掉**——地方 TV 台和地方报的事故、投诉、社区反弹这类一手信号,Google News 的权重根本压不出来。

**实际代价（2026-09-02 实例）**:Waymo 开三城时清单里已有丹佛/圣迭戈/坦帕,三地本地媒体全部命中;但 **Zoox 宣布进驻休斯顿和圣迭戈时清单里没有**,那天 Zoox 的消息只能靠 Track B 捡回来。事后补了 9 个站点。

补充时**优先复用同城已在其他公司下验证过的站点**（同城媒体通用，直接抄）。完整操作步骤见 `workflows/daily-fetch.md` 的「强制触发」章节。

### 定期维护(不是每天,但别忘)

| 事项 | 频率 | 命令 |
|------|------|------|
| 滚动 daily 归档 | 约每月 | `python scripts/roll_daily_archive.py --apply` |
| 压缩周报图片 | 贴过新图之后 | `python scripts/compress_weekly_images.py --apply` |
| 核查 local_media.json | 每季度**兜底**（日常靠上面的强制触发，这里只查旧站点是否失效） | 手动 |
| 复查静默源 | Phase 5 连续 2 天报同一个源 | 手动打开该 feed URL 确认 |
| **普查新增 AV 运营方** | 每季度 | `python scripts/track_tx_av_registrations.py --discover` |

两个脚本都**默认只预览、加 `--apply` 才写入**,且都是幂等的,重复跑安全。

### 这个 skill 做不到的事(必读)

**为了让你和实习生有合理预期,必须明确以下限制:**

1. **没有专业新闻 API**:skill 当前主流程用的是 Python + Google News RSS 召回。**没有接入** NewsAPI、GDELT、Bloomberg Terminal、彭博社等专业新闻源
2. **微信公众号几乎抓不到**:很多中国公司新闻最早只发公众号,搜索引擎对微信内容索引很差。等到二次转载到新浪/36氪可能延迟 1-2 天
3. **X / Twitter 滞后**:搜索引擎对 X 的索引滞后明显,车主目击视频、Musk 即时推文这类内容**很可能错过**或滞后
4. **非中英文媒体覆盖差**:日韩德法的本地新闻基本要等英文转载,原始日文/德文 PR 抓不到
5. **预估覆盖率:约 70-85%**。剩余 15-30% 需要靠人工补漏

**降低漏查的措施**:
- **CnEVPost、36氪 已在 2026-09-01 接入 Track C 自动抓取**,不再需要手动扫。仍建议偶尔人工抽查一两个垂直媒体作为 backup
- ⚠️ **汽车垂直媒体仍是盲区**:RSSHub 没有汽车之家 / 第一电动 / 盖世汽车 / 懂车帝 / 车东西 的路由,这几家目前只能靠 Track B 搜索召回,是已知最薄弱的一环
- 如果发现某次明显漏查,告诉 Claude 调整 competitors.md 或启用 `archive/legacy-fetch/sources.md` 做应急补漏

---

## 文件结构

```
robotaxi-news/
├── SKILL.md                     # 你正在看的这个文件
├── DEPLOY.md                    # GitHub Pages 首次部署指南
├── competitors.md               # 竞品 + 关键词维护入口
├── style-guide.md               # 写作风格规则(学自 Long 的历史周报)
├── important-examples.md        # 重要性判断参考例(供 ⭐ 评级参考，按需手动维护)
├── workflows/
│   ├── daily-fetch.md           # 每日抓取的执行步骤(含 Phase 3 自动发布)
│   ├── weekly-report.md         # 周报生成的执行步骤(含步骤 8.5 + 11)
│   ├── daily-publish.md         # 每日精选自动发布到网页
│   └── weekly-publish.md        # 周报自动发布到网页
├── scripts/
│   ├── python_rss_fetch.py      # 主流程 Python 召回脚本(读取 competitors.md 产出结构化 JSON + health 健康分级)
│   ├── roll_daily_archive.py    # 定期:把 daily.json 的旧日期滚动进归档(带条目守恒校验)
│   ├── compress_weekly_images.py # 定期:压缩周报内联图片(PNG→WebP,幂等)
│   └── track_tx_av_registrations.py # Phase 6:德州 DMV 车队登记追踪
├── archive/
│   ├── claude_structured_summary.py # 已归档:旧的 API 调用总结脚本(已由 Claude 直接总结替代)
│   └── legacy-fetch/            # 已下线的旧抓取方案归档
│       ├── sources.md           # 旧 Tier URL 白名单(仅应急兜底)
│       └── ref/                 # 旧 Python/Gemini 抓取参考实现
├── data/
│   ├── daily/                   # 每日抓取产物,文件名 YYYY-MM-DD.md
│   ├── uber_ceo_interviews.json # Phase 4 去重台账(报过的访谈,避免重复提醒)
│   ├── tx_av_registrations.json # Phase 6 德州车队登记历史快照
│   └── reports/                 # 周报 HTML(YYYY-Wxx.html)+ JSON 副产物(YYYY-Wxx.json)
└── docs/                        # GitHub Pages 网站根目录(固定用 /docs,GitHub 原生支持)
    ├── index.html               # 单文件网页(Tailwind CDN + 原生 JS)
    └── data/
        ├── daily.json           # 每日精选,近 90 天(Phase 3 只写这个)
        ├── daily-archive.json   # 每日精选,更早的历史(只由 roll_daily_archive.py 维护)
        ├── weekly.json          # 周报数据(Claude 自动写入)
        └── weekly_overrides.json # 周报人工修订 + 内联图片(定期跑压缩脚本)
```

---

## 实习生操作手册(每日 / 每周)

### 每天上班后 / 每天上午 10 点左右(20-30 分钟)

**包括周六和周日**。周末不跑的话,周一补三天工作量会很大,所以养成每天跑一次的习惯。

1. 打开 Claude Code,说:"跑今日 robotaxi 新闻"
2. Claude 会自动跑完 6 个 Phase,耗时约 20-30 分钟。**跑完就结束了,不需要你做任何事**
3. (可选)看一眼 `data/daily/YYYY-MM-DD.md`,觉得哪条措辞不准或想补事实,可以**直接改文字**
4. (可选)网页上打开「周报选稿」tab,为本周周报挑条目——这一步也可以攒到周一再做

**⚠️ 逐条勾选 `[ ]` → `[x]` 的流程已于 2026-09-02 取消。** 重要性判断改由 Claude 在写入时用 ⭐ 评级完成(标准见 `workflows/daily-fetch.md` 的「⭐ 评级标准」)。

取消的原因:重要性规则已经积累够多,继续按人工勾选训练会让筛选越来越紧,**导致抓到的内容被过度丢弃**。现在的原则是**宁可多留**——⭐ 条目同样写进 daily、同样发布到网页,评级只影响阅读优先级,真正的筛选留到周报选稿阶段做。

**提示**:如果某天 Claude Code 跑到一半卡住(网络/额度问题),等一会儿说"只跑国内组"或"只跑国外组"补跑缺失的那一半即可。两阶段都写入同一份 daily 文件,不会冲突。

### 周一上班后(额外 15-20 分钟)

周一是**特殊日子**:既要跑当天的 daily,又要在网页选稿 UI 里完成本周选稿,还要生成周报。

**先理清时间逻辑**:
- **周报覆盖范围是"上周二 ~ 本周一"**(共 7 天),以周一作为周报的结尾
- 例:本周一是 4 月 13 日,那本周发出的周报覆盖 4 月 7 日(上周二)到 4 月 13 日(周一),标题是 `无人驾驶行业0407-0413重要新闻`
- 周一 daily 跑完后,立刻就可以生成本周周报

**周一流程**(在常规的"每天跑 daily"之后追加这些步骤):
1. **先跑一次周一的 daily**(上面那几步)
2. 打开网页的「**周报选稿**」tab,选择本周区间(上周二 ~ 本周一)
3. **逐条勾选要进周报的条目并保存**——保存会写入 `docs/data/selections.json`
4. 说:"生成本周周报"
5. Claude 会先 `git pull` 拉取你刚保存的选稿,再据此生成周报到 `data/reports/YYYY-Wxx.html`
7. 浏览器双击打开 HTML 文件
8. **Ctrl+A 全选 → Ctrl+C → 在 OneNote 新建一页 → Ctrl+V 粘贴**
9. 在 OneNote 里手动**微调文字、替换/补充图片**
10. OneNote 整页截图,发老板

**周一总工作量估算**:跑 daily(20-30 分钟) + 网页选稿(10-15 分钟) + 生成周报(3-5 分钟) + OneNote 粘贴微调(10 分钟) = **约 45-55 分钟**。

---

## 维护这个 skill

### 想加/删一家竞品公司
直接编辑 `competitors.md`。这是一份按组分类的 markdown list + 关键词配置,加一行公司或补充关键词即可。下次 daily-fetch 会自动覆盖。

### 想调整写作风格
编辑 `style-guide.md`。这个文件里写的是从历史周报里学到的规则(比如"日期开头"、"加粗用于事实而非情绪"、"零评论性词汇"等)。改了之后下次 weekly-report 会按新规则生成。

### 想调整重要性判断
有两种方式:
直接打开 `important-examples.md` 添加规则,比如"涉及融资金额超过 5 亿美元的一律重要"。

⭐ 评级标准本身定义在 `workflows/daily-fetch.md`。**注意别把规则写得越来越严**——取消人工勾选的初衷就是避免过度筛选。

### 想加新的信息源
当前主流程优先维护 `competitors.md` 的公司与关键词。`archive/legacy-fetch/sources.md` 仅在应急补漏时启用。

**加一个新媒体 RSS 源**（推荐,链接质量最高）:在 `competitors.md` → `## 行业媒体 RSS` 下加一行 `媒体名 | 地区 | 是否重点 | RSS URL` 即可,脚本会自动带上主题关键词过滤。加之前先验证这个 feed 真的能出条目:

```bash
python -c "import feedparser;f=feedparser.parse('https://example.com/feed');print(len(f.entries))"
```

**注意区分两个 section**:
- `## 直接订阅 RSS` —— 公司官方新闻室,条条相关,**不过滤**
- `## 行业媒体 RSS` —— 综合大盘源,**强制过主题关键词**（`MEDIA_TOPIC_KEYWORDS`）

放错 section 的后果:公司源放进行业媒体 section 会漏掉不含关键词的官方公告;大盘源放进直接订阅 section 会每天灌进几百条无关新闻。

**调整主题关键词**:改 `scripts/python_rss_fetch.py` 的 `MEDIA_TOPIC_KEYWORDS`。加词前想清楚该词在**非自动驾驶语境**下有多常见——例如 `端到端` 就因为在大模型报道里泛滥而被刻意移除。

---

## Token 消耗与运行成本

> 当前套餐:**Max**。配额已不是约束,下面的数字用于**判断哪一步不正常**,不再用于省着跑。
> 实测基准:2026-09-01 那次运行(国外 37 家 + 国内 52 家,产出 11 条)。

### 各步骤实测量级

| 操作 | 主要 input 来源 | 实测 input tokens | 预估时长 |
|------|------|------|------|
| daily-fetch Phase 1(国外)| `raw_news_overseas.json` 53KB | **约 1.4 万** | 8-12 分钟 |
| daily-fetch Phase 2(国内)| `raw_news_china.json` 90KB | **约 2.4 万** | 8-12 分钟 |
| daily-fetch Phase 3(发布)| ⚠️ 见下方 `daily.json` 说明 | **1 万 ~ 54 万**(取决于做法) | <2 分钟 |
| weekly-report(含发布)| 7 份 daily md,每份约 4 千 | 约 5-10 万 | 3-5 分钟 |
| daily-publish / weekly-publish(单独跑)| 同上 | <1 万 | <1 分钟 |

抓取本身(Python 跑 RSS)**不消耗 Claude token**,真正花 token 的是 Claude 读 JSON + 写总结。所以公司数量增加对 token 的影响远小于对**时长**的影响。

### ⚠️ 真正的大头是 `docs/data/daily.json`

2026-09-01 已按「近 90 天 + 归档」拆分,现状:

| 文件 | 内容 | 全量读入上下文的代价 |
|------|------|------|
| `docs/data/daily.json` | 近 **90 天**(daily-publish 只写这里) | 约 **34 万 token** |
| `docs/data/daily-archive.json` | 更早的历史(当前 51 天) | 约 19 万 token |

每天仍增长约 14 KB,靠 `scripts/roll_daily_archive.py` 定期滚动封顶(见 `workflows/daily-fetch.md` 的「定期维护」)。

**拆分是为了给网页首屏减负,不是为了省 Claude 的 token。** token 的正确解法是下面这条区分:

**关键区分**:贵的是把它 **`Read` 进 Claude 上下文**;用 **Python 在进程内读它是 0 token**。

所以 Phase 3 的规则是:

| 动作 | 允许? | 代价 |
|------|------|------|
| `Read` 整份 `daily.json` | ❌ **禁止** | 约 34 万 token,且每天在涨 |
| `Read` 整份 `daily-archive.json` | ❌ **禁止**,而且 Phase 3 根本用不到它 | 约 19 万 token |
| `Read` 前 10 行确认最新日期 | ✅ | 可忽略 |
| Python `json.load` → 插入 → `json.dump` 写回 | ✅ **唯一正确做法** | 0 token |
| 用 Edit / Write 手拼 JSON 字符串 | ❌ **禁止** | 见下 |

**Phase 3 只写 `daily.json`,永远不要碰 `daily-archive.json`。** 归档是滚动脚本的职责,发布流程误写归档会造成日期重叠。

**必须用 `workflows/daily-publish.md` 步骤 6 的 Python 写法**,原因有两个,缺一不可:
1. **省 token**:文件由 Python 读,不进 Claude 上下文
2. **保证转义正确**:`json.dump` 自动处理引号。手拼字符串做不到——2026-09-01 就是因为用 Edit 手写 JSON,`summary_html` 里的中文引号未转义,**整份 JSON 失效、网页一条都显示不出来**,只能事后写脚本批量修

**校验用 Python,不要用 `node -e "require(...)"`**(后者对语法错误的报错位置不精确):

```bash
python -c "import json;d=json.load(open('docs/data/daily.json',encoding='utf-8'));print(len(d),d[0]['date'],len(d[0]['items']))"
```

### 关于配额

- Max 套餐下,daily-fetch 两阶段连着跑、周一 daily + 周报连着做,都不需要错峰
- 不再需要"跑的时候别用 claude.ai"这类规避动作
- 真要看当前用量,在交互式 `claude` 终端里跑 `/usage`(本会话是非交互环境,看不了)
- 如果某次仍然中断(网络/超时,而非配额),照旧说"只跑国内组"补跑 Phase 2 即可,两阶段写同一份文件不会冲突

---

## 网页展示

### 访问地址

https://qlqymzhybmr.github.io/robotaxi-news/

### 工作方式（自动串接）

1. 实习生说"跑今日新闻",Claude 跑完 daily-fetch 后自动串接 daily-publish
2. daily-publish 从今日 daily 文件里提取**全部条目**（不按 rating 过滤）,写入 `docs/data/daily.json`
3. 实习生运行 `git add -A && git commit -m "daily YYYY-MM-DD" && git push`,约 1-2 分钟后网页更新
4. 每周一周报生成后,weekly-report 自动串接 weekly-publish,把选稿汇总结果写入 `docs/data/weekly.json`,同样 push 后自动更新

### ⚠️ Claude Code 工作目录与本地主目录不同步问题

**原因**：Claude Code 每次任务都在 `.claude/worktrees/<分支名>/` 下创建独立 worktree，所有文件编辑和 git push 均在 worktree 内完成。主目录 `D:\Desktop\robotaxi-news` 不会自动感知这些变更（Cursor 直接在主目录工作，所以没有这个问题）。

**规则：每次 git push 完成后，Claude 必须紧接着执行以下命令同步本地主目录：**

```bash
git -C "D:\Desktop\robotaxi-news" pull origin main
```

如果出现本地冲突（`Your local changes would be overwritten`），说明本地有过时的修改，先丢弃再拉取：

```bash
git -C "D:\Desktop\robotaxi-news" restore docs/data/daily.json   # 或冲突的具体文件
git -C "D:\Desktop\robotaxi-news" pull origin main
```

**checklist（每次 push 后必做）**：
- [ ] `git push origin <worktree-branch>:main` ✅ 推送成功
- [ ] `git -C "D:\Desktop\robotaxi-news" pull origin main` ✅ 本地主目录已同步

### 网页功能

- **每日精选 tab**(默认):按日期倒序展示,支持按日期/公司/国内外筛选
- **周报 tab**:按周次浏览,渲染结构化周报正文
- 所有数据通过 JSON 文件驱动,无需后端服务器

### 首屏性能(2026-09-01 优化)

优化前每次打开网页要传 **1943 KB**(gzip 后),两个原因都不在直觉位置:

| 文件 | 优化前传输 | 优化后 | 怎么做的 |
|------|------|------|------|
| `weekly_overrides.json` | **1181 KB**(占 61%) | 约 90 KB | 内联图片 PNG→WebP。它 99.6% 是两张 base64 图,而 base64 后的 PNG 几乎压不动(gzip 仅 1.3x),所以磁盘比 daily.json 小、传输却更大 |
| `daily.json` | 680 KB | 约 430 KB | 拆成近 90 天 + 归档 |
| `weekly.json` | 62 KB | 不变 | **本身没问题**,不用管 |

**归档是"后台补齐"不是"不加载"**:`index.html` 的 `loadDailyArchive()` 在首屏渲染完成后才去拉 `daily-archive.json`,拉到后合并进 `dailyData` 并重建筛选器。**网页上看到的数据仍然是全量 141 天,一条不少**,只是不再阻塞首屏。

改动时的两个坑(已处理,改这块代码要注意):
- `buildDateFilter()` 是 **append 式**构建,重建前必须先清掉旧 option(保留第一项"全部日期"),否则会出现 141 个重复项
- `buildCompanyFilter()` 会**整个重建下拉**,重建后必须从 `selectedCompanies` 还原勾选状态,否则用户已选的公司会被清空

### 首次部署

参见 `DEPLOY.md`。部署只需做一次,之后每次 push 自动发布。

---

## 已知问题与改进方向

- [ ] 图片自动下载到本地(目前是引用在线 URL,OneNote 粘贴时会自动嵌入,但理论上有图被原站删除的风险)
- [ ] 自动调度(目前是实习生每天手动触发一次。未来可研究用 Windows 任务计划程序 + 休眠唤醒,或云 VPS 部署的方案)
- [ ] 微信公众号源接入(技术难度高,待研究)
- [ ] X / Twitter 实时监控(需要 API,目前不可行)
- [ ] 接入专业新闻 API(NewsAPI / GDELT 等,需要预算)
- [ ] **汽车垂直媒体接入**(汽车之家 / 第一电动 / 盖世汽车 / 懂车帝 / 车东西。RSSHub 无对应路由,需自己写解析器或找第三方镜像。这是当前最大的覆盖盲区)
- [ ] **发布前链接体检**(写入 `docs/data/daily.json` 前对每条 `source_url` 做一次探活,把静默失效变成显式告警)
- [x] ~~Track A/B 链接失效~~(2026-09-01:还原真实链接的路子已全部排除,改为构造可复现的搜索链接 + 新增 Track C 真实链接源,详见 `workflows/daily-fetch.md` 「链接策略」)

如果有新的需求或发现 bug,直接编辑这个 SKILL.md 文件记录下来。

---

## 重要教训与避坑指南

### ⚠️ 误判：RSSHub 返回 503 不代表服务挂了（2026-09-01）

**问题描述**：
排查时用三个**自己编的路由名**（`/36kr/search/article/robotaxi`、`/gasgoo/news`、`/d1ev/news`）去探活 RSSHub 实例，三个全返回 `503`，据此得出"RSSHub 实例已宕机、20+ 个 Twitter 源全部静默失效"的结论并上报。**结论是错的**，白白让用户去排查一个不存在的故障。

**根本原因**：
RSSHub 对**不存在或加载失败的路由**返回的是 `503 + 欢迎页 HTML`，而不是 `404`。仅凭若干路由 503 无法区分"服务挂了"和"这几个路由不存在"。

**正确的探活方法**（按顺序）：
```bash
# 1. 先探服务本身，不要用业务路由
curl -s -o /dev/null -w "%{http_code}\n" https://<实例>/healthz     # 期望 200 "ok"
curl -s -o /dev/null -w "%{http_code}\n" https://<实例>/             # 期望 200

# 2. 再探一个已知在用的路由
curl -s https://<实例>/twitter/user/waymo | head -c 200              # 期望真实 RSS XML

# 3. 想知道有哪些路由可用，直接问实例自己（不要猜路由名）
curl -s https://<实例>/api/namespace | python -c "import sys,json;print(len(json.load(sys.stdin).get('data',{})))"
```

**结论**：`/healthz` 和 `/api/namespace` 是判断 RSSHub 状态的权威依据。**业务路由 503 只说明那条路由不可用。**

**附带结论**（已验证）：该实例共 1584 个 namespace，**汽车垂直媒体一个都没有**（无 autohome / d1ev / gasgoo / dongchedi），但 36kr / caixin / yicai / tmtpost / jiemian / cls / qbitai / ifeng / sina / sohu 都在。

---

### ⚠️ 关键错误：覆盖 daily.json 导致历史数据丢失（2026-04-23）

**问题描述**：
在执行 Phase 3（daily-publish）时，Claude 直接用 `Write` 工具覆盖了整个 `docs/data/daily.json` 文件，导致所有历史数据（10天的新闻记录）全部丢失。同时还遗漏了 JSON 数组的闭合方括号 `]`，导致 JSON 格式错误，网页无法正常显示。

**根本原因**：
1. **未遵循 daily-publish.md 的规则**：应该先读取现有 JSON，然后插入或替换今日数据，而不是直接覆盖整个文件
2. **Write 工具使用不当**：对于需要追加/更新的 JSON 文件，应该先 Read → 修改 → Write，而不是直接 Write

**正确做法**（完整版见 `workflows/daily-publish.md` 步骤 6）：
```python
import json

entry = {"date": "YYYY-MM-DD", "items": [...]}   # Python dict，引号直接写

with open("docs/data/daily.json", encoding="utf-8") as f:
    data = json.load(f)                          # 进程内读，不进 Claude 上下文，0 token

data = [e for e in data if e["date"] != entry["date"]]   # 重跑则替换
data.insert(0, entry)                                     # 日期倒序，新的在最前

with open("docs/data/daily.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)      # 自动转义，不会出语法错误
```

**防范措施**：
- ✅ **禁止 `Read` 整份 `daily.json`**：现为 1.20MB / 约 34 万 token（近 90 天），且每天涨 14KB。只允许 `Read` 前 10 行确认最新日期，其余交给 Python
- ✅ **Phase 3 不要碰 `daily-archive.json`**：归档由 `roll_daily_archive.py` 维护，发布流程误写会造成日期重叠
- ✅ **禁止用 Edit / Write 手拼 JSON 字符串**：见下方 2026-09-01 的转义事故
- ✅ **写入前后都用 Python 验证**：`python -c "import json;json.load(open('docs/data/daily.json',encoding='utf-8'))"`（不要用 `node -e "require(...)"`，它对语法错误的报错位置不精确）
- ✅ **提交前检查**：确认 git diff 显示的是"新增今日数据"而不是"删除所有历史数据"
- ✅ **备份意识**：重要的数据文件操作前，可以先用 `git show HEAD:path/to/file` 备份

**恢复方法**（如果再次发生）：
```bash
# 1. 从上次提交恢复历史数据
git show HEAD~1:docs/data/daily.json > docs/data/daily_backup.json

# 2. 用 Python 合并新旧数据
python -c "
import json
old = json.load(open('docs/data/daily_backup.json', encoding='utf-8'))
entry = {'date': 'YYYY-MM-DD', 'items': []}   # 今日数据
json.dump([entry] + old, open('docs/data/daily.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
"

# 3. 验证并提交
python -c "import json;d=json.load(open('docs/data/daily.json',encoding='utf-8'));print('OK',len(d),'天')"
git add docs/data/daily.json && git commit -m "fix: 恢复历史数据" && git push
```

---

### ⚠️ 关键错误：用 Edit 手拼 JSON 导致引号未转义、网页全白（2026-09-01）

**问题描述**：
Phase 3 发布时没有走 `daily-publish.md` 步骤 6 的 Python 写法，而是用 `Edit` 工具直接把 JSON 文本拼进 `daily.json`。`summary_html` 里含中文引号的内容（如 `解读为"暗批 Tesla 三隐患"`）原样写入，**引号未转义 → 整份 JSON 语法失效 → 网页一条新闻都显示不出来**。

当时表现具有迷惑性：git push 成功、GitHub 上文件也在，但页面就是空的。连续推了两次（含一次空提交触发重新部署）都没用，因为问题不在部署而在数据。

**根本原因**：
`daily-publish.md` 步骤 6 早就写明「**强制使用 Python 写入，禁止用 Edit 工具直接拼 JSON 字符串**」，原因正是转义。没遵守。

**排查方法**（页面空白但 push 成功时，第一件事就做这个）：
```bash
python -c "import json;json.load(open('docs/data/daily.json',encoding='utf-8'))"
# JSONDecodeError 会直接给出行列号，定位到具体哪条 summary_html
```

**教训**：`json.dump` 存在的意义就是处理转义。只要是往 JSON 里写**模型生成的中文文本**，就必须让序列化库来写，人工/Edit 拼字符串迟早出事。

**影响范围**：
- 网页无法显示任何新闻（JSON 解析失败）
- 历史数据全部丢失（需要从 git 历史恢复）
- 需要额外的修复提交和推送

**总结**：
对于 `docs/data/daily.json` 和 `docs/data/weekly.json` 这类**累积型数据文件**，永远不要直接 `Write` 覆盖，必须先 `Read` → 修改 → `Write`。这是 daily-publish 和 weekly-publish 流程的核心规则。
