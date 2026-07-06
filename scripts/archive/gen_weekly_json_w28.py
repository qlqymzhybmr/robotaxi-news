"""Generate 2026-W28 weekly JSON and publish to docs/data/weekly.json."""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

data = {
  "week_id": "2026-W28",
  "date_range": "0630-0706",
  "title": "无人驾驶行业0630-0706重要新闻",
  "generated_at": "2026-07-06T23:00:00+08:00",
  "sections": [
    {
      "name": "国外",
      "entries": [
        {
          "company": "Waymo",
          "company_slug": "waymo",
          "headline_html": "<b>Waymo：</b>凤凰城/Uber 分手全程落幕 + 独立日大乱暴露极端场景短板，扩张步伐同步推进",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月29日</b>，Waymo 与 Uber 正式终止在凤凰城持续近三年的 Robotaxi 合作。Waymo 叫车入口从 Uber App 移除，车辆回归 Waymo One 独立平台，同日转向 <b>DoorDash 自动配送</b>拓展多模式收入。Reuters、CNBC、Bloomberg 均证实属「计划性退出」，同日 Uber 宣布与 Lucid Air+Nuro 新合作，节奏之密集清晰表明 Uber 已备好替代方案。"
            },
            {
              "label": "b",
              "content_html": "分手余震持续整周：<b>7月4日</b>，<b>Uber CEO Dara Khosrowshahi 乘坐 Gravity Robotaxi</b>（Lucid Gravity 平台）的视频在社交媒体传播，带动 Lucid 股价明显上涨，被解读为 Uber CEO 正在主动布局 Waymo 以外的合作选项。<b>7月5日</b>，凤凰城本地公共广播 <b>KJZZ</b> 再次确认 Uber 正式终止凤凰城合作，Uber「技术不可知论」平台战略从分手当天到整周行动已成清晰链条。"
            },
            {
              "label": "c",
              "content_html": "<b>7月4日美国独立日</b>，旧金山多辆 Waymo 无人出租车在节日庆典中碾过路面烟花，其中一辆被<b>引燃起火</b>，消防赶赴处置；庆典结束后严重拥堵，数辆 Waymo 长时间堵路、电量耗尽后被<b>拖车拖走</b>。Waymo 表示正在调查，此次事件将「极端场景应急处置」能力不足暴露在公众与监管机构面前。"
            },
            {
              "label": "d",
              "content_html": "扩张层面，Waymo 本周在<b>纳什维尔国际机场（BNA）</b>积极测试感知数据，同日 Sawyer Merritt 体验 Waymo Ojai 遭遇首次<b>行程失败</b>（地图错误叠加远程代理判断失误），为新城市扩张早期挑战写照；<b>华盛顿 DC 市议员 Charles Allen</b> 推进 AV 专项立法，拟为自动驾驶车辆建立许可制度与基础设施规范，若通过将打开东海岸核心市场。"
            }
          ]
        },
        {
          "company": "Tesla",
          "company_slug": "tesla",
          "headline_html": "<b>Tesla：</b>Robotaxi 迈阿密全面落地 + FSD 德州过失杀人案全程——扩张与法律压力并行",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>7月3日</b>，Tesla 在<b>迈阿密</b>正式启动 Robotaxi 商业运营，成为继奥斯汀后第二个商业城市，总计覆盖 <b>5 城</b>（Reuters 报道）。用户通过 Tesla App 即可叫车，无需安全员随车，与 Waymo 在南佛罗里达展开直接竞争。<b>7月4日</b>服务区持续扩展，Tech Times 专门关注<b>佛罗里达暴雨天气</b>对纯摄像头方案的极限考验。<b>7月5日</b>，The Information 独家确认迈阿密服务<b>无安全员随车</b>，新奥尔良同步目击搭载摄像头清洗器的新型 Robotaxi 测试车，多城扩张布局持续提速。"
            },
            {
              "label": "b",
              "content_html": "德州致命事故引发的刑事诉讼持续发酵：德州哈里斯县检察官于 <b>7月1日</b>对凯蒂（Katy, TX）车主 <b>Michael David Butler</b>（44 岁）正式提起<b>过失杀人诉讼</b>（Electrek 7月3日完整报道）。<b>6月19日</b>，他驾驶 Model 3 将油门从 67% 踩至 100% 强行超控 FSD，以 73 英里/时冲入民居，致 <b>76 岁老人 Martha Avila</b> 当场身亡。最关键证据来自手机搜索记录：事故数周前他多次搜索「tesla fsd not aggressive enough 2026」，直接证明蓄意超控。Butler 面临二级重罪<b>最高 20 年刑期</b>，这是美国首批因主动超控辅助驾驶被追究刑责的案例，将深刻影响全美 AV 责任认定框架。"
            },
            {
              "label": "c",
              "content_html": "<b>7月3日</b>法庭文件进一步揭示：FSD 当时已在<b>主动减速准备停车</b>，Butler 随后踩下油门踢出系统，从技术层面表明 FSD 本身并未失效，法律责任指向驾驶员主动决策。此外本周还发生两起 Tesla 安全事件：<b>6月29日</b>加州<b>希米谷（Simi Valley）</b>咖啡厅 Tesla 撞车事故，<b>1名女性死亡</b>，与 FSD V14 Lite 扩大覆盖公告发生于同一天；<b>7月1日</b>已婚夫妇在 <b>Tesla Semi</b> 事故中双双罹难，为已知首例 Semi 致命碰撞事故。"
            },
            {
              "label": "d",
              "content_html": "<b>7月2日</b>，Tesla 已在公开道路测试<b>不带方向盘的 Cybercab 原型车</b>（KVUE ABC Austin 报道），Robotaxi 无人化目标进入实质阶段。同日 <b>NHTSA 提出新提案</b>，拟允许无刹车踏板和手动控制装置的自动驾驶车辆上路，大幅降低 FMVSS 对 AV 的适用要求，意见征询截止 <b>7月27日</b>（编号 NHTSA-2026-0728）；提案若通过，将为 Tesla Cybercab、Waymo、Zoox 扫清关键监管障碍。"
            }
          ]
        },
        {
          "company": "Zoox",
          "company_slug": "zoox",
          "headline_html": "<b>Zoox：</b>量产冲刺进入实质阶段，「无人监管」运营难题同步浮现",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>7月1日</b>，亚马逊旗下 Zoox 正式宣布<b>量产就绪设计</b>（production-ready autonomous vehicle），外形与内饰大幅优化，距上月预生产设计定型仅数周，进入实质量产冲刺阶段。<b>7月3日</b>发布 Robotaxi 改款方案，聚焦乘客体验升级，座椅、屏幕布局、内饰均有大幅改进；Zoox 坚持<b>无方向盘无踏板专用车型路线</b>，与市面改装 Robotaxi 形成本质区别，差异化竞争力进一步强化。"
            },
            {
              "label": "b",
              "content_html": "<b>7月5日</b>，Zoox 遭遇<b>乘客车内吸烟</b>运营难题，视频显示乘客「什么都抽」，Zoox 已宣布紧急升级改造以应对。事件折射出无人出租车在「无人监管」环境下维护公共秩序的普遍挑战，也引发业界对车内行为规则与技术执法手段的讨论——随着 Waymo、Tesla、Zoox 同步扩张，运营层面的合规问题将日益成为关键变量。"
            }
          ]
        },
        {
          "company": "Uber / WeRide",
          "company_slug": "uber",
          "headline_html": "<b>Uber 新布局 + WeRide 苏黎世：</b>出行平台 × AV 国际化组合本周双线推进",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月29日</b>，Uber 宣布与 <b>Lucid Air + Nuro</b> 合作在旧金山测试高端 Robotaxi，消息确认后 <b>Lucid（LCID）股价当日涨 15%</b>，分析师同日将 Uber 目标价上调至 $100。Nuro 原以最后一公里配送机器人起家，此次进入载人 Robotaxi 是其商业模式的重大转型；<b>7月1日</b>，日产 CEO 在 Yahoo Finance 访谈中公开表示 Robotaxi 市场潜力「really big」，力挺 Uber 合作，成为 Waymo/Uber 分手后首批 OEM 级别的公开背书。"
            },
            {
              "label": "b",
              "content_html": "<b>7月4日</b>，文远知行（WeRide）与 Uber 在瑞士<b>苏黎世</b>正式启动商业 Robotaxi 服务，这是<b>欧洲首个</b>规模化商业无人出租车落地案例，用户可通过 Uber App 直接叫车。<b>7月2日</b> WeRide 已宣布参展 WAIC 2026（7月17-20日上海），展示 GXR Robotaxi + AION N60（累计销量 12,573 台），并预告展会上将有新品发布；GXR 已在新加坡、苏黎世、马德里、利雅得商业运营，中国 Robotaxi 公司全球化步伐清晰领先。"
            }
          ]
        },
        {
          "company": "GM",
          "company_slug": "gm",
          "headline_html": "<b>GM 正式放弃 Robotaxi：</b>美国三大车企全部退出，专业玩家格局加速形成",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>7月3日</b>，通用汽车正式宣布从 Robotaxi 战略转向，将资源集中于 <b>Super Cruise</b> 等量产 ADAS 业务，放弃了 Cruise 2023 年事故后留下的 Robotaxi 遗产。这标志<b>美国三大传统车企（Ford/GM/Stellantis）中最后一家 Robotaxi 积极参与者彻底退出</b>，全球纯 Robotaxi 赛道进一步向 Waymo、Tesla 和中国玩家集中，行业格局加速收敛至专业玩家。"
            }
          ]
        }
      ]
    },
    {
      "name": "国内",
      "entries": [
        {
          "company": "监管突破",
          "company_slug": "regulation",
          "headline_html": "<b>中国 L3 首批准入落地：</b>长安深蓝、北汽极狐获批，驾驶员可合法「脱眼」时代开启",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>7月4日</b>，中国监管层正式批准<b>长安深蓝和北汽极狐</b>两款车型的 L3 级自动驾驶准入资质，成为国内首批获得 L3 上路许可的量产车型（汽车之家报道）。此前 L3 在中国长期处于法规空白状态，驾驶员须对 L2+ 功能全程监控。首批 L3 准入意味着驾驶员在特定条件下可<b>合法「脱眼」</b>，对整车厂的产品定义、保险定价及责任认定框架将产生全面影响，标志中国智驾监管进入全新阶段。"
            }
          ]
        },
        {
          "company": "小鹏 / 理想",
          "company_slug": "xpeng",
          "headline_html": "<b>小鹏 + 理想：</b>组织架构加速重塑，两家公司均把「机器人」列为下阶段核心战略",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月30日</b>，小鹏集团<b>机器人业务负责人米良川离职</b>，创始人 <b>何小鹏亲自兼任</b>机器人中心及产品部负责人（新浪科技报道）。米良川在英伟达工作约 15 年，2021 年加入小鹏，此次人事变动延续了 6月10日何小鹏兼任机器人中心负责人的动作。<b>7月2日</b>，何小鹏在 MONA L03 发布会公开表示<b>中国智能驾驶已领先全球，L4/L5 将在 3-5 年内落地</b>，措辞较此前更为直接。"
            },
            {
              "label": "b",
              "content_html": "<b>7月2日</b>，理想汽车宣布新一轮<b>组织架构调整</b>，将整车与智驾职能并入研发体系，产品决策部门由 3 个缩减为 2 个，以提升智驾研发效率（电子工程专辑报道）。<b>7月3日</b>媒体进一步披露：智驾团队核心负责人 <b>范皓宇转岗至机器人研发部门</b>，李想借此为具身智能领域引入核心人才，架构精简同时为机器人赛道腾出战略空间——与小鹏同样在「智驾人才向机器人迁移」的方向上主动落子。"
            }
          ]
        },
        {
          "company": "比亚迪 / 萝卜快跑",
          "company_slug": "byd",
          "headline_html": "<b>比亚迪智驾「兜底」落地 + 萝卜快跑花旗背书：</b>国内智驾商业化信心指标走高",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>7月4日</b>，比亚迪宣布旗下全系车型标准配备智能辅助驾驶系统，<b>起价仅 1.2 万元</b>，并率先公开承诺：若因智驾系统问题导致事故，<b>厂家承担全额赔偿、不向用户追偿</b>（汽车之家报道）。这是继比亚迪 6月30日「无上限安全兜底」声明后的进一步落地，与即将出台的辅助驾驶新国标形成正向呼应，有望推动行业从「辅助驾驶免责」走向「厂家全责」的全面转型。"
            },
            {
              "label": "b",
              "content_html": "<b>7月4日</b>，花旗银行发布研报，力挺百度旗下<b>萝卜快跑</b>的全球化布局战略，并看好中国无人驾驶赛道即将迎来<b>千亿级资本热潮</b>（汽车之家报道）。在 Momenta IPO 超购 414 倍之后，这是国际大行对中国 Robotaxi 赛道发出的最新积极信号；萝卜快跑已在北京、武汉等多座城市实现全无人商业运营，花旗背书将进一步提振其海外融资能力。"
            }
          ]
        }
      ]
    }
  ]
}

os.makedirs('data/reports', exist_ok=True)

with open('data/reports/2026-W28.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Written data/reports/2026-W28.json')

with open('docs/data/weekly.json', encoding='utf-8') as f:
    weekly = json.load(f)

weekly = [w for w in weekly if w.get('week_id') not in ('W28', '2026-W28')]
weekly.insert(0, data)

with open('docs/data/weekly.json', 'w', encoding='utf-8') as f:
    json.dump(weekly, f, ensure_ascii=False, indent=2)
print(f'Written docs/data/weekly.json  (total weeks: {len(weekly)})')

with open('docs/data/weekly.json', encoding='utf-8') as f:
    json.load(f)
print('JSON OK')
