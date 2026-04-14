# Weekly Report Workflow

> **目标读者:Claude 本身**。把过去一周(上周二 ~ 本周一)daily 里被标记为重要的条目合成一份 OneNote 兼容的 HTML 周报。
>
> 用户触发:"生成本周周报" / "weekly report" / "做这周的简报"

---

## 前置条件

开始之前检查:
- `data/daily/` 里有上周二 ~ 本周一共 7 份 daily 文件(至少 5 天)
- 如果条件不足,提示用户:"本周期内只有 X 天的 daily 文件,可能是实习生漏跑了几天。是否仍然继续生成周报?"

---

## 执行步骤

### 步骤 1:确定周范围

- **默认目标**:覆盖**上周二 ~ 本周一**共 7 天的周报。**以周一作为周报的结尾**,不是开头。
- 例子:今天是 2026 年 4 月 13 日(周一),那周报覆盖 4 月 7 日(上周二)到 4 月 13 日(本周一)
- 用户触发"生成本周周报"时默认就是这个范围。如果用户明确说"生成上周周报",则覆盖**上上周二 ~ 上周一**
- 文件名格式:`data/reports/YYYY-Wxx.html`,其中 Wxx 是 ISO 周数(按周一所在的周)
- 标题格式:`无人驾驶行业MMDD-MMDD重要新闻`,MMDD 是上周二到本周一的日期(例:`0407-0413`)

### 步骤 2:收集所有勾选条目

扫描 `data/daily/` 里**上周二 ~ 本周一共 7 份** daily 文件:
- 提取所有前面标记为 `[x]` 的条目(Long 划过重点的)
- 忽略 `[ ]` 的条目(未被选中)
- 记录每条的:公司名、日期、事件摘要、详细内容、候选图 URL、源链接、评级

把所有条目汇总到一个**内部列表**。

### 步骤 3:第二轮重要性筛选

**这一步是 Long 明确要求的——写周报时对 daily 的勾选再做一次筛选和合并。**

- 默认信任 Long 的勾选,但有两种情况需要调整:
  1. **勾选数过多**(超过 12 条主条目):砍掉 ⭐⭐ 中的次要条目,保留最重要的 8-10 条
  2. **发现重复**:同一事件被多个来源报道并且 Long 都勾了,合并成一条
- 筛选规则参考 `important-examples.md`
- **宁少不多**:Long 的风格是高密度简报,不是大杂烩

### 步骤 4:按公司聚合 + 合并多事件

- 把条目按**公司名**分组
- 如果一家公司有 2+ 条事件:
  - 按事件类型分(区域扩张 / 技术发布 / 商业化 / 融资 / 事故)
  - 同类事件**合并成一个主条目**,headline 用分号串联,子条目用 `a./b./c.` 展开
  - 不同类事件**保持分开**的主条目
  - 参考 `style-guide.md` 里的"多事件公司"结构

### 步骤 5:排序

**全局排序**:
1. **分区**:国内 section 在前,国外 section 在后
2. **分区内**:按重要性(⭐⭐⭐ > ⭐⭐ > ⭐),同级别按公司重点程度(参考 competitors.md 的 ⭐ 标记和 style-guide.md 里的公司顺序)
3. 同公司同类事件内部:按日期正序(早的在前)

### 步骤 6:按 style-guide 生成中文文本

**严格按 `style-guide.md` 的所有规则写**,重点:
- 每条以日期开头:`X月X日,...`(不加年份,不加"消息")
- 公司名后用中文全角冒号 `:`
- 加粗只用于事实元素(数字、地名、产品名、监管动作)
- 禁用所有评论性词汇、填充词、AI 典型句式
- 原文数字、英文名、专有名词逐字保留
- 不出现链接

**每条写完后自检一遍**:
- 逐句读,如果某句话删掉不影响事实传达,就删掉
- 检查是否出现了 style-guide.md 的禁用词
- 检查冒号是否是中文全角

### 步骤 7:处理图片(可选,不强求)

**总原则**:图片是锦上添花,**不强制**。最终周报里实习生还会在 OneNote 里手动调整图片,所以这一步只需要给出**合理的初始候选**。

**默认策略**:
- 对**区域扩张/开城**类事件:**默认尝试配 1 张图**(优先服务区地图 / 车辆在当地街景的图)
- 对**重大技术发布/产品发布**类事件:**默认尝试配 1 张图**(优先产品/系统官方渲染图)
- **其他类型**(融资、合作、监管、人事等):**默认不配图**,除非 daily 文件里有特别明显的好图候选
- **事故/安全类事件**:**绝不配图**(避免画面过于敏感)

**操作步骤**:
- 对符合"默认配图"条件的主条目,从 daily 文件里读取对应新闻的 `候选图:` 行记录的 URL
- 如果有多个候选,选 1 张(优先官方源,如 waymo.com / cnevpost.com 这种)
- 用 `web_fetch` 简单验证 URL 是否可用(失败就跳过,不替换)
- **不要每条都配图**。一份周报通常 2-4 张图,过多反而干扰阅读
- 实习生在 OneNote 里可以**自行替换、增加、删除**任何图片,这是预期内的人工修改空间

### 步骤 8:生成 OneNote 兼容 HTML

**关键原则**:
- **所有样式都是 inline**(`style="..."` 直接挂在元素上),不要用 `<style>` 块
- **缩进用 inline `margin-left`**,不要用嵌套列表
- 子条目用 `<p style="margin-left: 36px">` 段落,里面手写 `a./b./c.` 前缀
- 图片用 `<img src="URL" style="max-width: 500px;">` 直接引用在线 URL
- 图注用 italic `<p>` 段落

**HTML 模板**(参考 v3 格式):

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>无人驾驶行业MMDD-MMDD重要新闻</title>
</head>
<body style="font-family: 'Microsoft YaHei', '微软雅黑', sans-serif; font-size: 15px; line-height: 1.7; color: #222; max-width: 760px; margin: 24px auto; padding: 0 20px;">

<h1 style="font-size: 20px; color: #1a73e8; border-bottom: 1px solid #1a73e8; padding-bottom: 6px;">无人驾驶行业MMDD-MMDD重要新闻</h1>

<h2 style="font-size: 17px; color: #000; margin-top: 28px;">国内</h2>

<ol style="padding-left: 24px;">
  <li style="margin-bottom: 16px;">
    <b>公司名:单事件标题或多事件串联 headline</b>

    <!-- 如果是单事件,直接跟正文段落 -->
    <!-- 如果是多事件,下面是 a./b./c. 子条目 -->

    <p style="margin-left: 36px; margin-top: 10px; margin-bottom: 10px;">
      <b>a. X月X日</b>,事件 A 的详细内容,包含<b>加粗的事实元素</b>。
    </p>

    <!-- 可选的图片,放在子条目之间 -->
    <p style="margin-left: 36px; text-align: center; margin-top: 8px; margin-bottom: 4px;">
      <img src="https://..." alt="图片描述" style="max-width: 500px; width: 100%; height: auto;">
    </p>
    <p style="margin-left: 36px; text-align: center; font-style: italic; color: #666; font-size: 13px; margin-top: 0;">
      图注文字
    </p>

    <p style="margin-left: 36px; margin-top: 10px; margin-bottom: 10px;">
      <b>b. X月X日</b>,事件 B 的详细内容。
    </p>
  </li>
</ol>

<h2 style="font-size: 17px; color: #000; margin-top: 28px;">国外</h2>

<ol style="padding-left: 24px;">
  <li style="margin-bottom: 16px;">
    ...
  </li>
</ol>

</body>
</html>
```

**特别注意**:
- `<ol>` 的 `padding-left` 必须 inline,因为 OneNote 会剥掉 CSS 类
- 子条目的 `margin-left: 36px` 必须 inline
- 不要用 `<ul>` 嵌套 `<ol>`,OneNote 对嵌套列表的处理不稳定
- 不要用 `<style>` 块,即使它更优雅

### 步骤 8.5:生成 JSON 副产物(线 A 使用)

在生成 OneNote HTML 的同时(复用步骤 2-7 的内部数据),生成一份结构化 JSON 供网页展示使用。

**数据来源**:不经过步骤 3 的第二轮人工勾选筛选,改为直接使用所有 **rating ≥ 2** 的条目(含勾选和未勾选)。

**按以下 schema 序列化**:

```json
{
  "week_id": "YYYY-Wxx",
  "date_range": "MMDD-MMDD",
  "title": "无人驾驶行业MMDD-MMDD重要新闻",
  "generated_at": "YYYY-MM-DDTHH:mm:ss+08:00",
  "sections": [
    {
      "name": "国内",
      "entries": [
        {
          "company": "公司名",
          "company_slug": "参考 daily-publish.md 的映射表",
          "headline_html": "<b>公司名:</b>单事件标题或多事件串联 headline",
          "sub_items": [
            {
              "label": "a",
              "content_html": "<b>X月X日</b>,详细内容..."
            }
          ]
        }
      ]
    },
    {
      "name": "国外",
      "entries": [ ... ]
    }
  ]
}
```

**格式要点**:
- sections 固定两个:"国内" 在前,"国外" 在后
- headline_html 和 content_html 中的加粗用 `<b>` 标签
- 单事件公司也用 sub_items,只放一条,label 为 "a"
- generated_at 用 ISO 8601 格式,北京时间(+08:00)
- company_slug 参考 `workflows/daily-publish.md` 的映射表

**写入文件**:`data/reports/YYYY-Wxx.json`

---

### 步骤 9:自检

生成后按 style-guide.md 的"校验清单"逐条过一遍:

- [ ] 标题格式是否为 `无人驾驶行业MMDD-MMDD重要新闻`?
- [ ] 国内排在国外前面?
- [ ] 每条都以日期开头?
- [ ] 公司名后是中文全角冒号?
- [ ] 有没有"标志着"、"据悉"等禁用词?
- [ ] 每条有没有评论性总结?
- [ ] 数字、英文原文是否逐字保留?
- [ ] 加粗是否只用于事实元素?
- [ ] 是否没有出现链接?
- [ ] 排序是否国内→国外、重点公司优先?
- [ ] 图片 URL 是否都验证过可用?

如果发现问题,修正后再写文件。

### 步骤 10:写入文件 + 呈现给用户

- 写入 `data/reports/YYYY-Wxx.html`
- 用 `present_files` 工具把文件呈现给用户
- 告诉用户下一步操作:

```
周报已生成:data/reports/2026-W15.html

请按以下步骤粘贴到 OneNote:
1. 双击 HTML 文件用浏览器打开
2. Ctrl+A 全选 → Ctrl+C 复制
3. 在 OneNote 新建一页 → Ctrl+V 粘贴
4. OneNote 会自动嵌入图片,保留加粗和缩进
5. 手动微调文字、替换/补充图片
6. 整页截图,发老板

本次周报统计:
- 国内 X 条主条目(涉及 Y 家公司)
- 国外 Z 条主条目(涉及 W 家公司)
- 配图 N 张
```

### 步骤 11:自动串接 weekly-publish(线 A)

步骤 10 完成后,**不等用户说话**,直接按 `workflows/weekly-publish.md` 的流程执行。

把步骤 8.5 生成的 `data/reports/YYYY-Wxx.json` 写入 `web/data/weekly.json`。

完成后在步骤 10 的结束消息里追加:

```
线 A 网页发布:本周周报(YYYY-Wxx)已写入 web/data/weekly.json。
发布请运行:git add -A && git commit -m "weekly YYYY-Wxx" && git push
```

---

## 常见问题处理

### 勾选条目太少(<5 条)
- 不要硬凑。直接生成简短版周报
- 提醒用户:"本周期(上周二~本周一)只有 X 条标记为重要,可能是 daily 漏查或这周本身新闻少。建议检查 daily 文件,或者人工补几条到 daily 里再重跑周报。"

### 勾选条目太多(>15 条)
- 按步骤 3 的第二轮筛选逻辑收紧
- 如果还是多,优先淘汰 ⭐⭐ 中的次要条目,保留 ⭐⭐⭐ 和头部公司
- 最终建议控制在 8-12 条主条目

### 同一事件在多份 daily 里都被勾(重复)
- 去重,保留信息更完整的那条
- 合并多条的候选图 URL 和源链接

### 图片 URL 全部验证失败
- 不配图,生成纯文本版周报
- 在结束消息里提示:"本次未配图(候选图 URL 全部验证失败),请在 OneNote 里手动添加"

### 某天 daily 文件缺失
- 用户可能漏跑了某天的 daily(忘记/请假/临时出差)
- 周报正常生成,但在结束消息里**明确提示**:"⚠️ X月X日的 daily 文件不存在,本周报可能漏掉这天的新闻。下次请记得每天跑一次 daily-fetch,包括周末。"

### 日期跨年(12 月跨 1 月)
- 标题格式保持 `MMDD-MMDD` 不变,例如 `1229-0104`
- 每条新闻仍然用 `X月X日,...` 不加年份
