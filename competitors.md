# Robotaxi Competitor & Keywords

> **维护说明**：这是竞品与关键词唯一维护入口。直接增删行即可。
> 公司维护：每家公司一行，公司名后面可以用括号标注归属（如 `极氪 (吉利)`）。
> 关键词维护：在文末 `## 搜索关键词` 区域维护，全局关键词会拼接到每家公司的查询中。
> 分组顺序就是 daily-fetch 时的搜索顺序，也间接反映重要性优先级（前面的组更受关注）。
> **重点公司**用 `⭐` 标记，daily-fetch 时按每语种最多抓取 10 条；普通公司按每语种最多抓取 5 条。

---

## 国外组

### L4 / Robotaxi 头部
- ⭐ Waymo
- ⭐ Tesla
- ⭐ Zoox
- ⭐ Wayve
- Cruise

### 出行平台
- ⭐ Uber
- ⭐ Lyft
- ⭐ Grab

### 美国 OEM
- Rivian
- Lucid
- GM

### 欧洲 / 日韩 OEM
- BMW
- Benz
- Audi
- Volkswagen
- Stellantis

### 自动驾驶技术公司
- Woven Planet (Toyota)
- Motional (Hyundai)
- 42dot (Hyundai)
- MOIA (Volkswagen)
- Tensor
- Aurora Innovation
- May Mobility
- SWM
- Sonnet.ai
- Nuro
- Waabi
- Mobileye
- Aptiv

### 国外 Tier1 / 零部件供应商
- ⭐ NVIDIA
- Bosch
- Continental
- ZF
- TRW
- Denso
- Valeo
- Magna

---

## 国内组

### L4 / Robotaxi 头部
- ⭐ 小马智行 (Pony.ai)
- ⭐ 文远知行 (WeRide)
- ⭐ 萝卜快跑 (Apollo Go / 百度)

### 出行平台
- ⭐ 曹操出行
- ⭐ 哈啰出行
- 高德地图
- 如祺出行
- 享道出行

### 新势力 OEM
- ⭐ 蔚来 (NIO)
- ⭐ 理想 (Li Auto)
- ⭐ 小鹏 (XPeng)
- 小米 (Xiaomi Auto)
- 零跑 (Leapmotor)
- 赛力斯 (Seres)
- 威马

### 传统 OEM 新能源品牌
- 极氪 (吉利)
- 岚图 (东风)
- 极狐 (北汽)
- 智己 (上汽)
- 埃安 (广汽)
- 比亚迪 (BYD)
- 长安
- 一汽
- 长城
- 奇瑞

### 第三方智驾供应商
- ⭐ Momenta
- ⭐ 地平线 (Horizon Robotics)
- ⭐ 轻舟智航
- ⭐ 元戎启行 (DeepRoute)
- 提雅智行
- 纵目科技
- 追势科技
- 智驾科技 MAXIEYE
- 佑驾创新 MINIEYE
- 驭势科技
- 鉴智机器人 (四维图新)

### 主机厂自研智驾
- ⭐ 千里科技 / 迈驰智行 (吉利)
- 毫末智行 (长城)
- 大卓智能 (奇瑞)
- 卓驭科技 (一汽 / 大疆)
- 福瑞泰克 Freetech (吉利)
- 零束科技 (上汽)
- 赛可智能 (上汽)
- 友道智途 (上汽)

### 华为系 / 其他
- ⭐ 鸿蒙智行 (华为)
- ⭐ 引望智能 (华为)
- 商汤绝影 (商汤)

### 互联网 / 平台生态
- 百度
- 字节
- 阿里
- 腾讯
- 美团

---

## 搜索关键词

### 全局中文关键词
- 自动驾驶
- 无人驾驶
- 智驾
- Robotaxi
- 无人出租车
- 自动驾驶出租车
- 智能驾驶
- 城市 NOA
- 端到端
- 智驾大模型
- 车路云一体化
- 高阶智驾
- L2+
- L3
- L4
- 智能网联汽车
- 自动泊车
- OTA
- 无图方案
- 激光雷达

### 全局英文关键词
- autonomous driving
- self-driving
- robotaxi
- driverless
- autonomous vehicle
- FSD
- ADAS
- urban NOA
- end-to-end
- foundation model
- HD map
- mapless
- lidar
- teleoperation
- safety driver
- permit
- deployment
- pilot program
- expansion
- recall

### 可选事件关键词（按需临时开启）
- 融资 / IPO / listing
- partnership / JV
- regulatory approval
- safety incident
- earnings
- software update

---

## 直接订阅 RSS（官方博客 / 新闻室）

> 已验证可用。由 `python_rss_fetch.py` 直接抓取，不经过 Google News，适合公司官方公告类内容。
> 格式：`公司名 | 地区 | 是否重点 | RSS URL`

- NVIDIA | overseas | ⭐ | https://nvidianews.nvidia.com/cats/driving.xml
- Aurora Innovation | overseas | | https://aurora.tech/rss.xml
- Not A Tesla App | overseas | ⭐ | https://www.notateslaapp.com/rss
- The Driverless Digest | overseas | ⭐ | https://thedriverlessdigest.com/feed
- Robonomics | overseas | | https://robonomics.substack.com/feed

---

## X（Twitter）RSS 订阅（via 自部署 RSSHub）

> RSSHub 实例：https://rsshub-production-8ec4.up.railway.app
> 认证变量：`TWITTER_AUTH_TOKEN`（Railway Variables 已配置）
> Cookie 约每 1-2 个月失效，失效后到 Railway Variables 更新 `TWITTER_AUTH_TOKEN` 值即可。
> 格式：`公司名 | 地区 | 是否重点 | RSS URL`

- Waymo | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/waymo
- Tesla | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/Tesla
- Tesla Robotaxi | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/teslarobotaxi
- Zoox | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/zoox
- Wayve | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/wayve_ai
- Uber | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/uber
- Lyft | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/lyft
- Grab | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/grabsg
- Aurora Innovation | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/aurora_inno
- Nuro | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/nuro
- Mobileye | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/Mobileye
- NVIDIA | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/nvidia
- Rivian | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/Rivian
- Motional | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/MotionalDrive
- May Mobility | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/May_Mobility
- Waabi | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/waabi_ai
- Aptiv | overseas | | https://rsshub-production-8ec4.up.railway.app/twitter/user/Aptiv
- 小马智行 (Pony.ai) | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/ponyai_tech
- 文远知行 (WeRide) | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/WeRide_ai
- 萝卜快跑 (Apollo Go / 百度) | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/BaiduApollo
- 蔚来 (NIO) | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/NIOGlobal
- 小鹏 (XPeng) | overseas | ⭐ | https://rsshub-production-8ec4.up.railway.app/twitter/user/XPENG_Global

---

## X（Twitter）官方账号

> RSSHub 公共实例（rsshub.app）已封锁 Twitter 路由（2025 年起），需自部署 RSSHub 并配置 Twitter Cookie 才能使用。
> 账号已验证，待自部署接入后直接启用。
> 自部署参考：https://docs.rsshub.app/deploy/  免费平台：Vercel / Railway / Render

| 公司 | X 账号 | 地区 | 重点 |
|------|--------|------|------|
| Waymo | @waymo | overseas | ⭐ |
| Tesla | @Tesla | overseas | ⭐ |
| Tesla Robotaxi | @teslarobotaxi | overseas | ⭐ |
| Zoox | @zoox | overseas | ⭐ |
| Wayve | @wayve_ai | overseas | ⭐ |
| Uber | @uber | overseas | ⭐ |
| Lyft | @lyft | overseas | ⭐ |
| Grab | @grabsg | overseas | ⭐ |
| Aurora Innovation | @aurora_inno | overseas | |
| Nuro | @nuro | overseas | |
| Mobileye | @Mobileye | overseas | |
| NVIDIA | @nvidia | overseas | ⭐ |
| Rivian | @Rivian | overseas | |
| Motional | @MotionalDrive | overseas | |
| May Mobility | @May_Mobility | overseas | |
| Waabi | @waabi_ai | overseas | |
| Aptiv | @Aptiv | overseas | |
| Pony.ai（小马智行） | @ponyai_tech | china | ⭐ |
| WeRide（文远知行） | @WeRide_ai | china | ⭐ |
| Baidu / Apollo | @BaiduApollo | china | ⭐ |
| NIO（蔚来） | @NIOGlobal | china | ⭐ |
| XPeng（小鹏） | @XPENG_Global | china | ⭐ |

---

## 社区 / 媒体 RSS（Reddit 热帖）

> Reddit 原生 RSS 免认证，覆盖自动驾驶社区分享的新闻、事故、政策帖。
> 抓取时间窗口与其他来源一致（前日 09:00 ~ 当日 09:00 北京时间）。
> 内容过滤：标题须含自动驾驶相关关键词，纯社交/调侃帖自动跳过。

- Reddit/SelfDrivingCars | overseas | | https://www.reddit.com/r/SelfDrivingCars/new/.rss
- Reddit/Waymo | overseas | | https://www.reddit.com/r/Waymo/new/.rss
- Reddit/teslamotors | overseas | | https://www.reddit.com/r/teslamotors/new/.rss

---

## 元数据
- 总计：约 89 家公司
- ⭐ 重点公司：23 家（每语种最多抓取 10 条）
- 普通公司：约 66 家（每语种最多抓取 5 条）
- 最后更新：2026-05-12
