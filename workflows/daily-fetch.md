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

---

## 时间窗口(严格执行)

- 覆盖窗口:**前一日 10:00 ~ 当日 10:00 (北京时间),严格 24 小时**
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
- 脚本会读取 `competitors.md` 的国外公司清单与 `## 搜索关键词`
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

### 步骤 1.2:按公司聚合 + 评级

- 读取 `data/tmp/raw_news_overseas.json`
- 执行 Claude 去重与结构化总结:
  - `! python scripts/claude_structured_summary.py --input data/tmp/raw_news_overseas.json --output-md data/tmp/summary_overseas.md --output-json data/tmp/summary_overseas.json --date YYYY-MM-DD`
  - 本地联调可加 `--mock`（不调用 API）
- 去重与理解规则:
  - URL 归一化去重 + 标题/摘要语义去重
  - 同一事件保留主来源 + 辅助来源
  - 生成公司维度结构化结果,用于写入 daily section

### 步骤 1.5:写入 daily 文件的国外 section

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

### 步骤 2.2 + 2.3:聚合、评级、写入
- 读取 `data/tmp/raw_news_china.json`
- 执行 Claude 去重与结构化总结:
  - `! python scripts/claude_structured_summary.py --input data/tmp/raw_news_china.json --output-md data/tmp/summary_china.md --output-json data/tmp/summary_china.json --date YYYY-MM-DD`
  - 本地联调可加 `--mock`（不调用 API）
- 同 Phase 1 步骤 1.2-1.5,写入 daily 文件的 `## 国内 L4`、`## 国内主机厂`、`## 国内智驾方案商` 等 section。

---

## 最终文件结构

完整的 daily 文件应该长这样:

```markdown
# Robotaxi Daily YYYY-MM-DD

> 覆盖窗口:前一日 10:00 ~ 当日 10:00(北京时间)
> 运行模式:默认(Phase 1 + Phase 2) / 仅国外组 / 仅国内组

## 国外 L4
...

## 国外出行平台
...

## 国外 OEM / Tier1 / 自动驾驶技术公司
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

## 结束动作

Phase 1 + Phase 2 + Phase 3 全部完成后,统一告诉用户:

```
今日 daily 抓取完成:
- 共 X 条新闻(⭐⭐⭐ x 条 / ⭐⭐ x 条 / ⭐ x 条),写入 data/daily/YYYY-MM-DD.md
- 自动发布:X 条(⭐⭐+)已写入 docs/data/daily.json

请用 VS Code 打开 data/daily/YYYY-MM-DD.md,把认为重要的条目 [ ] 改成 [x]（供 weekly 使用）。
发布网页请运行:git add -A && git commit -m "daily YYYY-MM-DD" && git push
```

如果有 fetch 失败,补充提示:"注意:X 个 URL fetch 失败,请检查文件末尾的 ⚠️ 列表"
