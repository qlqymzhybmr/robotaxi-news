---
name: robotaxi-news-tracking
description: 全球 Robotaxi、L2/L4 智能驾驶、政策法规的每日新闻追踪与每周简报生成。当用户说"跑今日新闻"、"跑 robotaxi daily"、"生成上周周报"等命令时触发。
---

# Robotaxi News Tracking Skill

## 这个 skill 是做什么的

这个 skill 帮 Long(DiDi 智驾产品/分析师)每天追踪全球 Robotaxi 竞品动态,并在每周一生成一份给老板看的简报。核心流程分两步,输出两条并行路线:

1. **每日抓取(daily-fetch)**:实习生每天上午手动触发一次(包括周末),覆盖过去 24 小时的新闻,输出一份带 ⭐ 评级 + 复选框的 markdown 文件供 Long 划重点
2. **周报生成(weekly-report)**:每周一,把**上周二到本周一**勾选过的重要新闻合成一份按 Long 写作风格的 HTML 简报,可粘贴到 OneNote 编辑后截图发老板

**两条并行输出路线**:

- **线 A(自动)**:daily-fetch / weekly-report 跑完后,Claude 按自己评级的 ⭐⭐+ 自动筛选,发布到 GitHub Pages 网页(https://qlqymzhybmr.github.io/robotaxi-news/)。全自动,实习生只需最后 push 一次。
- **线 B(人工)**:实习生勾选 `[x]` 重点,周一生成 OneNote 可粘贴周报,发老板。

两条线共享 daily-fetch 跑出来的数据,但输出完全独立,互不影响。

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
| "更新竞品 list" / "加一家公司到 list" | 直接编辑 `competitors.md` | 任意时间 |
| "学习这次的判断" / "把这条加进 examples" | 直接编辑 `important-examples.md` | 每次划完重点后 |

**默认执行策略(重要)**:
- 说"跑今日新闻"时,skill **默认自动分两阶段执行**:
  - Phase 1:国外组(fetch 英文白名单源 + 搜索 `competitors.md` 的国外公司)
  - Phase 2:国内组(fetch 中文白名单源 + 搜索国内公司)
- 两阶段的产物**合并写入同一份文件** `data/daily/YYYY-MM-DD.md`(包含 "## 国外 L4" 和 "## 国内 L4" 等 section),实习生体感是一次跑完、一份文件
- 分阶段的好处:避免单次 tool 调用过多导致上下文或 5 小时额度问题
- 如果 Phase 1 跑完后中断(网络/额度),隔一段时间说"只跑国内组"即可补跑 Phase 2,不会覆盖已有的国外组内容

---

## 工作原理

### 信息源(如何不漏查)

这个 skill **不依赖单一搜索**,用两层策略叠加:

**第一层:核心聚合页 fetch**(主力)
- skill 启动时优先 `web_fetch` 一组**强制白名单 URL**,列在 `sources.md` 里
- 这些 URL 是按时间倒序的新闻列表页(如 CnEVPost self-driving 板块、TechCrunch transportation、Waymo 官方博客等),fetch 一次能拿到当天 10-30 条最新标题
- 头部公司(Waymo、Tesla、Pony、WeRide、萝卜快跑、Zoox 等)的新闻基本会被这一层捕获

**第二层:按公司定向搜索**(中英双语)
- 对 `competitors.md` 里**没有出现在第一层结果中的公司**,逐家做 `web_search`
- 重点公司(带 ⭐):中英双语各 1 次
- 普通公司:单语搜 1 次
- 关键词模板见 `workflows/daily-fetch.md`

### 这个 skill 做不到的事(必读)

**为了让你和实习生有合理预期,必须明确以下限制:**

1. **没有专业新闻 API**:skill 用的是通用 web_search 和 web_fetch,背后是搜索引擎索引。**没有接入** NewsAPI、GDELT、Bloomberg Terminal、彭博社等专业新闻源
2. **微信公众号几乎抓不到**:很多中国公司新闻最早只发公众号,搜索引擎对微信内容索引很差。等到二次转载到新浪/36氪可能延迟 1-2 天
3. **X / Twitter 滞后**:搜索引擎对 X 的索引滞后明显,车主目击视频、Musk 即时推文这类内容**很可能错过**或滞后
4. **非中英文媒体覆盖差**:日韩德法的本地新闻基本要等英文转载,原始日文/德文 PR 抓不到
5. **预估覆盖率:约 70-85%**。剩余 15-30% 需要靠人工补漏

**降低漏查的措施**:
- 强烈建议实习生每天看完 daily 后,**手动扫一眼 1-2 个垂直媒体**(推荐 CnEVPost、36氪汽车)作为 backup
- 如果发现某次明显漏查,告诉 Claude 调整 sources.md 或 competitors.md

---

## 文件结构

```
robotaxi-news/
├── SKILL.md                     # 你正在看的这个文件
├── DEPLOY.md                    # GitHub Pages 首次部署指南
├── competitors.md               # 竞品 list(按组分),可随时增删
├── sources.md                   # 强制白名单源 URL
├── style-guide.md               # 写作风格规则(学自 Long 的历史周报)
├── important-examples.md        # 重要性判断规则(每次划完重点后追加)
├── workflows/
│   ├── daily-fetch.md           # 每日抓取的执行步骤(含 Phase 3 自动发布)
│   ├── weekly-report.md         # 周报生成的执行步骤(含步骤 8.5 + 11)
│   ├── daily-publish.md         # 线 A:每日精选自动发布到网页
│   └── weekly-publish.md        # 线 A:周报自动发布到网页
├── data/
│   ├── daily/                   # 每日抓取产物,文件名 YYYY-MM-DD.md
│   └── reports/                 # 周报 HTML(YYYY-Wxx.html)+ JSON 副产物(YYYY-Wxx.json)
└── web/                         # GitHub Pages 网站根目录
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
直接编辑 `competitors.md`。这是一份按组分类的 markdown list,加一行就行。下次 daily-fetch 会自动覆盖。

### 想调整写作风格
编辑 `style-guide.md`。这个文件里写的是从历史周报里学到的规则(比如"日期开头"、"加粗用于事实而非情绪"、"零评论性词汇"等)。改了之后下次 weekly-report 会按新规则生成。

### 想调整重要性判断
有两种方式:
1. **被动学习**:每天划完重点后说"学习这次的判断",Claude 会把你的勾选追加到 `important-examples.md`
2. **主动编辑**:直接打开 `important-examples.md` 添加规则,比如"涉及融资金额超过 5 亿美元的一律重要"

### 想加新的信息源
编辑 `sources.md`,按格式加一行 URL 即可。建议优先加**按时间倒序的新闻列表页**,而不是单篇文章 URL。

---

## Token 消耗与运行成本

| 操作 | 工具调用次数 | 预估 input tokens | 预估时长 |
|------|------|------|------|
| daily-fetch(默认两阶段 + 线 A 发布)| ~45(22+22+1)| 80万-120万 | 20-30 分钟 |
| daily-fetch(仅一组,单独跑)| ~22 | 40-60 万 | 10-15 分钟 |
| weekly-report(含 JSON 副产物 + 线 A 发布)| ~8 | 5-10 万 | 3-5 分钟 |
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

### 工作方式(线 A 全自动)

1. 实习生说"跑今日新闻",Claude 跑完 daily-fetch 后,自动串接 daily-publish
2. daily-publish 从今日 daily 文件里提取所有 ⭐⭐+ 条目,写入 `web/data/daily.json`
3. 实习生运行 `git add -A && git commit -m "daily YYYY-MM-DD" && git push`,约 1-2 分钟后网页更新
4. 每周一周报生成后,weekly-report 自动串接 weekly-publish,写入 `web/data/weekly.json`,同样 push 后自动更新

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
