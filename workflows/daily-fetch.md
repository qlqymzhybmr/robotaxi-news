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

**数据来源（五类，全部并存，一次运行同时跑完）**:
| 来源类型 | 说明 | 链接质量 | 配置位置 |
|------|------|------|------|
| Track B：Google News RSS | 按公司名 + 关键词搜索，覆盖全量媒体报道，但受 Google 权重压制，地方小报容易被淹没 | ⚠️ 搜索链接（见下方「链接策略」） | `competitors.md` 国外/国内公司列表 |
| Track A：本地媒体 site: 查询 | 对每家公司在其运营城市的指定本地媒体发起 `site:xxx.com` 专项查询，绕过 Google 权重，补漏地方 TV 台 / 地方报 | ⚠️ 搜索链接 | `data/local_media.json` |
| Track C：行业媒体 RSS | 综合财经/科技/汽车媒体大盘源（Electrek、CnEVPost、36氪、财新、华尔街见闻…），**必过主题关键词** | ✅ 发布方真实永久链接 | `competitors.md` → `## 行业媒体 RSS` |
| 直接订阅 RSS | 公司官方博客/新闻室 + X(Twitter) via RSSHub | ✅ 发布方真实永久链接 | `competitors.md` → `## 直接订阅 RSS` / `## X（Twitter）RSS 订阅` |
| Reddit 社区热帖 | r/SelfDrivingCars、r/Waymo、r/teslamotors；免认证，按 AV 关键词过滤 | ✅ Reddit 帖真实链接 | `competitors.md` → `## 社区 / 媒体 RSS（Reddit 热帖）` |

**Track C 工作原理（2026-09-01 新增）**:
- 与「直接订阅 RSS」的关键差别：公司新闻室条条相关，**不过滤**；Track C 是综合大盘源，绝大多数内容与自动驾驶无关，**每条必须命中 `MEDIA_TOPIC_KEYWORDS`**（定义在 `scripts/python_rss_fetch.py`）才进入管线。约 350 条原始条目 → 过滤后约 15 条。
- 解析靠 section 标题区分：`FILTERED_FEED_SECTIONS` 里的 section 打 `filtered=True`，其余走原逻辑。**两种模式完全并存，Track A / Track B 行为未做任何改动。**
- Track C 的独特价值有两点，都不是 Track B 能替代的：
  1. **链接质量**：返回发布方真实永久 URL，不经 Google News 包装，不存在过期/搜不到问题
  2. **补公司无关的新闻**：Track B 是按公司名检索的，**监管/政策类新闻往往不含任何公司名，会被结构性漏掉**。实测 2026-08-31「商务部等三部门发布车联网及自动驾驶数据合规指引」就是只有 Track C 抓到（36氪 + 华尔街见闻 + 界面 三源命中），Track B 全部漏掉。
- ⚠️ RSSHub **没有汽车垂直媒体路由**（汽车之家 / 第一电动 / 盖世汽车 / 懂车帝 / 车东西均不存在），这部分仍只能靠 Track B 搜索召回。

---

## 链接策略（source_url 怎么来的，为什么有两种）

写 daily 和 daily.json 时，`url` 字段有两种形态，**要能分辨**：

**① 真实永久链接**（Track C / 直接订阅 / Reddit）
形如 `https://electrek.co/2026/08/31/tesla-driver-assist-stopped-freeway-mesa/`。直接用，最优。

**② 搜索链接**（Track A / Track B）
形如 `https://www.google.com/search?q="标题" site:electrek.co`。

**为什么不能给真实链接**：Google News RSS 返回的是 `CBMi…/AU_yqL…` 包装 URL，几天后失效。已实测排除全部还原方案——base64 解码（新格式解不出）、Google `batchexecute` 私有接口（4.9 秒/条且返回值已无 URL）、302 跳转（只跳到另一个包装）、Bing News RSS（已废弃）、DuckDuckGo（限流且有假阳性）。**这条路是死的，不要再试。**

**因此搜索词按"结果可复现"来构造**（`_make_search_url()`）：
1. 去掉 Google 给每条标题追加的 ` - 发布方` 后缀（纯噪音）
2. 标题加引号做精确短语匹配，避免松散关键词的排序漂移
3. 已知发布方域名时加 `site:` 限定，防止转载版和同题文章抢排名
4. **用 `www.google.com` 网页搜索，不用 `news.google.com`** —— 新闻索引有时效衰减，几个月后旧文会掉出索引，这正是归档链接慢慢失效的原因；网页索引会长期保留
5. 中文走百度且**不加 `site:`** —— 国内转载极多、百度对 UGC 子域收录不稳，加了经常零结果；不限定反而稳定能找到同一篇的某个副本

**优先级**：同一事件如果 Track C 和 Track B 都抓到，**优先采用 Track C 的真实链接**作为权威源，Track B 的搜索链接降为辅助源。

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
- ⭐⭐ **Waymo:X月X日,事件标题一句话。**

  详细内容分 2-3 个段落,每段 2-3 句话,总计 6-8 句话(约 250-320 字)。包含:
  - 第一段:核心事实 + 关键数据(数字、地点、参与方、时间线)
  - 第二段:技术细节或背景信息(为什么做、如何做、影响范围)
  - 第三段(可选):推送计划、行业分析、多源信息补充

  **加粗重点词汇**:日期、产品名、地名、关键数字、核心功能、公司名等事实元素。

  - **原始发布日期**:YYYY-MM-DD(从源页面抓取的真实日期,不是今天的日期)
  - 权威源: [源网站名 日期](url)
  - 辅助源: [源网站名](url)

- ⭐ **Waymo:另一条新闻...**
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

### ⭐ 评级标准（2026-09-02 起由 Claude 自行判断，不再人工勾选）

原先的「实习生逐条把 `[ ]` 改成 `[x]`」流程**已取消**。评级现在就是重要性判断本身，请按下表打分：

| 评级 | 含义 | 典型例子 |
|------|------|------|
| ⭐⭐⭐ | 改变竞争格局或需要向上汇报 | 开城/开服、重大事故与监管处罚、财报与关键财务拐点、重大合作与并购、技术路线级发布 |
| ⭐⭐ | 值得知道，但不改变判断 | 功能更新、区域小幅扩张、高管公开表态、供应链动向、单一分析师观点 |
| ⭐ | 存疑或边缘 | 未经证实的传闻、二手转述、纯股价波动、社区讨论帖 |

**⚠️ 两条硬规则，防止过度筛选：**

1. **拿不准就往高了给，不要往低了给。** 漏掉一条真新闻的代价，远大于多留一条普通新闻。
2. **⭐ 也必须写进 daily 文件、也必须发布**。低评级 ≠ 不写。评级只影响阅读优先级，不是过滤器——真正的筛选发生在周报选稿阶段。

不要因为「感觉不够重要」就在写入前丢弃条目：只要在 24 小时窗口内、且与自动驾驶相关，就应该出现在 daily 里。

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

- ⭐ **Reddit/Waymo：X月X日，纳什维尔警察可对 Waymo 开交通罚单——新法正式生效**

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
- Daily（Phase 3 / daily-publish）:**全量**发布到网页，**不按 rating 过滤**。低评级条目被跳过会导致它在选稿 UI 里根本不出现
- Weekly（weekly-report）:按网页选稿 UI 保存到 `docs/data/selections.json` 的选择生成周报
- 两者互不覆盖

---

## Phase 4：Uber CEO 访谈提醒（自动执行）

Phase 3 完成后，**立即执行**以下搜索，无需用户手动触发。

### 目标

搜索 Uber CEO Dara Khosrowshahi 近期的对外访谈。

**⚠️ 这个提醒独立于 daily，不写进 `data/daily/YYYY-MM-DD.md`**，而是在最终回复里单独成一块告诉用户。理由：它不是当日新闻，也不进周报，混进 daily 文件只会干扰阅读。

### 平台覆盖（都要查，不只是 YouTube）

| 平台 | 查法 |
|---|---|
| YouTube | `site:youtube.com "Dara Khosrowshahi"` + WebSearch |
| Spotify | `site:open.spotify.com "Dara Khosrowshahi"` |
| Apple Podcasts | `site:podcasts.apple.com "Dara Khosrowshahi"` |
| 媒体专访 / Transcript | 关键词搜索，见下 |
| 现场活动 / 大会 | 关键词搜索，见下 |

### 搜索关键词（轮流尝试，至少用前三组）

1. `"Dara Khosrowshahi" interview 2026`
2. `"Uber CEO" podcast interview 2026`
3. `"Dara Khosrowshahi" site:open.spotify.com OR site:podcasts.apple.com`
4. `Dara Khosrowshahi podcast OR talk OR conversation`

### 去重：查台账，只提醒没提醒过的

读 `data/uber_ceo_interviews.json`：

- `seen` 数组里**已有相同 `url`** 的 → **跳过，不再提醒**（否则同一期访谈会天天弹）
- 不在里面的 → 走下面的日期核实；确认是新访谈后**提醒用户，并把它追加进 `seen`**

追加时用 Python 写入（同 daily.json 的理由，避免手拼 JSON 出转义错）：

```python
import json, datetime
p = "data/uber_ceo_interviews.json"
d = json.load(open(p, encoding="utf-8"))
d["seen"].append({
    "url": "...", "title": "...", "platform": "YouTube",
    "published_at": "2026-08-28",
    "first_seen": datetime.date.today().isoformat(),
})
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

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

**不写进 daily 文件**。改为两件事：

1. 追加进 `data/uber_ceo_interviews.json` 的 `seen`（去重台账，见上）
2. 在最终回复里**单独成一块**告诉用户：

```markdown
## 🎙️ Uber CEO 访谈提醒（1 条新内容）

- **节目/平台**：Decoder with Nilay Patel（YouTube）
- **发布日期**：2026-08-28（已核实：视频页显示 "4 days ago"）
- **链接**：[标题](url)
- **时长**：约 52 分钟
- **摘要**：一句话概括访谈主题，例如讨论 Uber Robotaxi 战略、与 Waymo/小马智行的平台合作、未来城市出行。
```

多条就每条一个区块。**日期后面要注明是怎么核实的**（"视频页显示 4 days ago"、"单集页标注 Aug 28, 2026"），便于用户判断可信度。

### 无新访谈时

不提示，不写任何文件。结束动作里用一行带过即可（见下）。

---

## Phase 5：抓取源健康告警（自动执行）

Phase 4 完成后执行。目的：**抓取源静默失效是最危险的故障** —— 凭证过期、路由下线、被封 IP，这些都不会报错，只会让某个源"今天恰好没新闻"，可能几周没人发现。

### 数据来源

脚本已经在输出 JSON 的**顶层 `health` 字段**里做好了分级，直接读，不要自己重新解析 `errors`：

```json
{
  "health": {
    "ok": false,
    "alerts": [
      { "level": "critical", "type": "TWITTER_AUTH_EXPIRED", "count": 22,
        "what": "X(Twitter) 抓取凭证已失效…", "action": "到 Railway → …", "sources": ["…"] }
    ],
    "silent_feeds": ["IT之家"],
    "missing_feeds": [],
    "checked_feeds": 45
  }
}
```

命令行末尾也会打印同样的信息（`health=OK` 或 `health=NEEDS_ATTENTION` + 明细）。

### 播报规则

读 Phase 1 和 Phase 2 两份 JSON 的 `health`，**合并后**判断：

| 情况 | 怎么做 |
|---|---|
| 两份都 `ok: true` | 结束动作里一行带过：`抓取源健康：正常（N 个源）`，不展开 |
| 有 `level: critical` | **在最终回复最顶部**用 🚨 单独成块，把 `what` 和 `action` 原样告诉用户。这类问题只有用户能修，压在报告底部等于没说 |
| 只有 `level: warning` | 结束动作里列一行，不单独成块 |
| `silent_feeds` 非空 | 列出来，并说明"请求成功但返回 0 条，疑似上游改版或路由失效，连续 2 天出现就该查了" |
| `missing_feeds` 非空 | 列出来（通常意味着脚本中途异常退出） |

### critical 告警格式

```markdown
🚨 **抓取源故障：需要你处理**

**X(Twitter) 抓取凭证已失效**，22 个 X 源当前抓不到任何内容。
→ 到 Railway → rsshub 服务 → Variables 更新 `TWITTER_AUTH_TOKEN`。
   取值：浏览器 DevTools → Application → Cookies → x.com → 复制 auth_token 的 Value
```

### ⚠️ 不要做的事

- **不要因为健康告警就中止发布**。抓到多少发多少，告警是附加信息
- **不要把告警写进 daily 文件**。它不是新闻，会干扰阅读
- **不要自己"猜"某个源是不是坏了**。只播报 `health` 里有的，`raw_counts` 为 0 才算静默，"今天没新闻"不是故障

---

## 结束动作

Phase 1 ~ Phase 5 全部完成后,统一告诉用户。

**顺序很重要**：如果有 `critical` 健康告警，它排在**最前面**，因为那是唯一需要用户动手的事；其余按下面的模板。

```
🚨 （仅当有 critical 告警时，按 Phase 5 的格式放在最顶部）

今日 daily 抓取完成:
- 共 X 条新闻(⭐⭐⭐ x 条 / ⭐⭐ x 条 / ⭐ x 条),写入 data/daily/YYYY-MM-DD.md
- 自动发布:X 条已写入 docs/data/daily.json
- 抓取源健康:正常（N 个源）/ N 个警告,详见上方
- Uber CEO 访谈:无新内容 / 见下方单独区块

发布网页请运行:git add -A && git commit -m "daily YYYY-MM-DD" && git push

## 🎙️ Uber CEO 访谈提醒（仅当有新内容时，按 Phase 4 的格式单独成块）
```

如果有 fetch 失败,补充提示:"注意:X 个 URL fetch 失败,请检查文件末尾的 ⚠️ 列表"

---

## 定期维护（不是每天，但别忘）

这几件事不在每日流程里，但放着不管会慢慢劣化：

| 事项 | 频率 | 命令 / 做法 |
|------|------|------|
| **滚动 daily 归档** | 约每月，或 daily.json 超过 100 天时 | `python scripts/roll_daily_archive.py --apply`（默认保留近 90 天，脚本对条目数做守恒校验，不一致会拒绝写入） |
| **压缩周报图片** | 每次周报贴过新图之后 | `python scripts/compress_weekly_images.py --apply`（幂等，已是 WebP 的会跳过） |
| **核查 local_media.json** | 每季度 | 各公司是否有新运营城市；旧站点是否还有效 |
| **复查静默源** | 当 Phase 5 连续 2 天报同一个源 | 手动打开该 feed URL 确认是上游改版还是路由下线 |

**为什么图片压缩要定期做**：网页的粘贴路径仍然是 `FileReader.readAsDataURL`，贴进去的新图还是未压缩 PNG。2026-09-01 时两张图就把 `weekly_overrides.json` 撑到 1.56MB、实际传输 1181KB，占了全站首屏的 61%。
