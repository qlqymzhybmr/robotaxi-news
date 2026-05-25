"""Generate 2026-W20 weekly JSON artifact and publish to docs/data/weekly.json."""
import json, sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

data = {
  "week_id": "2026-W20",
  "date_range": "0512-0518",
  "title": "无人驾驶行业0512-0518重要新闻",
  "generated_at": "2026-05-18T20:00:00+08:00",
  "sections": [
    {
      "name": "国内",
      "entries": [
        {
          "company": "小鹏",
          "company_slug": "xpeng",
          "headline_html": "<b>小鹏：</b>GX今年广州启动Robotaxi商业运营；VLA 2.0大模型发布，宣称超越Tesla FSD",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月15日</b>，小鹏GX取得广州智能网联汽车道路测试牌照，公开路测累计超<b>50万公里</b>，<b>2026年</b>内将在<b>广州</b>启动Robotaxi商业运营，与<b>曹操出行</b>合作首批部署约<b>5,000辆</b>GX Robotaxi版（预计覆盖10城）；<b>2027年</b>推出Robotaxi专属经济版，去除驾驶舱冗余配置，降低单车BOM成本和运营门槛；何小鹏同步表态，预判<b>L5</b>自动驾驶将于<b>2030年</b>实现。"
            },
            {
              "label": "b",
              "content_html": "<b>5月17日</b>，正式发布第二代<b>VLA 2.0</b>（Vision-Language-Action）大模型，由副总裁<b>刘先明</b>主导，官方宣称将实现"中国最好用的自动驾驶"；VLA 2.0将视觉理解、语言推理与驾驶决策整合为端到端大模型，复杂城市路况（施工区、无结构化路段）处理能力大幅提升，<b>ArenaEV</b>在北京路况实测验证；5月14日小鹏邀请Tesla粉丝飞行<b>1万公里</b>赴华同路段对比测试，官宣接管次数更少于Tesla FSD；何小鹏在<b>轩辕奖</b>论坛表态："Robotaxi有网络效应，运营规模越大边际成本递减，是传统汽车制造不具备的价值增长模型。""
            }
          ]
        },
        {
          "company": "曹操出行",
          "company_slug": "caocao",
          "headline_html": "<b>曹操出行：</b>与上海国际汽车城战略合作，2026年嘉定100辆Robotaxi，2030年目标10万辆",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月15日</b>，与<b>上海国际汽车城</b>（嘉定区）正式签署战略合作协议，计划<b>2026年</b>内在嘉定区投入<b>100辆</b>Robotaxi商业运营，并明确提出<b>2030年</b>将车队规模扩张至<b>10万辆</b>。"
            }
          ]
        },
        {
          "company": "小马智行",
          "company_slug": "xiaoma",
          "headline_html": "<b>小马智行：</b>Robotaxi正式接入腾讯出行服务",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月12日</b>，Robotaxi正式接入<b>腾讯出行</b>服务平台，用户可通过腾讯出行App直接呼叫；此前已接入高德等平台，腾讯出行接入进一步拓展流量入口生态。"
            }
          ]
        }
      ]
    },
    {
      "name": "国外",
      "entries": [
        {
          "company": "Waymo",
          "company_slug": "waymo",
          "headline_html": "<b>Waymo：</b>全国3,791辆车队召回并OTA修复；宣告迈阿密扩张11城共1,400+平方英里；达拉斯闯红灯与亚特兰大空车绕圈事件持续发酵",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月12日</b>，<b>NHTSA</b>披露Waymo召回<b>3,791辆</b>第六代自动驾驶系统（Waymo Driver），原因是软件缺陷导致部分车辆在积水路段继续行驶，其中一辆在<b>圣安东尼奥</b>洪水期间被冲入<b>Salado Creek</b>；OTA修复已在召回公告发出前完成推送；同日，圣安东尼奥正式向全体用户开放无人驾驶服务，取消候补名单。"
            },
            {
              "label": "b",
              "content_html": "<b>5月13日</b>，官方宣布：已在<b>迈阿密</b>启动服务区扩张，并正式明确<b>奥斯汀、亚特兰大、休斯顿、旧金山湾区</b>为下一批扩张城市；扩张完成后将在<b>11</b>座城市实现服务覆盖，总面积超过<b>1,400平方英里</b>（大于罗德岛州面积）；休斯顿扩张与<b>FIFA 2026</b>世界杯举办地布局直接相关。"
            },
            {
              "label": "c",
              "content_html": "<b>5月14日</b>，<b>FOX 4</b>记者拍摄到两辆Waymo在<b>达拉斯</b>同一路口连续左转闯越红灯；Waymo回应称从传感器角度信号灯"severely dimmed（严重变暗）"导致系统未能正确识别，正在处理该感知边缘案例；事发在3,791辆积水召回完成后不到两天。"
            },
            {
              "label": "d",
              "content_html": "<b>5月15日</b>，<b>亚特兰大 Buckhead</b>住宅区出现多达<b>50辆</b>空载Waymo循环困于死胡同数小时，<b>NBC News</b>、<b>FOX 5</b>等多家媒体报道居民路堵投诉；Waymo官方称已修复路由逻辑，但<b>CBS News</b>同日播出新一批居民录像显示OTA后仍有异常；与5月12日召回引发的路由逻辑漏洞直接相关。"
            },
            {
              "label": "e",
              "content_html": "<b>5月17日</b>，NHTSA OTA召回备案追踪显示，Waymo车队从2025年5月<b>1,212辆</b>增至当前<b>3,791辆</b>，同比增幅超<b>212%</b>，自2024年2月<b>444辆</b>起实现约<b>8.5倍</b>增长，大幅领先Tesla Robotaxi车队<b>39辆</b>；迈阿密服务区同期新增<b>50平方英里</b>，总覆盖达<b>150平方英里</b>。"
            },
            {
              "label": "f",
              "content_html": "<b>5月11日</b>，<b>洛杉矶 Koreatown</b>发生Waymo翻车事故，Reddit用户发布现场视频；同日，<b>伦敦 Shoreditch</b>路段凌晨发生两起事故（无人车困于死胡同噪音扰民、乘客称车辆行为异常），当地居民随即发起请愿叫停试点，为伦敦试点启动以来首次较大规模社区抵制。"
            }
          ]
        },
        {
          "company": "Tesla",
          "company_slug": "tesla",
          "headline_html": "<b>Tesla：</b>德州Robotaxi公测"无车可用"，比利时FSD获批，NHTSA公开17起事故报告，FSD v14.3.3推送",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月12日</b>，路透社记者在<b>达拉斯</b>实测Robotaxi，原计20分钟行程因频繁遭遇"无可用车辆"，最终等待超<b>2小时</b>；服务覆盖范围受限、车辆密度不足，与Waymo服务体验差距明显；同日，拉斯维加斯目击<b>Cybercab</b>实拍照片流传。"
            },
            {
              "label": "b",
              "content_html": "<b>5月13日</b>，Tesla正式获<b>比利时</b>监管机构批准，可在该国道路上测试有监督自动驾驶（supervised FSD）；Tesla FSD在欧洲获得迄今最明确的监管许可，同期马斯克赴华推动FSD落地，欧亚双线并进。"
            },
            {
              "label": "c",
              "content_html": "<b>5月15日</b>，<b>NHTSA</b>首次公开Tesla Robotaxi自2025年7月运营以来全部<b>17起</b>事故的非脱敏叙述文本（<b>WIRED</b>深度报道）；其中<b>2起</b>由<b>电话操控员</b>（teleoperator）远程接管后操作失当致碰撞，均发生在<b>奥斯汀</b>：一起将车辆驶上路牙撞击金属围栏（唯一造成人员轻伤的事故），一起以约<b>9MPH</b>驶入施工护栏，直接质疑电话操控员机制可靠性。"
            },
            {
              "label": "d",
              "content_html": "<b>5月15日至17日</b>，FSD v14.3新增"分心自动靠边停车"功能（驾驶员持续分心时ADS主动减速靠边）；5月17日推送v14.3.3（软件版本<b>2026.14.6.6</b>）：<b>Actually Smart Summon</b>最高速从<b>6mph</b>提升至<b>8mph</b>（+33%），Summon/FSD/Robotaxi统一为同一AI模型，新增无干预里程计数器，重写AI编译器使反应时间提速<b>20%</b>。"
            }
          ]
        },
        {
          "company": "Zoox",
          "company_slug": "zoox",
          "headline_html": "<b>Zoox：</b>一周内宣布进驻4城，VP公开访谈，USA Today评测上线",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月11日</b>，一周内宣布Robotaxi服务扩展至<b>迈阿密、奥斯汀、拉斯维加斯、旧金山</b>共4座城市；Zoox采用无方向盘双向定制车型（purpose-built），与Waymo改装方案思路不同。"
            },
            {
              "label": "b",
              "content_html": "<b>5月13日</b>，自动软件副总裁<b>Marc Wimmershoff</b>接受TheRideshareGuy播客访谈，详谈purpose-built设计差异化及下一步扩张路径。"
            },
            {
              "label": "c",
              "content_html": "<b>5月15日</b>，<b>USA Today</b>记者实地免费体验，发布正面评测，服务范围同日新增站点覆盖。"
            }
          ]
        },
        {
          "company": "Wayve",
          "company_slug": "wayve",
          "headline_html": "<b>Wayve：</b>AI Driver覆盖全球500+城市里程碑；英国政府签署合作协议",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月11日</b>，AI Driver已在全球<b>500+</b>座城市完成驾驶，进入新城市几乎无需额外本地化训练数据，与Waymo深耕少数城市的精细化路线形成鲜明对比。"
            },
            {
              "label": "b",
              "content_html": "<b>5月17日</b>，<b>英国政府</b>与Wayve签署无人驾驶车辆合作协议；Wayve总部位于<b>伦敦</b>，由<b>NVIDIA、Microsoft、SoftBank</b>战略支持。"
            }
          ]
        },
        {
          "company": "Uber/Motional",
          "company_slug": "uber",
          "headline_html": "<b>Uber/Motional：</b>联邦机构调查16起碰撞事故；Motional正式上线Uber；Lucid×Nuro联合方案推进",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月12日</b>，美国联邦机构就Uber平台Robotaxi涉及的<b>16起</b>碰撞事故启动安全调查。"
            },
            {
              "label": "b",
              "content_html": "<b>5月15日</b>，Motional Robotaxi正式通过<b>Uber</b>平台向公众开放乘车服务（此前已在Lyft运营），运营市场为<b>拉斯维加斯</b>。"
            },
            {
              "label": "c",
              "content_html": "<b>5月16日</b>，<b>Lucid Motors</b>高管完成Uber×Nuro联合方案原型车首次实车体验，按计划将于<b>2026年底</b>在<b>旧金山湾区</b>上线。"
            }
          ]
        },
        {
          "company": "立法/监管",
          "company_slug": "regulation",
          "headline_html": "<b>立法/监管：</b>美国各州AV立法加速，D.C.提出高额许可费方案",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>5月12日</b>，<b>田纳西州纳什维尔</b>通过立法，明确赋予执法机构对无人驾驶汽车独立开具交通违章罚单的权力，继内华达州后美国第二个明确AV独立执法权的州级立法。"
            },
            {
              "label": "b",
              "content_html": "<b>5月13日</b>，<b>新泽西州</b>参议院委员会通过AV立法，赋予自动驾驶车辆在该州公共道路上运营的法律依据。"
            },
            {
              "label": "c",
              "content_html": "<b>5月14日</b>，<b>华盛顿D.C.</b>议会提出AV许可费方案，被法律分析机构形容为"全美代价最高的路径之一"，可能对Waymo等进入首都形成实质性经济壁垒，与田纳西、新泽西的友好立法政策形成鲜明对比。"
            }
          ]
        }
      ]
    }
  ]
}

# write to data/reports/
with open('data/reports/2026-W20.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Written data/reports/2026-W20.json')

# weekly-publish: write to docs/data/weekly.json
with open('docs/data/weekly.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Written docs/data/weekly.json')

# validate
with open('docs/data/weekly.json', encoding='utf-8') as f:
    json.load(f)
print('JSON OK')
