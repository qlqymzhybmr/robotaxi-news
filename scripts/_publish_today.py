"""
临时脚本：把 2026-05-22 的新闻条目写入 docs/data/daily.json
"""
import json, re
from pathlib import Path
from datetime import datetime

TODAY = "2026-05-22"

def h(s):
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)

def p(*paras):
    return "".join(f"<p>{h(x.strip())}</p>" for x in paras if x.strip())

items = [
  # ── 国外 L4 ──────────────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-001", "date": TODAY, "published_at": "2026-05-21",
    "company": "Waymo", "company_slug": "waymo",
    "group": "国外", "sub_group": "国外 L4", "rating": 3,
    "title": "5月21日，亚特兰大 Robotaxi 车辆多次驶入洪水被困，服务全面暂停。",
    "summary_html": p(
      "**5月21日**，亚特兰大遭遇强闪洪，多辆 **Waymo** 无人出租车在积水路段停驶被困，其中至少一辆困于 **Midtown 路段**，导致乘客短暂受困。当地媒体 WSB-TV、11Alive、AJC 等密集报道，视频广泛传播。Waymo 随即宣布暂停亚特兰大全部运营服务，官方声明解释称，车辆在遭遇积水时会主动停车以保护乘客——这一设计本身符合安全逻辑，但在极端天气下造成了「乘客被锁车内」的体验问题。",
      "此次事件是 Waymo 进入亚特兰大以来最受关注的公众事件。截至5月22日上午，服务仍处于暂停状态，Waymo 未给出恢复时间表。Atlanta 是 Waymo 在无监督驾驶城市之外的首批有监督扩张城市之一。",
    ),
    "source_name": "AJC（Atlanta Journal-Constitution）",
    "source_url": "https://news.google.com/rss/articles/CBMisAFBVV95cUxOY25tOFR4TGFxVGpjN2NOeXdrSU1RMXdka2Yzck4zQW03NURBMUdEOEpOQThneFc0YnB6elFMa3RPTUR4cjl1YmFVMHpQNlhNNURpdFNEa1U4b3EzdGlSaWVtbnBpdXBxQWptX2hNWWl3Q05Vd2R4dVFqNFdDRnF2b21EMkxvVlUzUmlROVY5M012czFSUEJ2SXRtbzhfS3Q5RmdZX2dweXBWcEdFRElOQQ?oc=5",
  },
  {
    "id": f"{TODAY}-002", "date": TODAY, "published_at": "2026-05-21",
    "company": "Waymo", "company_slug": "waymo",
    "group": "国外", "sub_group": "国外 L4", "rating": 3,
    "title": "5月21日，因 Robotaxi 在施工区遇困，暂停高速公路接送服务。",
    "summary_html": p(
      "**TechCrunch** 5月21日报道，Waymo 决定暂停高速公路（Freeway）乘客服务，起因是旗下 Robotaxi 在**道路施工区段**反复遭遇行驶困难——包括车辆无法正确判断施工区临时标线、长时间无法通过等问题。这是 Waymo 在高速公路场景上的一次主动降级决定，显示其城市道路能力与高速工况之间仍存在感知差距。",
      "Waymo 此前已逐步在多个城市开放高速公路功能，此次回退是在积累足够施工区数据前的安全优先决策。Reddit 社区对此反应激烈，多位用户反映达拉斯等城市已连续多日服务暂停。",
    ),
    "source_name": "TechCrunch",
    "source_url": "https://techcrunch.com/2026/05/21/waymo-halts-freeway-rides-after-robotaxis-struggle-in-construction-zones/",
  },
  {
    "id": f"{TODAY}-003", "date": TODAY, "published_at": "2026-05-21",
    "company": "Tesla", "company_slug": "tesla",
    "group": "国外", "sub_group": "国外 L4", "rating": 3,
    "title": "5月21日，监督版 FSD（Full Self-Driving Supervised）正式在中国上线，延迟多年后终于落地。",
    "summary_html": p(
      "**5月21日**，**Tesla** 在中国市场正式推出「**FSD（监督版）**」功能，多家媒体同步报道。这是 Tesla 自动驾驶软件在中国市场迟到数年后的正式落地，此前受制于中国数据监管政策和高精地图要求，FSD 一直无法在华商业化。监督版 FSD 仍需驾驶员注意力在场，但标志着 Tesla 在中国正式进入高阶辅助驾驶功能竞争。",
      "国内主要竞争对手（华为乾崑、小鹏、理想等）高阶智驾已深度本土化，**Tesla FSD 的中国表现**及其能否通过本土数据快速迭代将是关键观察点。",
    ),
    "source_name": "The Tech Buzz",
    "source_url": "https://www.techbuzz.ai/tesla-brings-full-self-driving-supervised-to-china/",
  },
  {
    "id": f"{TODAY}-004", "date": TODAY, "published_at": "2026-05-21",
    "company": "Wayve", "company_slug": "wayve",
    "group": "国外", "sub_group": "国外 L4", "rating": 2,
    "title": "5月21日，与 Stellantis 达成协议，Jeep / Ram / Dodge 等品牌将搭载 Wayve 自动驾驶系统。",
    "summary_html": p(
      "**Gizmodo** 5月21日报道，英国自动驾驶公司 **Wayve** 与 **Stellantis** 签署合作协议，Stellantis 旗下 **Jeep、Ram、Dodge** 等品牌的未来车型将搭载 Wayve 的端到端自动驾驶技术。",
      "这是 Wayve 首次与主流 OEM 达成量产搭载协议，意味着其技术路线从「自营 Robotaxi」向「向车企授权」延伸，与 Mobileye 的商业模式趋同。Stellantis 同期宣布另外三项自动驾驶合作，是其 700 亿美元转型计划的组成部分。",
    ),
    "source_name": "Gizmodo",
    "source_url": "https://gizmodo.com/jeep-ram-and-dodge-vehicles-could-soon-come-equipped-with-wayves-self-driving-tech/",
  },
  # ── 国外出行平台 ──────────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-005", "date": TODAY, "published_at": "2026-05-21",
    "company": "Uber", "company_slug": "uber",
    "group": "国外", "sub_group": "国外出行平台", "rating": 3,
    "title": "5月21日，宣布重新部署自有自动驾驶车队——但不作为 Robotaxi 运营。",
    "summary_html": p(
      "**The Verge** 5月21日头条报道：**Uber** 宣布将在内部重新部署自有自动驾驶车辆，用于**非 Robotaxi 场景**，而非直接面向乘客的无人叫车服务。这是 Uber 自 2018 年出售 ATG 自动驾驶部门给 Aurora 后，首次重新以自有车辆身份出现在 AV 领域。",
      "此举引发业界对「Uber-Waymo 合作关系走向」的讨论。Uber 的 AV 重返路径与其是否放弃独家依赖第三方（如 Waymo、Zoox）值得持续关注。",
    ),
    "source_name": "The Verge",
    "source_url": "https://www.theverge.com/2026/5/21/uber-deploying-self-driving-cars-not-robotaxis/",
  },
  {
    "id": f"{TODAY}-006", "date": TODAY, "published_at": "2026-05-21",
    "company": "Lucid", "company_slug": "lucid",
    "group": "国外", "sub_group": "国外出行平台", "rating": 2,
    "title": "5月21日，与 Uber 和 Nuro 达成 Robotaxi 相关合作，市场聚焦其长期叙事。",
    "summary_html": p(
      "**Yahoo Finance** 5月21日报道，**Lucid Motors** 与 **Uber** 和 **Nuro** 分别达成合作，涉及未来 Robotaxi 平台的硬件供应或联合运营方向。市场将此视为 Lucid 在 EV 销量压力下寻求出行生态变现的新尝试。",
    ),
    "source_name": "Yahoo Finance",
    "source_url": "https://finance.yahoo.com/news/lucid-robotaxi-deals-uber-nuro-focus-long-term-story/",
  },
  # ── 国外 OEM / Tier1 ─────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-007", "date": TODAY, "published_at": "2026-05-21",
    "company": "NVIDIA", "company_slug": "nvidia",
    "group": "国外", "sub_group": "国外 OEM / Tier1", "rating": 1,
    "title": "5月21日，宣布 GTC Live Computex 2026，Jensen Huang 将在台北发布 AI 与加速计算最新突破。",
    "summary_html": p(
      "活动定于 **6月1日台北时间上午9点**，NVIDIA 称将发布「AI 与加速计算最新突破」，与自动驾驶芯片生态直接相关（NVIDIA 系车载算力当前最主流的方案之一）。",
    ),
    "source_name": "Twitter @NVIDIA",
    "source_url": "https://x.com/nvidia/status/2057606098983456840",
  },
  {
    "id": f"{TODAY}-008", "date": TODAY, "published_at": "2026-05-21",
    "company": "Stellantis", "company_slug": "stellantis",
    "group": "国外", "sub_group": "国外 OEM / Tier1", "rating": 2,
    "title": "5月21日，宣布 700 亿美元电动化与自动驾驶回归计划，同期形成三项自动驾驶合作。",
    "summary_html": p(
      "**InsideEVs** 报道，**Stellantis** 公布规模达 **700 亿美元**的综合转型计划，包括 LFP 电池自研、挑战 Tesla FSD 的自研智驾方案，以及三项外部自动驾驶合作（其中之一为与 Wayve 的技术授权协议）。这是 Stellantis 在销量下滑压力下的战略重启信号。",
    ),
    "source_name": "InsideEVs",
    "source_url": "https://insideevs.com/news/stellantis-70-billion-comeback-lfp-batteries-tesla-fsd-challenger/",
  },
  # ── 社区热帖 ──────────────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-009", "date": TODAY, "published_at": "2026-05-21",
    "company": "Reddit/SelfDrivingCars", "company_slug": "reddit-selfdriving",
    "group": "国外", "sub_group": "社区热帖", "rating": 2,
    "title": "5月21日，Waymo 亚特兰大洪水事件社区反应热烈，达拉斯用户反映服务暂停多日。",
    "summary_html": p(
      "r/SelfDrivingCars 和 r/Waymo 均大量转载亚特兰大洪水相关报道，社区对「Waymo 在恶劣天气下的感知局限」展开讨论。达拉斯用户表示本地 Waymo 服务已暂停数日，疑与此次全国性高速公路政策调整有关。",
    ),
    "source_name": "r/SelfDrivingCars · Reddit",
    "source_url": "https://www.reddit.com/r/SelfDrivingCars/comments/1tk2u9t/waymo_halts_freeway_rides_after_robotaxis/",
  },
  {
    "id": f"{TODAY}-010", "date": TODAY, "published_at": "2026-05-21",
    "company": "Reddit/SelfDrivingCars", "company_slug": "reddit-selfdriving",
    "group": "国外", "sub_group": "社区热帖", "rating": 2,
    "title": "5月21日，Transport for London（TfL）就 Robotaxi 进入伦敦表达担忧，英国政府已公开征集运营商投标。",
    "summary_html": p(
      "英国政府已正式启动 Robotaxi 商业运营的竞标程序，但 **TfL（伦敦交通局）**公开表达对无人出租车安全性和对现有公共交通冲击的担忧。英国监管路径与美国的差异值得关注。",
    ),
    "source_name": "r/SelfDrivingCars · Reddit",
    "source_url": "https://www.reddit.com/r/SelfDrivingCars/comments/1tjw4e5/transport_for_london_voices_concern_over_robotaxis/",
  },
  {
    "id": f"{TODAY}-011", "date": TODAY, "published_at": "2026-05-21",
    "company": "Reddit/Waymo", "company_slug": "reddit-waymo",
    "group": "国外", "sub_group": "社区热帖", "rating": 1,
    "title": "Uber-Waymo 合作关系是否走向终结？社区讨论热度高。",
    "summary_html": p(
      "Uber 宣布重新部署自有 AV 车队后，r/Waymo 出现分析贴探讨二者合作走势，社区整体偏向「Uber 在建立自主 AV 能力」的判断。",
    ),
    "source_name": "r/Waymo · Reddit",
    "source_url": "https://www.reddit.com/r/waymo/comments/1tjo3cx/is_the_uberwaymo_partnership_coming_to_an_end/",
  },
  # ── 国内 L4 ──────────────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-012", "date": TODAY, "published_at": "2026-05-21",
    "company": "小鹏", "company_slug": "xpeng",
    "group": "国内", "sub_group": "国内 L4", "rating": 3,
    "title": "5月21日，Robotaxi 首台量产车正式下线，搭载 4 颗图灵 AI 芯片。",
    "summary_html": p(
      "**5月21日**，**小鹏集团** Robotaxi 首台量产整车在工厂正式下线。该车搭载 **4 颗小鹏自研图灵 AI 芯片**，算力配置面向全无人驾驶场景。英文媒体 AD HOC NEWS 标题直指「小鹏正式启动 Robotaxi 量产，向 Tesla 发起自动驾驶挑战」。",
      "这是继百度萝卜快跑之后，国内第二家自主 OEM 实现 Robotaxi 整车批量下线。小鹏计划 2026 年开放规模化 Robotaxi 商业运营，当前量产下线是关键里程碑。",
    ),
    "source_name": "汽车之家",
    "source_url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTE9aVjdQTmdaX05ia0QxbEQ1UVE5R3VNSlFhdWNRSWtHU2o2NVZQNjhyajFOam04aHdGdm5CT1dLaHNlb3hzMUl4MktFS0NOU25FakR6RFk2bFVZb00?oc=5",
  },
  {
    "id": f"{TODAY}-013", "date": TODAY, "published_at": "2026-05-21",
    "company": "小鹏", "company_slug": "xpeng",
    "group": "国内", "sub_group": "国内 L4", "rating": 1,
    "title": "5月21日，GX 全系不带激光雷达上市，纯视觉智驾路线正式落地量产。",
    "summary_html": p(
      "小鹏 GX 所有版本均不配备激光雷达，采用纯视觉方案，体现小鹏向「无图纯视觉」路线的战略转型。同期「城区 NOA 智驾天梯榜」显示小鹏 VLA 2.0 排名第五，与华为乾崑差距 8 分。",
    ),
    "source_name": "汽车之家",
    "source_url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTE5zYW5nSV9PQ1N3SzJnTWhEZDZtQnpKZUM3NWdsOXhkU1NwSVRhNXVubnRVcDV0YjB2M3FCdDZUN2tHdDVLWTVqWm02TkdIc3BGSnExXzBpNEw0eGM?oc=5",
  },
  {
    "id": f"{TODAY}-014", "date": TODAY, "published_at": "2026-05-21",
    "company": "小马智行", "company_slug": "xiaoma",
    "group": "国内", "sub_group": "国内 L4", "rating": 2,
    "title": "5月21日，首次进军 RoboVan 赛道，做了 10 年 Robotaxi 后拓展商用车场景。",
    "summary_html": p(
      "**小马智行**在做了 **10 年 Robotaxi** 之后，首次宣布进入 **RoboVan**（无人货运面包车）领域，以北京车展为契机推出相关产品规划。RoboVan 是介于 Robotaxi 和自动驾驶卡车之间的新兴细分赛道，在同城物流、最后一公里配送场景有潜力。",
    ),
    "source_name": "新浪财经",
    "source_url": "https://news.google.com/rss/articles/CBMi2AVBVV95cUxOMFowdmRRbVZEbWNyQ1QxQ2h5M21ZRXRYX3dVOXNWcWl5ejFLdmQ0NkpnOUYzWXdMOHBxbEhwSFpCNUVBQ0ZxWkxVMVNUSTJZODVlVi1Nb2E0cjYtWlYwY0dfZkNzeWF2Wm1MYWFSVlFnWHYyN1NidlJiWDQyelpGV2pQN3JuZFRVdjhIQWlsdGlDV01UV1hTTTZxWU9qYnVSRnFmbGVDdldBWmxRbzVIcm8wNFllVUFnRzF1V0ZzaV9TeFhvdDBOUVFPOWRaWEhLeUhVV040NWhWWXR6NUxUekhRWndzd2Y2YTJ5Rm5IUms2M1ZvdUY1SlVhUU13YV9GTmRvWjh5M0VmSlF5SXZXMkxJZkFGZVhtNE1DdEY2OHpNbEZ6bVh3SmxwcW9lODVIUXl3dERZVFNnMG1qbW54cmJPYU82MVhnOGQ3U3lnVGZHblJOWk5lVGdwbjViS1QxdGNYcFZmT1ByNzAtai1QR2ltbDFaVEdEaGFHQkxtbzhxZjNHRHJqVndCLWpTZEZWUjlTcnA1WVZ4S2hlUVNXempyNHdzUE9OMzdCV1d5NTlJOXVyeEozT2JBYWdqN1JUbUhwZzdiZkItTVJKMlpzTDIwOTU1VkQ5SVdMVDRrODdNMmxIQWFFLUpvbkRWM19hMFhJMnh4bGd2VEdSMm9kMW9TU3ZRMUR6ZWNuNnpsYzM2YXY3b0JXbHdlbnVtUG9OWnBvT2xNNXRpNklKYkQ0UDkxcWxGVTZyZl9hNXFuLWpIbi1pNDRWYW9xVk5peUg3aGhIZ05hY184dzNNWkhGam1Hb2taUEN2SWJJcTQ2NnltcHZuVlNYMjdIVGhRWmhqekNpcGJCMWQxVm1ucUwxTzVHb3BzZWZhM05WSTRKVVhmalNxN2VPXzdoMklWSlRFcjhjZTJQZGhMU1JqV3hveUVRUUFPekMtenRpd05iWGxreEJpdWRvbw?oc=5",
  },
  # ── 国内出行平台 ──────────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-015", "date": TODAY, "published_at": "2026-05-21",
    "company": "曹操出行", "company_slug": "caocao",
    "group": "国内", "sub_group": "国内出行平台", "rating": 2,
    "title": "5月21日，宣布以香港为桥头堡拓展全球 Robotaxi 右舵市场，股价盘中涨逾 10%。",
    "summary_html": p(
      "**曹操出行**宣布将以**香港**作为进军全球 Robotaxi 右舵市场的首个桥头堡，结合花旗等机构推荐，股价当日盘中一度涨逾 **10%**。右舵市场（英国、澳洲、新加坡、日本等）是国内 Robotaxi 玩家尚未布局的蓝海。",
    ),
    "source_name": "新浪财经",
    "source_url": "https://news.google.com/rss/articles/CBMinAJBVV95cUxOdDNlNV9QT09MTzVJX3pJRjQ0NUR5ZERNaXJyYUdNRUM5d0lMNzF3ZkxXcGhwWFhTT3V1TEdiSkJoSVp0OG9VLUp2Nkh3dWV4cnBJQ0R0N005eDhwSjEweVo3eHRjWkNXeGhYWUwtMVV6ME1CeUVOa01SeDNjZ0Q0dnB6bndxdkI0OVoxN0twaVhrY21pSm04V0VTblVPVmhuTWJvSkVvTURLMjhTcERKaUtvY0E0T2tXdkRKbEZucnRZUElTa0V5UHhSREVuQThuWVJzSV8wQVJsbWZhcENMX2ZSa2J6ODlHOUxDcW1YeTliclR6Q01nbFkwVlUzZEtvTTNSTGxROWpXUkVmWS04aWRjMU1ZOWsyVjFRcQ?oc=5",
  },
  {
    "id": f"{TODAY}-016", "date": TODAY, "published_at": "2026-05-21",
    "company": "文远知行", "company_slug": "wenyuan",
    "group": "国内", "sub_group": "国内出行平台", "rating": 1,
    "title": "5月21日，智驾概念股早盘走势强劲，文远知行-W 涨逾 9%。",
    "summary_html": p(
      "受行业政策预期利好影响，智驾板块概念股整体走强，**文远知行-W** 盘中涨幅逾 **9%**，浙江世宝涨逾 15%。暂无文远具体业务新进展。",
    ),
    "source_name": "新浪财经",
    "source_url": "https://news.google.com/rss/articles/CBMirgFBVV95cUxNV2ZpaXR1RDRMcVVieFppWHZQdndUdnpDYXpYSTlacjJFNWVkZ00zaUg1WjVZeXdnRUhNMDlYYkhhVDJ5eEpmZG9xZ0kwUVJoV0FGYS1tVms2ME5QSC1Od0dsNjIwWktOWng1YmdLYmpIRi1HajJlYzd5OEgyS0plUWlsS1cyM1dCOGVQc2Y1TVdNNzA2dHczSFU0TzVIdkdPRjA0UkprTXBVMkpYRmc?oc=5",
  },
  # ── 国内新势力 / 传统 OEM ─────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-017", "date": TODAY, "published_at": "2026-05-21",
    "company": "蔚来", "company_slug": "nio",
    "group": "国内", "sub_group": "国内新势力 / 传统 OEM", "rating": 2,
    "title": "5月21日，Q1 财报超预期，连续第二季度录得盈利；同期披露辅助驾驶仅需竞品 1/5 算力。",
    "summary_html": p(
      "**5月21日**，蔚来发布 **2026 Q1 未审计财报**，收入超预期，连续第二季度实现盈利，为公司历史最佳毛利率。股价当日先涨后跌——盘后因「毛利率警告」部分抹去涨幅。",
      "与此同时，蔚来披露其辅助驾驶软件在相同功能下**仅需竞争对手 1/5 的算力**运行，暗示蔚来在端侧算法效率上具备竞争优势，可能影响芯片采购与成本结构。",
    ),
    "source_name": "Yahoo Finance",
    "source_url": "https://finance.yahoo.com/news/nio-shares-rally-after-first-quarter-earnings/",
  },
  {
    "id": f"{TODAY}-018", "date": TODAY, "published_at": "2026-05-21",
    "company": "理想", "company_slug": "liauto",
    "group": "国内", "sub_group": "国内新势力 / 传统 OEM", "rating": 2,
    "title": "5月21日，自研 M100 芯片披露，采用「数据流架构」，与传统 SoC 路线不同。",
    "summary_html": p(
      "**理想汽车**正在研发自研 **M100 芯片**，采用「数据流架构」而非传统 SoC 流水线架构，声称在自动驾驶推理场景下具备效率优势。同期理想还选择 **Arteris FlexNoC 5 IP** 用于 AI 驱动的自动驾驶 SoC 设计。两条消息共同指向理想在芯片自研上的加速布局。",
    ),
    "source_name": "信息化观察网",
    "source_url": "https://news.google.com/rss/articles/CBMiYEFVX3lxTE12S1BSemZERlRuRk90R1FmaVhaT3lXeTltSGZ4NGVEZl80UmdlSDl6ZklwM2tFNkdaQ01kc3hzemUxRkRqSkNOaHEtSHRqcnduZHktNzctendwdkEyVU5mSg?oc=5",
  },
  {
    "id": f"{TODAY}-019", "date": TODAY, "published_at": "2026-05-22",
    "company": "小米", "company_slug": "xiaomi",
    "group": "国内", "sub_group": "国内新势力 / 传统 OEM", "rating": 1,
    "title": "5月22日，YU7 GT 发布，38.99 万元起；智驾团队负责人谈大模型成熟度。",
    "summary_html": p(
      "**小米 YU7 GT** 于 **5月22日凌晨**正式发布，起售价 **38.99 万元**。小米智驾团队负责人陈龙表示「先让大模型长到十八岁」，暗示小米对端到端大模型智驾方案仍处于成熟期评估阶段，当前未急于大规模商用。",
    ),
    "source_name": "新浪财经",
    "source_url": "https://news.google.com/rss/articles/CBMivAFBVV95cUxNVnBuNVUtR0xqZGdHMkhaTGFsdjcwYkE2NjQ0dWZVRlBiSnFLR1htYTJqd0dCa1ZUa25LSExxVTFTcTBMQVpYR2dsS256RzlwZlR3WGpNUHZkX0t2cjJNMUZJMnJHeXJYQWpLd0ZvZDZBMlYwVm9jOTNlb0xyUlR4SmpKWVRVYm9EU0VJT0ZBUHJBaUhPNlI1LUJLcXBiNmJPMUJlTXNzT1BxeW9nclJEX3FTa1h4MUtIZXhCOQ?oc=5",
  },
  {
    "id": f"{TODAY}-020", "date": TODAY, "published_at": "2026-05-21",
    "company": "零跑", "company_slug": "leapmotor",
    "group": "国内", "sub_group": "国内新势力 / 传统 OEM", "rating": 1,
    "title": "5月21日，2026 年战略曝光，冲刺百万辆年销，含智驾全系推新。",
    "summary_html": p(
      "零跑汽车 2026 年将在产品、智驾、服务三线全面推新，目标冲刺**百万辆年销量**。智驾路线以自研平台为主，中低价位段规模化是核心差异化策略。",
    ),
    "source_name": "新浪财经",
    "source_url": "https://news.google.com/rss/articles/CBMifkFVX3lxTFBSR19VdjJkYlJ6Y3RsbDRDOVpmT0F2cjhRblVucmpVRmphTjBQQ3hNUV9kVVNBSmdkLUNCLU03LTU2WWsyOHpXM2UzYkpnVTNUQk5GODBhNHNZdWFrNUdPV3RweThacEd0WGtBbm9pV1lOM1Rxc0xpN2JzQWZyUQ?oc=5",
  },
  {
    "id": f"{TODAY}-021", "date": TODAY, "published_at": "2026-05-21",
    "company": "长安", "company_slug": "changan",
    "group": "国内", "sub_group": "国内新势力 / 传统 OEM", "rating": 1,
    "title": "5月21日，启源 A06 摄像头异常导致紧急制动，部分车主称不敢用智驾。",
    "summary_html": p(
      "长安启源 A06 部分车主反映摄像头「突然变糊」并触发**紧急制动**，4S 店给出拆卸擦拭方案，部分车主拒绝。此事件对长安智驾品牌信任度有负面影响，在 L2+ 智驾普及关键节点尤为敏感。",
    ),
    "source_name": "新浪财经",
    "source_url": "https://news.google.com/rss/articles/CBMidkFVX3lxTE5PbTYtN19vemxrTjJPbFJyaXpaQV9wNWxnVEtUby16Q2dFUFdGNkRycXhYQ2VxbEpRU3prdzFUOEV1bFdrcGxSMUxzMjNxNkdWRjFDUGhhcXJ1WDRsU1FWXzlKRVI1RUNqLW9LRjdYNGp6Zk5nc2c?oc=5",
  },
  # ── 国内智驾方案商 ────────────────────────────────────────────────────────────
  {
    "id": f"{TODAY}-022", "date": TODAY, "published_at": "2026-05-21",
    "company": "Momenta", "company_slug": "momenta",
    "group": "国内", "sub_group": "国内智驾方案商", "rating": 2,
    "title": "5月21日，对标特斯拉 FSD，借势出海战略浮出水面。",
    "summary_html": p(
      "**Momenta** 明确以**对标特斯拉 FSD** 为技术定位，并借助当前国际客户对中国智驾供应商的关注，加速出海布局。Momenta 以「飞轮数据」闭环为核心竞争力，此次出海是继 Bosch、丰田等合作之后的进一步国际化动作。",
    ),
    "source_name": "雷峰网",
    "source_url": "https://news.google.com/rss/articles/CBMiekFVX3lxTE9xVkpVSGhvWTBKdTJwN2R3NHBKcjR2eWFUb3R0aHd4MlJ1QmI0ZmZfSDBqZFUtWVRRRzVmOW5JSktpQ3F3cXZvbk1FOWFWMDduNEZYY0hydlFJaW5YalZfQkF4bHNZV0JrVDRZbTItM0JxbEVGLTVOeFJR?oc=5",
  },
]

# ── 日期过滤 ──────────────────────────────────────────────────────────────────
run_date = datetime.strptime(TODAY, "%Y-%m-%d")
passed, filtered = [], []
for item in items:
    pub = datetime.strptime(item["published_at"], "%Y-%m-%d")
    if abs((run_date - pub).days) <= 2:
        passed.append(item)
    else:
        filtered.append(item["id"])
print(f"日期过滤：{len(filtered)} 条被过滤，{len(passed)} 条通过。")

# ── 读取 / 写入 daily.json ────────────────────────────────────────────────────
daily_path = Path("docs/data/daily.json")
if daily_path.exists():
    with open(daily_path, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

entry = {"date": TODAY, "items": passed}
data = [e for e in data if e["date"] != TODAY]
data.insert(0, entry)

with open(daily_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"写入完成：docs/data/daily.json 共 {len(data)} 天，今日 {len(passed)} 条。")
r3 = sum(1 for i in passed if i['rating']==3)
r2 = sum(1 for i in passed if i['rating']==2)
r1 = sum(1 for i in passed if i['rating']==1)
print(f"评级分布：⭐⭐⭐ {r3} 条 / ⭐⭐ {r2} 条 / ⭐ {r1} 条")
