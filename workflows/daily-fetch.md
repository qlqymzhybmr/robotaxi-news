# Daily Fetch Workflow

> **目标读者:Claude 本身**。当用户说"跑今日新闻"、"daily fetch"、"跑今天的新闻"时执行这个流程。

---

## 运行前依赖

- 首次运行需安装: `! python -m pip install feedparser`

## 模式判断

用户可能说三种话,对应三种模式:

| 用户说的话 | 模式 | 执行 |
|------|------|------|
| "跑今日新闻" / "daily fetch" / "跑今天的新闻" | **默认**(自动分两阶段)| 依次执行 Phase 1 和 Phase 2,合并到同一份 daily 文件 |
| "只跑国外组" / "daily fetch overseas" | **仅 Phase 1** | 只执行 Phase 1,写入/追加 daily 文件的国外 section |
| "只跑国内组" / "daily fetch china" | **仅 Phase 2** | 只执行 Phase 2,写入/追加 daily 文件的国内 section |

**关键**:无论哪种模式,**都写入同一个文件** `data/daily/YYYY-MM-DD.md`。如果文件已存在,不要覆盖整个文件,**只更新对应 section**(国外 section 或国内 section)。

**抓取入口变更**:
- 召回统一走 Python 抓取器(公司 + 关键词 + 时间窗),不再以 `archive/legacy-fetch/sources.md` 的 tier URL fetch 作为主流程。
- `archive/legacy-fetch/sources.md` 仅作历史归档与兜底参考,默认不执行批量 fetch。

**数据来源（四类）**:
| 来源类型 | 说明 | 配置位置 |
|------|------|------|
| Track B：Google News RSS | 按公司名 + 关键词搜索，覆盖全量媒体报道，但受 Google 权重压制，地方小报容易被淹没 | `competitors.md` 国外/国内公司列表 |
| Track A：本地媒体 site: 查询 | 对每家公司在其运营城市的指定本地媒体发起 `site:xxx.com` 专项查询，绕过 Google 权重，补漏地方 TV 台 / 地方报 | `data/local_media.json` |
| 直接订阅 RSS | 公司官方博客/新闻室 + X(Twitter) via RSSHub | `competitors.md` → `## 直接订阅 RSS` / `## X（Twitter）RSS 订阅` |
| Reddit 社区热帖 | r/SelfDrivingCars、r/Waymo、r/teslamotors；免认证，按 AV 关键词过滤 | `competitors.md` → `## 社区 / 媒体 RSS（Reddit 热帖）` |

**Track A 工作原理**:
- 脚本读取 `data/local_media.json`，对每个 `(公司, 站点)` 组合构建 `"CompanyName" site:outlet.com` 查询
- 相关性判断比 Track B 更宽松：只要公司名出现在标题中即视为相关（不强制要求 AV 技术关键词），因为本地 TV 台标题常用"Waymo vehicle"这类非技术表述
- Track A 和 Track B 结果合并后走统一 URL 去重，同一篇文章只保留一条
- **Track A 仅覆盖国外组**（local_media.json 当前全部是英文媒体）

**`data/local_media.json` 维护规范**:
- 新城市宣布运营 → 立即在对应公司下追加该城市的主报 + 主要 TV 台（至少 2 条）
- site 字段填纯域名，不含 `https://`，例如 `ksat.com`
- 每季度核查一次：各公司是否有新城市；旧条目是否仍有效
- 当前覆盖：Waymo（68 个站点）、Tesla（18）、Aurora（13）、Zoox（7）、Motional（9）、May Mobility（6）

---

## 时间窗口(严格执行)

- 覆盖窗口:**前一日 09:00 ~ 当日 09:00 (北京时间),严格 24 小时**
- **硬规则**:任何新闻的发布日期如果不在这个窗口内,**一律丢弃,不写入 daily 文件**。包括:
  - 比窗口早超过 24 小时的新闻(即使你觉得"重要")
  - 没有明确发布日期、只能猜测的新闻
  - 聚合页里发布日期是去年或几个月前的旧闻
- **不允许**"我觉得这条很重要,虽然是上周的,所以也写进来"。这种判断留给周报阶段,daily 只管 24 小时
- 唯一例外:如果一条新闻昨天发布、但今天才被中文媒体转载,以**原始发布日期**为准。如果原始日期不在窗口内,丢弃

## 抓取时如何过滤(必须执行)

每次 Python RSS 抓取后:
1. **首先解析每条新闻的发布时间**
2. **只保留在时间窗口内的条目**,其他全部丢弃
3. 对于没有清晰发布日期的条目,**默认丢弃**(不要假设是今天)
4. 如果公司返回结果为 0 条或全部超窗,标记"过去 24 小时无相关新闻",**不要硬编**

---

## Phase 1:国外组

### 步骤 1.1:Python 召回（国外公司）

- 执行命令:
  - `! python scripts/python_rss_fetch.py --group overseas --date YYYY-MM-DD --output data/tmp/raw_news_overseas.json`
- 脚本**同时运行 Track B（全局搜索）和 Track A（本地媒体 site: 查询）**，输出合并去重后的同一份 JSON
- 脚本会读取 `competitors.md` 的国外公司清单与 `## 搜索关键词`（Track B），以及 `data/local_media.json`（Track A）
- 抓取规则(基于 Google News RSS):
  - 重点公司(⭐):中英双语各抓,每语种最多 10 条
  - 普通公司:默认英文抓取,每语种最多 5 条(必要时补中文)
- 仅保留时间窗口内新闻,输出标准化 JSON 字段:
  - company
  - title
  - published_at
  - source
  - url
  - summary
  - lang

### 步骤 1.2:Claude 直接读 JSON、去重总结并写入国外 section

- 读取 `data/tmp/raw_news_overseas.json`
- Claude 直接对 JSON 做去重 + 结构化总结,**无需调用外部 API**:
  - URL 归一化去重 + 标题/摘要语义去重
  - 同一事件保留主来源 + 辅助来源
  - 按公司维度整理后,按下方格式**直接写入** `data/daily/YYYY-MM-DD.md` 的国外 section
- 无中间产物文件

**⚠️ 必做：写入前对每条新闻核查真实发布日期**

RSS 的 `pubDate` 不可靠——Google News 会把旧文章重新推到 feed 顶部，`pubDate` 刷新为今天，但文章本身可能是几个月前的。核查步骤：

1. **优先从 URL 中提取日期**：许多文章 URL 包含发布日期，常见格式：
   - `/2026/03/15/`、`/20260315/`、`-2026-03-15-`、`_20260315_`
   - `?date=20260315`、`/2026-03/`
   - 示例：`chejiahao.autohome.com.cn/info/24991288` → 无日期，需看摘要
   - 示例：`techcrunch.com/2026/03/15/waymo-...` → 真实日期 2026-03-15

2. **其次从文章摘要/标题中找日期**：RSS 摘要里通常会提到原文发布时间

3. **判断规则**：
   - 若 URL 或摘要中的日期比 `pubDate` **早超过 3 天** → 以该日期为真实发布日期
   - 若真实发布日期**不在 24 小时窗口内** → **丢弃这条，不写入 daily**
   - 若无法从 URL 和摘要判断日期，且 `pubDate` 在窗口内 → 保留，但写入时注明"日期待核实"

4. **写入 `原始发布日期` 字段时必须是核查后的真实日期**，不能直接复制 RSS `pubDate`

### 格式规范:国外 section（供步骤 1.2 参考）

按以下 markdown 格式写入 `data/daily/YYYY-MM-DD.md` 的 `## 国外 L4` 等 section:

```markdown
# Robotaxi Daily YYYY-MM-DD

## 国外 L4

### Waymo
- [ ] ⭐⭐ **Waymo:X月X日,事件标题一句话。**

  详细内容分 2-3 个段落,每段 2-3 句话,总计 6-8 句话(约 250-320 字)。包含:
  - 第一段:核心事实 + 关键数据(数字、地点、参与方、时间线)
  - 第二段:技术细节或背景信息(为什么做、如何做、影响范围)
  - 第三段(可选):推送计划、行业分析、多源信息补充

  **加粗重点词汇**:日期、产品名、地名、关键数字、核心功能、公司名等事实元素。

  - **原始发布日期**:YYYY-MM-DD(从源页面抓取的真实日期,不是今天的日期)
  - 权威源: [源网站名 日期](url)
  - 辅助源: [源网站名](url)

- [ ] ⭐ **Waymo:另一条新闻...**
  ...

### Tesla
...

### Zoox / Cruise / Wayve / Aurora / Nuro
(过去24h无相关新闻。)

---

## 国外出行平台

### Uber / Lyft / Grab
...

---

## 国外 OEM / Tier1
...
```

**格式要点**:
- 公司名作为 `###` 标题
- 没新闻的公司合并成 `### 公司A / 公司B / 公司C`,下面写 `(过去24h无相关新闻。)`
- 每条新闻第一行是加粗标题(公司名:日期,一句话事件)
- 详细内容分 2-3 段,每段空行分隔,总计 6-8 句话(约 250-320 字)
- 加粗重点词汇:日期、产品名、地名、关键数字、核心功能等事实元素
- **原始发布日期**:YYYY-MM-DD 是必填项(从源页面抓取的真实日期,不是今天的日期)
  - 如果**原始发布日期**不在 24 小时窗口内,这条不应该出现在 daily 文件里。这是自检规则。
- 源链接用 markdown 链接格式

### Reddit 社区热帖（步骤 1.2 补充）

JSON 中 `company` 以 `Reddit/` 开头的条目属于 Reddit 来源，写入方式有所不同：

- **不按公司分组**，而是统一写入国外 section 末尾的独立区块 `## 社区热帖 (Reddit)`
- **来源格式**：`- 权威源: [r/subreddit · Reddit](Reddit帖子链接)`（Reddit 帖链接本身即可，无需找原文）
- **质量判断**（二次过滤，脚本已过滤一次）：
  - 保留：事故/安全事件、立法/监管动态、产品/扩张新闻、有实质内容的社区讨论
  - 跳过：纯调侃帖、个人出行体验、无实质信息的段子
- **摘要格式**：1-2 段，总计 3-5 句，比公司新闻条目短（Reddit 帖通常信息密度较低）
- **原始发布日期**：取 RSS `published_at`，Reddit 帖的发布时间通常可靠

```markdown
## 社区热帖 (Reddit)

- [ ] ⭐ **Reddit/Waymo：X月X日，纳什维尔警察可对 Waymo 开交通罚单——新法正式生效**

  内华达州立法先例后，田纳西州**纳什维尔**通过新法，**警察可对 Waymo 无人车直接开具交通违章罚单**，无需找人类司机。
  这是美国第二个明确赋予执法机构对 Robotaxi 独立执法权的城市级立法，对 Waymo 后续扩张城市具有参考意义。

  - **原始发布日期**：2026-05-12
  - 权威源：[r/Waymo · Reddit](https://www.reddit.com/r/waymo/comments/...)
```

---

## Phase 2:国内组

执行步骤和 Phase 1 对称,差别:

### 步骤 2.1:Python 召回（国内公司）

- 执行命令:
  - `! python scripts/python_rss_fetch.py --group china --date YYYY-MM-DD --output data/tmp/raw_news_china.json`
- 脚本会读取 `competitors.md` 的国内公司清单与 `## 搜索关键词`
- 抓取规则(基于 Google News RSS):
  - 重点公司(⭐):中英双语各抓,每语种最多 10 条
  - 普通公司:默认中文抓取,每语种最多 5 条(必要时补英文)
- 仅保留时间窗口内新闻并输出标准化 JSON

### 步骤 2.2:Claude 直接读 JSON、去重总结并写入国内 section

- 读取 `data/tmp/raw_news_china.json`
- Claude 直接对 JSON 做去重 + 结构化总结,**无需调用外部 API**:
  - URL 归一化去重 + 标题/摘要语义去重
  - 同一事件保留主来源 + 辅助来源
  - 按公司维度整理后,与 Phase 1 相同的格式**直接追加写入** `data/daily/YYYY-MM-DD.md` 的国内 section
- 无中间产物文件

**⚠️ 同 Phase 1：写入前对每条新闻核查真实发布日期（规则同步骤 1.2）**

国内媒体 URL 常见日期格式补充：
- `autohome.com.cn/info/XXXXXXXX`（无日期，需从摘要判断）
- `mp.weixin.qq.com/s/...`（无日期，从标题或摘要找）
- `36kr.com/p/XXXXXXXXXX`（无日期）
- `cls.cn/detail/XXXXXXX`（无日期，从内容找）
- `sina.com.cn/.../YYYY-MM-DD/...`（有日期）

对于**无法从 URL 提取日期**的国内媒体链接（微信公众号、汽车之家车家号等），必须从摘要文本中找到文章提到的日期，与 `pubDate` 对比。若摘要中提到的事件发生时间比今天早超过 7 天，大概率是旧文重推，**丢弃**。

---

## 最终文件结构

完整的 daily 文件应该长这样:

```markdown
# Robotaxi Daily YYYY-MM-DD

> 覆盖窗口:前一日 09:00 ~ 当日 09:00(北京时间)
> 运行模式:默认(Phase 1 + Phase 2) / 仅国外组 / 仅国内组

## 国外 L4
...

## 国外出行平台
...

## 国外 OEM / Tier1 / 自动驾驶技术公司
...

## 社区热帖 (Reddit)
(来自 r/SelfDrivingCars、r/Waymo、r/teslamotors，过滤后仅保留有新闻价值的帖子)
...

---

## 国内 L4
...

## 国内出行平台
...

## 国内新势力 / 传统 OEM
...

## 国内智驾方案商
...

## 国内华为系 / 互联网大厂
...

---

## ⚠️ 抓取失败列表
(如果有公司抓取失败,列在这里)
- Company A : timeout / parse error
- ...

## 📊 本次运行统计
- 模式:默认 / 仅国外组 / 仅国内组
- Phase 1 耗时:X 分钟
- Phase 2 耗时:Y 分钟
- 总公司抓取次数:N
- 抓到新闻数:X 条(国外 A + 国内 B)
- 去重后新闻数:Y 条
- 评级分布:⭐⭐⭐ x 条,⭐⭐ x 条,⭐ x 条
```

---

## 失败与恢复

### 中途中断
- 如果 Phase 1 完成后中断(比如额度限制),下次用户可以说"只跑国内组"补跑 Phase 2
- 写入时**不要覆盖已有的国外 section**,只追加国内 section

### Fetch 失败容忍
- 单个 URL fetch 失败:记录,继续
- 连续 3 个 URL fetch 失败:提示用户网络可能有问题,询问是否继续
- 同一个公司连续 3 天抓取失败:在日志中明确提示 "必要时启用 archive/legacy-fetch/sources.md 做应急补漏"

### Twitter Auth Token 失效检测
读取 JSON 后，检查 `errors` 列表中是否含有 `TWITTER_AUTH_EXPIRED` 字样：
- **有**：在 daily 文件末尾 ⚠️ 区域用醒目格式提示：
  ```
  ⚠️ **[紧急] Twitter Auth Token 已失效！**
  请立即到 Railway → rsshub 服务 → Variables → 更新 `TWITTER_AUTH_TOKEN` 的值。
  步骤：DevTools → Application → Cookies → x.com → 复制 auth_token 的 Value。
  ```
- **无**：正常继续，无需提示

### 搜索结果不足
- 如果某家公司搜索返回 0 结果,不要重试,直接标记为"无相关新闻"
- 如果搜索返回结果但日期都不在窗口内,同样标记"无相关新闻"

---

## Phase 3:自动发布到网页（自动执行）

Phase 2 完成后,**不等用户说话**,直接按 `workflows/daily-publish.md` 的流程执行发布。

执行完成后,统一向用户报告 Phase 1 + Phase 2 + Phase 3 的结果。

**Daily 与 Weekly 职责划分**:
- Daily（Phase 3 / daily-publish）:Claude 按 rating ≥ 2 自动筛选并发布到网页
- Weekly（weekly-report）:按用户手动勾选 `[x]` 生成周报并发布到网页
- 两者互不覆盖,Daily 发布不会改变 daily 文件里的勾选状态

---

## Phase 4：Uber CEO 访谈提醒（自动执行）

Phase 3 完成后，**立即执行**以下搜索，无需用户手动触发。

### 目标

搜索 Uber CEO Dara Khosrowshahi 近期的对外访谈。不限平台（YouTube、Podcast、媒体专访均算）。

### 搜索关键词（轮流尝试，至少用前两组）

1. `"Dara Khosrowshahi" interview 2026`
2. `"Uber CEO" podcast interview 2026`
3. `Dara Khosrowshahi podcast OR talk OR conversation`

### ⚠️ 强制日期核实（绝不跳过）

搜索结果只是线索，**不能依靠搜索摘要或页面框架时间来判断内容是否在 14 天内**。每条候选结果必须执行以下步骤：

**YouTube 视频：**
- 必须用 WebFetch 打开该 YouTube 页面（或用 WebSearch 搜索该视频标题），确认视频标题下方显示的**上传日期**（如 "3 days ago"、"Jun 25, 2026"）
- 不能以搜索摘要里出现"2026"就认为是新内容

**Podcast 单集：**
- 必须打开该 Podcast 单集页面（节目官网、Spotify、Apple Podcasts 等），确认单集本身的**发布日期**
- 不能以所在节目仍在更新为由认为该集是新的

**现场活动 / 大会（如 Aspen Ideas、TED、DealBook 等）：**
- 必须找到**该场次**的具体日期（不是大活动的整体时间范围）
- 若找不到场次具体日期，**不能标记为新内容**

**文字采访 / Transcript：**
- 必须从文章页面确认文章发布日期（通常显示在标题下方或文末）
- 不能以文章 URL 中出现当年年份就认为是近期

**核实失败的处理：**
- 无法确认具体发布日期 → 不写入提醒，不提示用户
- 可以确认日期但超过 14 天 → 不写入提醒，不提示用户

### 判断是否有新内容

仅当**经过上述核实、确认发布日期距今 ≤ 14 天**后，才算有新访谈。同时满足：

- 跳过：新闻报道、公司公告、二手引用、公司 PR 稿
- 保留以下任意形式：
  - YouTube 视频、Podcast 单集、现场演讲录像
  - 文字采访（媒体记者对话形式，如 The Verge、Semafor、Bloomberg 等）
  - 音频/视频访谈配套发布的 Transcript 文本（通常在节目官网或 Substack）

### 有新访谈时

在 `data/daily/YYYY-MM-DD.md` 文件**末尾另起一段**，追加：

```markdown
---

## Uber CEO 访谈提醒

- **节目/平台**：节目名称（如 Decoder with Nilay Patel / Invest Like the Best）
- **发布日期**：YYYY-MM-DD（已核实的真实发布日期）
- **链接**：[标题](url)
- **时长**：约 XX 分钟（如已知）
- **摘要**：一句话概括访谈主题，例如：讨论 Uber Robotaxi 战略、自动驾驶合作伙伴关系、未来城市出行。
```

如果本次搜索有**多个新访谈**，每个写一个列表条目。

### 无新访谈时

不追加任何内容，不提示，继续执行结束动作。

---

## 结束动作

Phase 1 + Phase 2 + Phase 3 + Phase 4 全部完成后,统一告诉用户:

```
今日 daily 抓取完成:
- 共 X 条新闻(⭐⭐⭐ x 条 / ⭐⭐ x 条 / ⭐ x 条),写入 data/daily/YYYY-MM-DD.md
- 自动发布:X 条已写入 docs/data/daily.json
- Uber CEO 访谈:有新访谈 / 无新内容

请用 VS Code 打开 data/daily/YYYY-MM-DD.md,把认为重要的条目 [ ] 改成 [x]（供 weekly 使用）。
发布网页请运行:git add -A && git commit -m "daily YYYY-MM-DD" && git push
```

如果有 fetch 失败,补充提示:"注意:X 个 URL fetch 失败,请检查文件末尾的 ⚠️ 列表"
