# Daily Fetch Workflow

> **目标读者:Claude 本身**。当用户说"跑今日新闻"、"daily fetch"、"跑今天的新闻"时执行这个流程。

---

## 模式判断

用户可能说三种话,对应三种模式:

| 用户说的话 | 模式 | 执行 |
|------|------|------|
| "跑今日新闻" / "daily fetch" / "跑今天的新闻" | **默认**(自动分两阶段)| 依次执行 Phase 1 和 Phase 2,合并到同一份 daily 文件 |
| "只跑国外组" / "daily fetch overseas" | **仅 Phase 1** | 只执行 Phase 1,写入/追加 daily 文件的国外 section |
| "只跑国内组" / "daily fetch china" | **仅 Phase 2** | 只执行 Phase 2,写入/追加 daily 文件的国内 section |

**关键**:无论哪种模式,**都写入同一个文件** `data/daily/YYYY-MM-DD.md`。如果文件已存在,不要覆盖整个文件,**只更新对应 section**(国外 section 或国内 section)。

---

## 时间窗口

- 默认覆盖**过去 24 小时**,即 `前一日 10:00 ~ 当日 10:00`(北京时间)
- 文件名用**当日日期**,例如 2026-04-10 上午 10 点跑就写入 `data/daily/2026-04-10.md`
- 新闻筛选时,保留发布时间在窗口内的,**允许 ±6 小时宽裕**(防止时区问题漏查)
- 如果发现重要新闻是 24-48 小时前的且 Long 之前的 daily 里没记录,**作为"滞后新闻"标注后仍然保留**

---

## Phase 1:国外组

### 步骤 1.1:Fetch Tier 1 英文聚合页

按 `sources.md` 里 **Tier 1 英文/全球** 板块和 **Tier 1 中英双语** 板块列出的 URL,依次 `web_fetch`:

- 每个 URL fetch 后,从结果中提取:
  - 标题
  - 发布日期(过滤出时间窗口内的)
  - 涉及的公司名(对照 `competitors.md` 判断属于国外组还是国内组)
  - 新闻主体内容
  - **候选图片 URL**(如果页面有配图)

- **Fetch 失败处理**:
  - 记录到临时变量 `fetch_fails_phase1`
  - 不中断流程,继续下一个 URL
  - 最后写入 daily 文件末尾的 `⚠️ Fetch 失败列表` 区块

### 步骤 1.2:Fetch Tier 2 国外官方源

按 `sources.md` 里 **Tier 2 Robotaxi 头部公司官方** 和 **Tier 2 Tesla 专门追踪** 板块列出的 URL,依次 `web_fetch`。处理方式同 1.1。

### 步骤 1.3:识别"白名单未覆盖的国外公司"

- 统计步骤 1.1 和 1.2 已经 fetch 到的新闻涉及哪些国外公司
- 对照 `competitors.md` 的**国外组**,找出**没被覆盖到的公司**
- 对这些"沉默的国外公司",按以下策略做 `web_search`:
  - **重点公司**(带 ⭐):中英双语各搜 1 次
    - 英文查询:`{公司名} news {月份 日期, 年}`,例如 `Zoox news April 10, 2026`
    - 中文查询:`{公司名中文} 最新`,例如 `Zoox 最新`
  - **普通公司**(无 ⭐):单次英文搜索即可
    - `{公司名} {月份 日期, 年}`

- **搜索关键词注意事项**:
  - 不要加 `site:` operator
  - 不要加引号 `""`
  - 关键词 3-6 个词最佳
  - 今日日期(2026-04-10 这种格式)写年份避免返回旧新闻

### 步骤 1.4:按公司聚合 + 评级

- 把 1.1、1.2、1.3 抓到的所有新闻**按公司分组**
- 对每条新闻打 ⭐ 评级,参考 `important-examples.md` 的规则
- 去重:同一事件可能被多个源报道,只保留一条(优先保留有权威源的那条)

### 步骤 1.5:写入 daily 文件的国外 section

按以下 markdown 格式写入 `data/daily/YYYY-MM-DD.md` 的 `## 国外 L4` 等 section:

```markdown
# Robotaxi Daily YYYY-MM-DD

## 国外 L4

### Waymo
- [ ] ⭐⭐ **Waymo:X月X日,事件标题一句话。**
  详细内容 2-3 句,包含关键数字、地点、参与方、背景。
  候选图:<图片 URL 如果有>
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
- 每条新闻第一行是加粗标题(公司名:日期,一句话事件),第二行是详细内容
- 候选图 URL 独立一行,前缀 `候选图:`,方便 weekly-report 读取
- 源链接用 markdown 链接格式

---

## Phase 2:国内组

执行步骤和 Phase 1 完全对称,差别:

### 步骤 2.1:Fetch Tier 1 中文 & 中英双语聚合页
按 `sources.md` 里 **Tier 1 中文** 板块 + **Tier 1 中英双语**(如果 Phase 1 没 fetch 过,或者需要补充国内相关内容)

### 步骤 2.2:Fetch Tier 2 中国公司官方源
按 `sources.md` 里 **Tier 2 中国公司官方** 板块

### 步骤 2.3:识别"白名单未覆盖的国内公司"
对照 `competitors.md` 的**国内组**,搜索没覆盖到的公司:
- 重点公司(带 ⭐):中英双语各 1 次
- 普通公司:中文 1 次

搜索关键词示例:
- `小鹏 智驾 4月10日`
- `理想汽车 最新`
- `Horizon Robotics news`(重点公司英文)

### 步骤 2.4 + 2.5:聚合、评级、写入
同 Phase 1 步骤 1.4-1.5,写入 daily 文件的 `## 国内 L4`、`## 国内主机厂`、`## 国内智驾方案商` 等 section。

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

## ⚠️ Fetch 失败列表
(如果有 URL fetch 失败,列在这里)
- https://xxx.com/yyy : 403 Forbidden
- ...

## 📊 本次运行统计
- 模式:默认 / 仅国外组 / 仅国内组
- Phase 1 耗时:X 分钟
- Phase 2 耗时:Y 分钟
- 总 fetch 次数:N
- 总 search 次数:M
- 抓到新闻数:X 条(国外 A + 国内 B)
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
- 同一个源连续 3 天 fetch 失败:在日志中明确提示 "建议在 sources.md 中把 X 加上 `# DISABLED:` 前缀"

### 搜索结果不足
- 如果某家公司搜索返回 0 结果,不要重试,直接标记为"无相关新闻"
- 如果搜索返回结果但日期都不在窗口内,同样标记"无相关新闻"

---

## Phase 3:自动发布到网页(线 A,自动执行)

Phase 2 完成后,**不等用户说话**,直接按 `workflows/daily-publish.md` 的流程执行发布。

执行完成后,统一向用户报告 Phase 1 + Phase 2 + Phase 3 的结果。

**线 A 和线 B 完全独立**:
- 线 A(Phase 3 / daily-publish):Claude 自己按 rating ≥ 2 自动筛选并发布到网页
- 线 B(周报人工流程):实习生手动勾选 `[x]`,周一生成 OneNote 周报
- 两者互不影响,线 A 发布不会改变 daily 文件里的勾选状态

---

## 结束动作

Phase 1 + Phase 2 + Phase 3 全部完成后,统一告诉用户:

```
今日 daily 抓取完成:
- 共 X 条新闻(⭐⭐⭐ x 条 / ⭐⭐ x 条 / ⭐ x 条),写入 data/daily/YYYY-MM-DD.md
- 线 A 自动精选:X 条(⭐⭐+)已写入 docs/data/daily.json

请用 VS Code 打开 data/daily/YYYY-MM-DD.md,把认为重要的条目 [ ] 改成 [x]。(线 B 周报流程)
发布网页请运行:git add -A && git commit -m "daily YYYY-MM-DD" && git push
```

如果有 fetch 失败,补充提示:"注意:X 个 URL fetch 失败,请检查文件末尾的 ⚠️ 列表"
