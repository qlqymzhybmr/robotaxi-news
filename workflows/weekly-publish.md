# Weekly Publish Workflow (线 A — 自动发布周报)

> **目标读者:Claude 本身**。由 weekly-report 的步骤 11 自动串接,不需要用户手动触发。
>
> 任务:把 `data/reports/YYYY-Wxx.json`(weekly-report 步骤 8.5 生成的副产物)写入 `docs/data/weekly.json`,供 GitHub Pages 网页展示。

---

## 执行步骤

### 步骤 1:确定本周 week_id

根据当前周报覆盖范围确定:
- week_id 格式:`YYYY-Wxx`,xx 是 ISO 周数(按周一所在的周)
- 例:本周一是 2026-04-13,week_id = "2026-W15"

### 步骤 2:读取 JSON 副产物

读取 `data/reports/YYYY-Wxx.json`(weekly-report 步骤 8.5 生成的)。

如果文件不存在,报错:"weekly-report 步骤 8.5 未执行或未生成 JSON 副产物,请先运行 weekly-report。"

### 步骤 3:读取现有 docs/data/weekly.json

如果文件存在,读取为数组。如果是 `[]` 或不存在,视为空数组 `[]`。

### 步骤 4:插入或替换

- 如果数组里已经有 `week_id == 本周 week_id` 的 entry,**替换**它
- 否则,**插入到数组开头**(保持周次倒序,最新周在前)

### 步骤 5:写回 docs/data/weekly.json

格式化为易读的 JSON(2空格缩进)。

### 步骤 6:输出提示

```
本周周报(YYYY-Wxx)已写入 docs/data/weekly.json。

请运行以下命令发布到 GitHub Pages:
  git add -A && git commit -m "weekly YYYY-Wxx" && git push
```

---

## 注意事项

- weekly-publish 直接使用 weekly-report 生成的 JSON 副产物(步骤 8.5),不需要重新处理数据
- 如果用户重跑了 weekly-report,重跑 weekly-publish 会替换掉旧数据(正常行为)
