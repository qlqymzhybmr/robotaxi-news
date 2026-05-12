# Daily Publish Workflow（自动发布每日精选）

> **目标读者:Claude 本身**。由 daily-fetch 的 Phase 2 完成后自动串接,不需要用户手动触发。
>
> 任务:把今日 daily 文件里**所有条目（全量推送，不限 rating）**写入 `docs/data/daily.json`,供 GitHub Pages 网页展示与后续选稿使用。
>
> **⚠️ 从 2026-05-12 起执行全量推送，⭐ 一星条目也写入 JSON，不再过滤。**

---

## 公司 Slug 映射表

将公司名映射为 URL 安全的 slug(小写字母、数字、连字符):

| 公司名 | slug |
|------|------|
| Waymo | waymo |
| Tesla | tesla |
| Zoox | zoox |
| Wayve | wayve |
| Cruise | cruise |
| Uber | uber |
| Lyft | lyft |
| Grab | grab |
| Rivian | rivian |
| Lucid | lucid |
| NVIDIA | nvidia |
| Woven Planet | woven-planet |
| Motional | motional |
| 42dot | 42dot |
| MOIA | moia |
| Aurora Innovation | aurora |
| May Mobility | may-mobility |
| SWM | swm |
| Sonnet.ai | sonnetai |
| Nuro | nuro |
| Waabi | waabi |
| Tensor | tensor |
| 小马智行 | xiaoma |
| 文远知行 | wenyuan |
| 萝卜快跑 | luobo |
| 曹操出行 | caocao |
| 哈啰出行 | hello |
| 高德地图 | amap |
| 如祺出行 | ruqi |
| 享道出行 | xiangdao |
| 蔚来 | nio |
| 理想 | liauto |
| 小鹏 | xpeng |
| 小米 | xiaomi |
| 零跑 | leapmotor |
| 赛力斯 | seres |
| 极氪 | zeekr |
| 岚图 | lantu |
| 极狐 | arcfox |
| 智己 | zhiji |
| 埃安 | aion |
| 比亚迪 | byd |
| 长安 | changan |
| 一汽 | faw |
| 长城 | gwm |
| 奇瑞 | chery |
| Momenta | momenta |
| 地平线 | horizon |
| 轻舟智航 | qingzhou |
| 元戎启行 | deeproute |
| 千里科技 / 迈驰智行 | qianli |
| 毫末智行 | haomo |
| 大卓智能 | dazuo |
| 卓驭科技 | zhuoyu |
| 鸿蒙智行 | hongmeng |
| 引望智能 | yinwang |
| 商汤绝影 | sensetime |

> 如果公司名不在表中,用公司名拼音小写并去掉空格作为 slug,如 "XX科技" → "xxkeji"。

---

## 执行步骤

### 步骤 1:读取今日 daily 文件

读取 `data/daily/YYYY-MM-DD.md`(今天日期)。如果文件不存在,报错停止。

### 步骤 2:扫描并提取所有新闻条目（全量）

逐行扫描 daily 文件。识别格式:
```
- [ ] ⭐⭐⭐ **公司名:标题**
  详细内容段落...
  候选图:...
  - 权威源: [源名 日期](url)
```

**评级识别**:
- `⭐⭐⭐` → rating = 3
- `⭐⭐` → rating = 2
- `⭐` → rating = 1

**提取所有条目，不按 rating 过滤**。rating 仅作为元数据保留在 JSON 中，供网页排序和展示使用。

**⚠️ 严格规则：Daily Publish 完全忽略 rating 和勾选状态**

- **必须**：提取 daily 文件里的所有条目，无论 `[x]` / `[ ]`、⭐ / ⭐⭐ / ⭐⭐⭐
- **禁止**：因为 rating = 1 跳过某条目
- **禁止**：因为 `[ ]` 未勾选跳过某条目
- **原则**：Daily Publish 全量写入；选稿（哪些进周报）由用户在选稿 UI 或 `docs/data/selections.json` 中决定
- **违反此规则将导致低 rating 条目无法在选稿 UI 中显示**

### 步骤 2.5:发布前的硬过滤(防止旧闻污染网页)

在转换 markdown 为 JSON 之前,对每条新闻执行:

1. 读取条目里的"**原始发布日期**"字段(格式 YYYY-MM-DD)
2. 计算这个日期距离今天(当前运行日期)相隔多少天
3. **如果超过 2 天,丢弃这条,不写入 JSON**(给 ±1 天的容错,允许昨天、今天、明天的新闻)
4. 如果没有"**原始发布日期**"字段,**也丢弃**

最后输出报告:"X 条因日期不在窗口内被过滤,Y 条通过日期检查全量写入 JSON（含所有 rating）"

### 步骤 3:从 markdown 结构提取元数据

对每条提取的新闻条目:

**group 和 sub_group**:从当前所在的 `##` 标题提取:
- `## 国外 L4` → group="国外", sub_group="国外 L4"
- `## 国外出行平台` → group="国外", sub_group="国外出行平台"
- `## 国外 OEM / Tier1 / 自动驾驶技术公司` → group="国外", sub_group="国外 OEM / Tier1"
- `## 国内 L4` → group="国内", sub_group="国内 L4"
- `## 国内出行平台` → group="国内", sub_group="国内出行平台"
- `## 国内新势力 / 传统 OEM` → group="国内", sub_group="国内新势力 / 传统 OEM"
- `## 国内智驾方案商` → group="国内", sub_group="国内智驾方案商"
- `## 国内华为系 / 互联网大厂` → group="国内", sub_group="国内华为系 / 互联网大厂"

**company**:从当前所在的 `###` 标题提取。如果是合并标题(如 `### Zoox / Cruise / Wayve`),则这个 section 下一般只有 `(过去24h无相关新闻。)`,跳过。

**title**:从 `**公司名:标题**` 提取冒号后的文字(去掉加粗符号)。

**summary_html**:把条目的详细内容段落转换为 HTML:
- 把 markdown `**xxx**` 转为 `<b>xxx</b>`
- 每个自然段用 `<p>...</p>` 包裹
- 去掉 `候选图:` 行和 `- 权威源:` / `- 辅助源:` 行
- 保留 3-5 句,不压缩内容

**source_name 和 source_url**:从 `- 权威源: [源名 日期](url)` 提取:
- source_name 是链接文字(去掉日期部分,只留媒体名称)
- source_url 是括号里的 URL

**company_slug**:查映射表,找不到则用拼音规则生成。

**id**:格式 `YYYY-MM-DD-NNN`,NNN 是当天该条目的序号,从 001 开始,按文件中出现顺序编号。

### 步骤 4:读取现有 docs/data/daily.json

如果文件存在,读取为数组。如果文件是 `[]` 或不存在,视为空数组 `[]`。

### 步骤 5:插入或替换今日数据

构建今日的 entry 对象:
```json
{
  "date": "YYYY-MM-DD",
  "items": [ ...提取的条目... ]
}
```

- 如果数组里已经有 `date == 今天` 的 entry,**替换**它(重跑场景)
- 否则,**插入到数组开头**(保持日期倒序)

### 步骤 6:写回 docs/data/daily.json

**强制使用 Python 写入**，禁止用 Edit 工具直接拼 JSON 字符串：

```python
import json

# 构建好 Python 对象后，用 json.dumps 序列化——它会自动处理所有转义
entry = {
    "date": "YYYY-MM-DD",
    "items": [...]   # Python dict，字符串里的引号直接写，不需要手动加反斜杠
}

# 读取现有文件
with open("docs/data/daily.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 插入/替换
data = [e for e in data if e["date"] != entry["date"]]
data.insert(0, entry)

# 写回——json.dumps 负责所有转义，永远不会出语法错误
with open("docs/data/daily.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

**为什么必须用 Python**：Edit 工具写的是字面字符，`"又一新国家"` 里的引号会原样写进去变成非法 JSON。`json.dumps` 会自动把 `"` 转义为 `\"`，不需要人工干预。

### 步骤 6.5:写入后强制验证

每次写完立刻验证，发现错误立即停止，不要继续 commit：

```bash
python -c "import json; json.load(open('docs/data/daily.json', encoding='utf-8')); print('JSON OK')"
```

如果输出 `JSON OK` 才进入步骤 7。如果抛出 `JSONDecodeError`，报错停止，修复后重跑步骤 6。

### 步骤 7:输出提示

```
今日全量 X 条（⭐⭐⭐ x 条 / ⭐⭐ x 条 / ⭐ x 条）已写入 docs/data/daily.json。

请运行以下命令发布到 GitHub Pages:
  git add -A && git commit -m "daily YYYY-MM-DD" && git push
```

---

## 注意事项

- Daily Publish 全量写入，不管 rating 也不管用户有没有勾 `[x]`；选稿（哪些进周报）由用户在 `docs/data/selections.json` 中决定。
- 如果今日 daily 没有任何条目（文件为空）,输出提示"今日无条目,docs/data/daily.json 未更改。"
- summary_html 保留原文细节,不要压缩或改写
- **⚠️ 禁止用 Edit 工具手动拼 JSON 字符串**：必须用 Python `json.dump()` 写入，写完必须跑步骤 6.5 的验证命令，验证通过才能 commit
