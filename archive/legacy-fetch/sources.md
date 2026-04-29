# 信息源白名单

> **维护说明**：这里列出的 URL 是 daily-fetch 时**强制 web_fetch 的页面**。
> 这些应该是**按时间倒序的新闻列表页**，而不是单篇文章 URL。fetch 一次能拿到当天最新 10-30 条标题。
> 如果某个源经常出错或质量下降，在 URL 前加 `# DISABLED:` 前缀临时禁用。
>
> **使用规则**：
> - **daily-fetch 默认拆分模式**时：
>   - Phase 1（国外组）：fetch Tier 1 英文源 + Tier 2 国外官方源
>   - Phase 2（国内组）：fetch Tier 1 中文源 + Tier 2 国内官方源
>   - CnEVPost 和 Gasgoo 是中英双语，两个 phase 都会涉及

---

## Tier 1 - 核心新闻聚合页（必 fetch）

### 英文 / 全球科技与交通（Phase 1）
- https://techcrunch.com/category/transportation/
  - 备注：TechCrunch transportation 频道，覆盖 Waymo / Tesla / Zoox / Uber 全套
- https://electrek.co/guides/autonomous-vehicles/
  - 备注：Electrek 自动驾驶 tag，对 Tesla FSD 报道密集
- https://www.theverge.com/transportation
  - 备注：The Verge transportation 频道
- https://www.reuters.com/business/autos-transportation/
  - 备注：Reuters 汽车交通频道，权威新闻源
- https://www.autoblog.com/category/autonomous-driving/
  - 备注：Autoblog 自动驾驶频道

### 英文 / 付费墙源（尝试 fetch，失败则跳过）
- https://www.theinformation.com/topics/transportation
  - 备注：The Information 交通频道。**部分付费墙**，fetch 可能只能拿到摘要

### 中英双语 / 中国视角英文报道（Phase 1 + Phase 2 都跑）
- https://cnevpost.com/self-driving/
  - 备注：**最重要的单一信源**。英文写中国 EV/自动驾驶，更新非常快，英文媒体常引用
- https://cnevpost.com/
  - 备注：CnEVPost 首页，补充 self-driving 之外的其他相关新闻
- https://www.scmp.com/topics/autonomous-driving
  - 备注：南华早报自动驾驶专题，覆盖中国和亚洲市场
- https://autonews.gasgoo.com/
  - 备注：盖世汽车 news（中英双语，对中国出海动态覆盖好）

### 中文 / 中国汽车媒体（Phase 2）
- https://36kr.com/information/travel/
  - 备注：36氪汽车频道
- https://m.thepaper.cn/list_25950
  - 备注：澎湃新闻汽车频道

---

## Tier 2 - 公司官方源（必 fetch）

### Robotaxi 头部公司官方（Phase 1）
- https://waymo.com/blog/
  - 备注：Waymo 官方博客，开城/技术发布最权威
- https://zoox.com/journal/
  - 备注：Zoox 官方 Journal 博客
- https://wayve.ai/thinking/
  - 备注：Wayve 官方博客
- https://www.prnewswire.com/news/pony-ai-inc/
  - 备注：Pony.ai 官方 PR Newswire 页面
- https://ir.weride.ai/news-releases
  - 备注：WeRide 官方 IR 新闻发布页

### Tesla 专门追踪（Phase 1，社区/泄露源为主）
- https://www.teslarati.com/category/news/
  - 备注：Teslarati Tesla 新闻
- https://www.notateslaapp.com/
  - 备注：Tesla 软件更新追踪，FSD 版本推送第一手信息

### 中国公司官方（Phase 2）
- https://www.apollo.auto/
  - 备注：百度 Apollo 官网（萝卜快跑母品牌）
- https://www.robotgo.com/
  - 备注：萝卜快跑官网

---

## Fetch 失败处理规则

- **单个 URL fetch 失败**：不中断流程，记录到 daily 文件末尾的"⚠️ Fetch 失败列表"区块
- **连续 3 天某 URL 失败**：在 daily 文件末尾提示 Long 检查，或在本文件里加 `# DISABLED:` 前缀
- **付费墙源**（如 The Information）fetch 返回摘要或 403 是正常的，不算失败

---

## 元数据
- Tier 1：12 个 URL（英文 6 + 中文/双语 6）
- Tier 2：11 个 URL（国外 7 + 国内 2）
- 最后更新：2026-04-13
