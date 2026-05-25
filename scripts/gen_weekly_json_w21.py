"""Generate 2026-W21 weekly JSON and publish to docs/data/weekly.json."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

data = {
  "week_id": "2026-W21",
  "date_range": "0519-0525",
  "title": "无人驾驶行业0519-0525重要新闻",
  "generated_at": "2026-05-25T21:00:00+08:00",
  "sections": [
    {
      "name": "国外",
      "entries": [
        {
          "company": "Waymo",
          "company_slug": "waymo",
          "headline_html": "<b>Waymo：</b>「危机周」——洪水连续被困、全美高速停运、乘客困车1小时；与此同时扩张步伐未停",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月19日</b>，亚特兰大居民区「死胡同」问题持续发酵——车队反复涌入安静街区并困于尽头，Automotive News 报道社区投诉升温；同日 11Alive 曝出 Waymo 与市政合作的「路坑追踪试点」数据被市政方弃而不用；圣卡洛斯（San Carlos）一辆 Waymo 撞上消防栓，Reddit 附图曝光。上述事件叠加此前 NHTSA <b>3,800 辆</b>强制召回（积水路段软件缺陷），令 Waymo 一周多次负面报道同时在案。"
            },
            {
              "label": "b",
              "content_html": "<b>5月20-21日</b>，大亚特兰大地区爆发暴洪，一辆 Waymo 驶入深度积水路段搁浅、乘客受困，视频在 WSB-TV、11Alive、AJC 大范围传播。Waymo 随即宣布<b>暂停大亚特兰大全部商业运营</b>；官方解释「遭遇积水时主动停车保护乘客」符合安全逻辑，但在极端天气下造成「乘客被锁车内」的舆论危机，截至 5月22日上午服务仍未恢复。"
            },
            {
              "label": "c",
              "content_html": "<b>5月21-23日</b>，Waymo 宣布在全美范围内<b>暂停所有高速公路（Freeway）自动驾驶接送服务</b>，原因是 Robotaxi 在施工区临时标线路段反复无法通行，属主动安全降级决定。SF Chronicle、LA Times、NBC Bay Area、TechCrunch 等主流媒体密集跟进；同日德克萨斯（达拉斯/休斯顿/奥斯汀/圣安东尼奥）和纳什维尔再遭暴雨，多城同时停运，Startup Fortune 评论：「Waymo 的洪水暂停再次证明 Robotaxi 仍然有天气问题没有解决。」"
            },
            {
              "label": "d",
              "content_html": "<b>5月24日</b>，三起事件叠加出现：① Yahoo Autos 报道一名女性乘客被两辆 Waymo 以异常路由方式困住<b>近1小时</b>，拨打 911 后赶到的警察对无人车束手无策，调侃「难道要和幽灵争论吗？」；② Reddit 详细记录停车场无限循环边缘案例——感知到入口封堵却路由逻辑强制重试，乘客被迫取消；③ CBS San Francisco 报道湾区夫妇称所乘 Waymo 穿越施工区超速，随后遭警察追踪。"
            },
            {
              "label": "e",
              "content_html": "<b>扩张动态（积极面）</b>：5月19日，Lyft 在纳什维尔 BNA 机场附近建设专属 Waymo 维护调度中心；5月20日，「Ojai」新测试车型现身达拉斯，旧金山湾区服务范围再度扩张；5月20日，Waymo 披露借助 Google DeepMind <b>Genie 3</b> 合成稀有场景（积水、施工、异常停车等）训练数据，结合 Google 街景的「街景接地」方案已全球化部署。"
            }
          ]
        },
        {
          "company": "Tesla",
          "company_slug": "tesla",
          "headline_html": "<b>Tesla：</b>FSD Supervised 正式入华；欧洲扩张+Cybercab 发布；马斯克「年底全面普及」承诺存疑",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月18-19日</b>，马斯克在以色列特拉维夫 Smart Mobility Summit 公开表示，无监督 FSD 将于<b>2026年底</b>在美国「全面普及」。然而现实是：全美无监督运营车辆合计仅 <b>38辆</b>（奥斯汀/达拉斯/休斯顿），奥斯汀同期曝出<b>两起 Robotaxi 碰撞事故</b>数据。Electrek 标题直接注明「——再一次」，显示市场对其频繁推迟习以为常。"
            },
            {
              "label": "b",
              "content_html": "<b>5月20-21日</b>，<b>FSD Supervised 正式进入中国市场</b>——延迟多年后终于落地，此前受制于数据监管和高精地图要求。同日<b>立陶宛</b>获批成为欧洲第二个 FSD 国家（首个为爱沙尼亚），Tesla 正以逐国审批模式渗透欧洲。FSD Supervised 入华意义在于开始合规积累中国本土数据，为未来无监督版铺路；国内竞争对手（华为乾崑、小鹏 VLA 2.0、理想等）已高度本土化，Tesla FSD 的在华表现是关键观察点。"
            },
            {
              "label": "c",
              "content_html": "<b>5月22日</b>，Tesla 宣布欧洲 FSD 正式切换为<b>纯订阅制</b>（取消一次性买断），与北美模式统一；欧洲监督版 FSD 仅上线数日便突破 <b>2000万公里</b>里程大关，用户采用速度远超预期。FSD 新版本实测评价总体正面——决策流畅、接管次数少，但部分测评者指出跟车偏近、对切入反应宽松，引发「激进化」安全争议。"
            },
            {
              "label": "d",
              "content_html": "<b>5月24日</b>，<b>Tesla Cybercab 完成正式发布上市</b>；同日 Reddit 用户在旧金山湾区斯坦福大学附近目击并拍到道路测试中的 Cybercab，是其在德克萨斯 Gigafactory 外被目击测试的最新记录，测试范围加速扩张。<b>5月25日</b>，FSD 展示新能力——遭遇停靠警车时自动减速让行，显示执法车辆识别与社会规则理解能力提升。"
            }
          ]
        },
        {
          "company": "Uber",
          "company_slug": "uber",
          "headline_html": "<b>Uber：</b>重返 AV 领域自有车队部署；Waymo 合作关系存疑",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月21日</b>，The Verge 头条报道：Uber 宣布将在内部重新部署<b>自有自动驾驶车辆</b>，用于非 Robotaxi 场景（内部运营测试），而非直接面向乘客的无人叫车服务。这是 Uber 自 <b>2018年</b>出售 ATG 自动驾驶部门给 Aurora 后，首次以自有 AV 车辆身份重返该领域，引发 r/Waymo 社区热帖「Uber-Waymo 合作是否走向终结？」的讨论。Uber 的自有 AV 能力建设路径与其对第三方（Waymo、Zoox）的依赖程度，值得持续追踪。"
            },
            {
              "label": "b",
              "content_html": "<b>5月20日</b>，一起社交媒体热议事件：一名执行 Uber 订单的 Tesla 车主在高速公路上<b>入睡约20分钟</b>，期间 FSD Supervised 持续运行并将乘客安全送达目的地。事件引发争议——支持者认为证明 FSD 已达实用水平；反对者指出监督式 FSD 的前提是清醒驾驶员在场，此次属违规使用，是 Tesla 降低驾驶员监控强度政策调整时机的警示。"
            }
          ]
        }
      ]
    },
    {
      "name": "国内",
      "entries": [
        {
          "company": "小鹏",
          "company_slug": "xpeng",
          "headline_html": "<b>小鹏：</b>Robotaxi 量产落地周——GX 下线、路测曝光、GX 上市、广州下半年承诺，纯视觉路线全面押注",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月18日</b>，小鹏汽车宣布旗下首款量产 Robotaxi 在<b>广州工厂</b>正式下线——基于 GX 平台全栈自研，搭载 <b>4颗自研图灵 AI 芯片（3000TOPS，全球量产车端最高算力）</b>及 <b>VLA 2.0</b>（Vision-Language-Action）端到端大模型，是继 Waymo（谷歌系）、Zoox（亚马逊系）、Cruise（通用系）之后，全球主流 OEM 中率先完成 Robotaxi 量产下线的里程碑；与萝卜快跑（改装车）、小马智行（SUV 改装）相比，GX Robotaxi 是<b>中国首款从量产平台正向设计的 L4 Robotaxi</b>。"
            },
            {
              "label": "b",
              "content_html": "<b>5月19日</b>，小鹏 Robotaxi 车队路测画面首次被媒体曝光，相关负责人首次公开确认「<b>已路测数月</b>」，但具体里程及接管率未披露。Bloomberg、electrive.com、Interesting Engineering 等国际主流媒体密集跟进，将小鹏 Robotaxi 定位为「Tesla FSD 的直接中国市场挑战者」。"
            },
            {
              "label": "c",
              "content_html": "<b>5月20日</b>，民用版小鹏 GX 正式发布上市，起售价 <b>26.98万元</b>，全系标配 800V 超充 + 全场景 ADAS。何小鹏在发布会上再次确认：Robotaxi 版 GX 将于 <b>2026年下半年</b>在广州开启示范运营，定位无人驾驶商业化首站。小鹏 G7 同期在上海城区实测 VLA 2.0，被评价为「可与华为乾崑智驾一较高下」。"
            },
            {
              "label": "d",
              "content_html": "<b>5月22日</b>，何小鹏在媒体采访中高调宣称「<b>汽车已不需要激光雷达</b>」，全押注纯视觉路线——这与 Waymo、小马智行等 L4 头部公司坚持激光雷达的主流路线形成正面对撞。GX 全系不配激光雷达，成本可显著降低，但安全冗余和恶劣天气感知能力存疑。Yahoo Finance 等随即重审 XPEV 估值逻辑，Robotaxi 运营时间线成为核心变量。"
            },
            {
              "label": "e",
              "content_html": "<b>5月25日</b>，小鹏明确承诺：<b>广州用户将于2026年下半年可通过网约车平台打到无人驾驶出租车</b>——给出具体城市（广州）和时间节点（2026年下半年），是国内 OEM 系迄今最明确的 Robotaxi 商业落地公开承诺之一。"
            }
          ]
        },
        {
          "company": "文远知行 (WeRide)",
          "company_slug": "weride",
          "headline_html": "<b>文远知行：</b>+ Grab 新加坡开放公众商业化——东南亚首个无人驾驶出行服务",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月22日</b>，文远知行与东南亚超级应用 <b>Grab</b> 宣布，在<b>新加坡</b>正式对普通公众开放 Robotaxi 商业运营——用户可直接通过 Grab App 叫车，乘坐文远知行自动驾驶车辆出行，无需邀请码。这是<b>东南亚首个面向普通用户全开放的无人驾驶出行商业服务</b>，也是文远知行继广州、阿联酋阿布扎比之后的第三个商业化市场，亦是首个东南亚城市。新加坡是东南亚 AV 监管体系最为成熟的城市，此次落地将对周边国家产生示范效应，或加速整个东南亚地区的 Robotaxi 监管开放进程。"
            }
          ]
        }
      ]
    }
  ]
}

import os
os.makedirs('data/reports', exist_ok=True)

# write to data/reports/
with open('data/reports/2026-W21.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Written data/reports/2026-W21.json')

# weekly-publish: read existing array, prepend W21, write back
with open('docs/data/weekly.json', encoding='utf-8') as f:
    weekly = json.load(f)

# remove existing W21 if any
weekly = [w for w in weekly if w.get('week_id') != 'W21' and w.get('week_id') != '2026-W21']
weekly.insert(0, data)

with open('docs/data/weekly.json', 'w', encoding='utf-8') as f:
    json.dump(weekly, f, ensure_ascii=False, indent=2)
print(f'Written docs/data/weekly.json  (total weeks: {len(weekly)})')

# validate
with open('docs/data/weekly.json', encoding='utf-8') as f:
    json.load(f)
print('JSON OK')
