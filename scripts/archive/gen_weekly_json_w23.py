"""Generate 2026-W23 weekly JSON and publish to docs/data/weekly.json."""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

data = {
  "week_id": "2026-W23",
  "date_range": "0602-0608",
  "title": "无人驾驶行业0602-0608重要新闻",
  "generated_at": "2026-06-08T22:00:00+08:00",
  "sections": [
    {
      "name": "国外",
      "entries": [
        {
          "company": "Waymo",
          "company_slug": "waymo",
          "headline_html": "<b>Waymo：</b>执法危机四连发重创公关叙事，技术亮点与扩张步伐依然不停",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月3日</b>，Waymo 发布一段令人印象深刻的安全演示：<b>两辆 Waymo 无人车在高速公路上同步协调躲避逆行来车</b>，由工程师 Dmitri Dolgov 公开发布的视频迅速在社交媒体引发广泛传播，成为本周 Robotaxi 安全性最有力的公开示范。<b>6月6日</b>，Waymo 在 <b>CVPR 2026</b> 首次公开其<b>世界模型（World Model）</b>研究进展，被业界解读为进入「Genie 时代」的信号——Waymo 的感知-预测-规划管线正从基于规则走向大模型驱动。扩张层面：本周官宣进入<b>马萨诸塞州</b>和<b>萨克拉门托</b>，叠加此前底特律、坦帕、波士顿，Waymo 的全美扩张节奏并未因危机而放缓。"
            },
            {
              "label": "b",
              "content_html": "<b>6月5日至7日，Waymo 在四天内接连陷入四起「执法/紧急场景危机」</b>，成为本周最受关注的系统性事件：<br>①&nbsp;<b>6月5日</b>，达拉斯发生气体爆炸，Waymo 无人车探测到异常后停留在事故现场道路中央，消防救援车辆被迫绕行，警察最终<b>亲自接管车辆</b>方才疏通；<br>②&nbsp;<b>6月6日</b>，凤凰城一起武装嫌疑人追捕行动中，Waymo 无人车驶入<b>警方封锁区</b>，成为 48 小时内第二起妨碍执法事件；<br>③&nbsp;<b>6月7日</b>，奥克兰一起入室盗窃案嫌疑人乘坐 Waymo 逃离现场，由于无法实时拦截，<b>警方至今无嫌疑人</b>，成为全美首例 Robotaxi 涉案协助犯罪逃逸；<br>④&nbsp;<b>同日</b>，达拉斯橡树崖区公寓爆炸后，Waymo 又一次停留在救援通道，<b>WFAA 视频</b>清晰记录了无人车长时间占据道路的过程。<br>四起事件在一周内密集爆发，暴露的是同一个结构性问题：Waymo 在非常规场景（执法/紧急事件）下的<b>主动退出机制、远程协助能力与执法部门数据配合</b>三项能力均存在明显缺口，行业监管框架的滞后已无法掩盖。"
            },
            {
              "label": "c",
              "content_html": "<b>6月2日</b>，伊利诺伊州议会通过<b>网约车司机工会集体谈判法案</b>，Waymo 进驻芝加哥等伊州城市的计划随即受阻——这是本周继执法摩擦之外，Waymo 扩张遭遇的另一类阻力：<b>劳工政治</b>。本周还涌现出两个运营层面的有趣信号：洛杉矶出现<b>峰值车费 $16.60/英里、每小时 $130</b>，为平台历史最高记录，折射出需求激增与供给不足并存的紧张态势；Waymo 宣布与 <b>B2U</b> 合作，将退役 Robotaxi 动力电池重新用于电网储能，是 Robotaxi 行业首个系统性「车-网」全生命周期管理方案。"
            }
          ]
        },
        {
          "company": "Tesla",
          "company_slug": "tesla",
          "headline_html": "<b>Tesla：</b>奥斯汀无监督 Robotaxi 正式落地里程碑，与路透社安全统计丑闻同日爆发",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月4日是 Tesla Robotaxi 历史上的关键节点</b>：特斯拉在奥斯汀正式推出<b>完全无安全员监督</b>的 Robotaxi 服务，并同步将服务区扩大一倍——这是特斯拉「每辆 Model Y 都是潜在 Robotaxi」愿景的第一次真正意义上的公开兑现，无论技术成熟度争议如何，商业化里程碑本身的意义不可否认。同日，<b>Reuters 发布深度调查报道</b>，指控特斯拉使用<b>错误的统计方法虚报 FSD 安全数据</b>——这不是情绪化的安全质疑，而是具体指向数据造假的新闻调查，对 Tesla Robotaxi 公信力形成迄今最直接的挑战，两则消息在同一天发酵，形成强烈对比。"
            },
            {
              "label": "b",
              "content_html": "<b>6月6日</b>，Tesla 向<b>内华达州</b>申请 Robotaxi 运营许可，<b>第一年目标 5,000 辆</b>——相当于当前奥斯汀在线车队的 119 倍，是迄今最激进的单城市扩张表态，凸显特斯拉对「电动车即 Robotaxi」的硬件规模化逻辑的信心。<b>6月5日</b>披露的 <b>FSD 全球待审批国家完整名单</b>显示欧洲和亚洲是下阶段重点，海外监管攻坚已进入具体执行阶段。<b>6月8日</b>，特斯拉展示了旧金山至帕洛阿尔托往返 FSD 演示，叠加奥斯汀扩展和圣安东尼奥私人部署计划，PR 节奏明显加密。与此同时，多辆 <b>CyberCab 现身亚特兰大服务中心</b>，暗示下一个开城城市的准备工作已在进行。"
            },
            {
              "label": "c",
              "content_html": "一个值得关注的矛盾信号：<b>6月8日</b>，Yahoo Autos 报道显示 Tesla 奥斯汀 Robotaxi 已将 ODD 扩展至全市，但批评者援引数据指出实际在线<b>车队规模正在收缩</b>——覆盖范围扩大与车辆数减少并存，被解读为在安全压力下的策略性稀释操作，而非真正意义上的规模化。这与上周（W22）首次出现的「车队萎缩」信号一致，是 Tesla Robotaxi 商业化进程中最需要持续跟踪的量化指标。"
            }
          ]
        },
        {
          "company": "Uber",
          "company_slug": "uber",
          "headline_html": "<b>Uber：</b>欧洲双城落地 + 5 亿押注 Nuro + CEO 预言 900 万司机失业，平台分发护城河持续深挖",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月2日</b>，<b>Uber + Autobrains + NVIDIA</b> 宣布在<b>德国慕尼黑</b>落地 Robotaxi 服务，成为欧洲首个以 Uber 品牌运营的无人驾驶服务，NVIDIA 的参与将其 Cosmos 物理 AI 生态与欧洲 Robotaxi 商业场景直接打通。<b>6月3日</b>，<b>文远知行 + Uber</b> 在<b>西班牙马德里</b>正式启动商业试点，6月8日确认全面上线——在同一周内，Uber 完成了<b>欧洲双城布局</b>，且两个城市分别依托不同的 AV 技术伙伴，印证了 Uber「技术不可知论」的平台分发战略：不押注单一 AV 技术，而是同时与 Waymo、Motional、文远知行、Autobrains 等多家合作，以分发能力构建护城河。"
            },
            {
              "label": "b",
              "content_html": "<b>6月4-5日</b>，<b>Uber 对 Nuro 的投资计划</b>完整披露：近 <b>5 亿美元</b>支持 Nuro 在湾区及多城市部署<b>3.5 万辆 Robotaxi</b>，是本周 AV 行业最大单笔资金承诺。Uber 同期还专门部署 <b>500 辆定制 EV</b> 在城市中持续收集驾驶数据，专门用于 Robotaxi 训练——这意味着 Uber 不再只是出行平台，而是在主动建设自己的 <b>AI 训练数据护城河</b>，未来谈判筹码将更强。"
            },
            {
              "label": "c",
              "content_html": "<b>6月6日</b>，Uber CEO Dara Khosrowshahi 发表迄今最直接的「自我革命」声明：<b>无人驾驶将让全球约 900 万网约车司机失业</b>。此表态一方面是 Uber 向资本市场传递 Robotaxi 战略决心的公关动作，另一方面也引发了监管机构和劳工组织的高度关注——Uber 在构建 Robotaxi 分发平台的同时，也在主动划定「人类司机终将被替代」的历史叙事，这一双重角色将成为其监管博弈的长期复杂背景。"
            }
          ]
        },
        {
          "company": "第二梯队",
          "company_slug": "others",
          "headline_html": "<b>GM/Cruise 回归 + 大众 LA 上路 + NVIDIA 物理 AI 加速：</b>第二梯队本周多点突破",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月5日</b>，彭博社独家报道：<b>通用汽车正在秘密回聘逾百名前 Cruise 员工</b>，Cruise 2023 年旧金山事故后解散 Robotaxi 部门已过去 18 个月，这一动作被解读为 GM 押注「AI 浪潮下重新切入 AV 赛道」的信号。与明确对外宣布的战略不同，秘密回聘意味着 GM 在技术储备层面的低调布局——它留有宝贵的技术积累和大量原班人马，一旦条件成熟可快速重组。"
            },
            {
              "label": "b",
              "content_html": "<b>6月7日</b>，<b>大众 ID. Buzz Robotaxi</b> 版本正式出现在洛杉矶街头，欧洲汽车制造商在美国 Robotaxi 市场正式「露面」。ID. Buzz 标志性的面包车外形具有天然的品牌辨识度，大众正尝试以差异化的外形设计在被 Waymo Jaguar 和 Tesla CyberCab 主导的市场中建立独特存在。"
            },
            {
              "label": "c",
              "content_html": "<b>6月2日</b>，<b>NVIDIA GTC 台北</b>发布 <b>Alpamayo 2 Super</b> L4 开放基础模型与<b>Cosmos 3 物理 AI</b> 平台，直接面向 Robotaxi 和机器人训练场景。NVIDIA 的定位日趋清晰：不造车、不造 AV，而是成为 Robotaxi 时代的「算力+AI 基础设施」底座，同周与 Uber 慕尼黑项目的联动也印证了这一战略落地节奏。"
            }
          ]
        }
      ]
    },
    {
      "name": "国内",
      "entries": [
        {
          "company": "中国市场",
          "company_slug": "china",
          "headline_html": "<b>中国市场：</b>小马智行撞车逃逸全责认定引爆法律争议，L3 梯队持续扩容，Momenta 布局长三角",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>6月7日</b>（事件发生于6月1日），<b>小马智行无人车变道刹车引发碰撞后径直驶离</b>，未停车处置，交警介入后判定小马智行无人车承担<b>事故全部责任</b>。视频证据显示无人车在事故发生后没有任何停车意图，直接离开现场。此事件引发的核心法律争议是：当无人车发生事故时，「停车、保护现场、报警」等驾驶人法定义务由谁承担？现行《道路交通安全法》中驾驶人义务框架在完全无人驾驶场景下的适用性存在根本性空白。这是中国 Robotaxi 商业化阶段迄今最直接的法律合规挑战。"
            },
            {
              "label": "b",
              "content_html": "<b>6月6日</b>，<b>岚图汽车（东风集团）</b>旗下泰山车型正式发布 <b>L3 自动驾驶系统</b>，继长安深蓝、北汽极狐之后，成为国内<b>首批 L3 准入资质梯队</b>的第三家。东风集团通过岚图品牌的加入，标志着中国三大传统汽车央企（一汽/东风/长安）中，东风已完成 L3 赛道布局。随着首批 L3 车型在 2026 年陆续上市，监管机构对事故责任认定的执法实践将成为行业最大的观测指标。"
            },
            {
              "label": "c",
              "content_html": "<b>6月3日/8日</b>，<b>Momenta</b> 获得<b>无锡市</b>自动驾驶道路测试许可并正式开展路测。Momenta 以「飞轮数据」战略著称，通过向 OEM 量产智驾系统持续积累场景数据，无锡路测是其长三角布局的重要一步。在当前国内 Robotaxi 监管趋于审慎（参考萝卜快跑 3 月停运后的行业冷却期）的背景下，Momenta 选择以更低调的量产智驾路径积累数据资产，是一种相对稳健的商业化路径。"
            }
          ]
        }
      ]
    }
  ]
}

os.makedirs('data/reports', exist_ok=True)

with open('data/reports/2026-W23.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Written data/reports/2026-W23.json')

with open('docs/data/weekly.json', encoding='utf-8') as f:
    weekly = json.load(f)

weekly = [w for w in weekly if w.get('week_id') not in ('W23', '2026-W23')]
weekly.insert(0, data)

with open('docs/data/weekly.json', 'w', encoding='utf-8') as f:
    json.dump(weekly, f, ensure_ascii=False, indent=2)
print(f'Written docs/data/weekly.json  (total weeks: {len(weekly)})')

with open('docs/data/weekly.json', encoding='utf-8') as f:
    json.load(f)
print('JSON OK')
