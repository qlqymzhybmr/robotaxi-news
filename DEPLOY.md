# GitHub Pages 部署指南

> 将 `web/` 目录部署到 GitHub Pages,访问地址:https://qlqymzhybmr.github.io/robotaxi-news/

---

## 首次部署(只做一次)

### 第 1 步:创建 GitHub 账号(已有账号跳过)

1. 打开 https://github.com/signup
2. 用邮箱注册,用户名填 `qlqymzhybmr`
3. 验证邮箱后登录

### 第 2 步:创建 public repo

1. 登录后点击右上角 "+" → "New repository"
2. Repository name 填 `robotaxi-news`
3. 选 **Public**(必须是 Public,GitHub Pages 免费版只支持 Public repo)
4. **不要**勾选 "Add a README file"(我们本地已有文件)
5. 点 "Create repository"

### 第 3 步:本地 git 初始化并推送

在 Windows 命令提示符(CMD)或 PowerShell 中,`cd` 到项目目录:

```bash
cd D:\Desktop\robotaxi-news
git init
git add -A
git commit -m "init: robotaxi-news tracking skill + web"
git branch -M main
git remote add origin https://github.com/qlqymzhybmr/robotaxi-news.git
git push -u origin main
```

> 第一次 push 时,Git 会弹出窗口让你登录 GitHub 账号(或要求 Personal Access Token)。
> 如果用 Token:GitHub → Settings → Developer settings → Personal access tokens → Generate new token,勾选 `repo` 权限。

### 第 4 步:开启 GitHub Pages

1. 打开 https://github.com/qlqymzhybmr/robotaxi-news
2. 点顶部 tab "Settings"
3. 左侧菜单找 "Pages"(在 "Code and automation" 分组下)
4. "Build and deployment" → Source 选 **"Deploy from a branch"**
5. Branch 选 **`main`**,文件夹选 **`/web`**
6. 点 "Save"

### 第 5 步:等待部署完成

- GitHub 会自动触发一次构建,约 1-3 分钟
- 刷新 Pages 设置页,顶部会出现绿色横幅:"Your site is live at https://qlqymzhybmr.github.io/robotaxi-news/"
- 打开 https://qlqymzhybmr.github.io/robotaxi-news/ 确认页面正常加载

---

## 日常发布(每次跑完 daily / weekly 后)

daily-fetch 和 weekly-report 跑完后,Claude 会提示你运行:

```bash
# 发布每日精选
git add -A && git commit -m "daily 2026-04-13" && git push

# 发布周报
git add -A && git commit -m "weekly 2026-W15" && git push
```

push 完成后约 1-2 分钟,网页自动更新。

---

## 常见问题

### 问题:打开网页显示 404

**原因**:GitHub Pages 还没部署完,或路径设置错误。

**排查步骤**:
1. 检查 Settings → Pages 是否已保存,Branch 是否是 `main`,文件夹是否是 `/web`
2. 检查 `web/index.html` 是否已经 push 到 main 分支
3. 等 5 分钟后刷新

### 问题:页面加载了但显示"暂无每日精选数据"

**原因**:数据文件是空的(`[]`),或者还没有运行过 daily-fetch。

**解决**:运行一次 daily-fetch,Claude 会自动更新 `web/data/daily.json`,然后 push 即可。

### 问题:CORS 错误(浏览器控制台报 Access-Control-Allow-Origin)

**原因**:直接用 `file://` 打开本地 HTML 文件时,浏览器阻止 fetch 本地 JSON。

**解决**:只能通过 GitHub Pages 的 `https://` 地址访问,不能直接双击本地 HTML 文件。如果要本地预览,用 VS Code 的 Live Server 插件。

### 问题:push 后页面没有更新

**原因**:浏览器缓存或 CDN 缓存延迟。

**解决**:按 `Ctrl+Shift+R`(强制刷新),或等 5-10 分钟后再试。

### 问题:git push 报错 "Authentication failed"

**原因**:GitHub 已不支持密码登录,需要 Personal Access Token。

**解决**:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token,Note 随便填,Expiration 选 No expiration(或 90 天)
3. 勾选 `repo` 权限
4. 生成后复制 token(只显示一次!)
5. 下次 git push 时,用户名填 GitHub 用户名,密码填这个 token

### 问题:每次都要输入用户名和密码

**解决**:配置 Git 记住凭据:
```bash
git config --global credential.helper store
```
然后下次输一次密码,之后不再询问。

---

## 目录结构说明

```
robotaxi-news/
└── web/                    ← GitHub Pages 从这里部署
    ├── index.html          ← 网页主文件
    └── data/
        ├── daily.json      ← 每日精选数据(Claude 自动写入)
        └── weekly.json     ← 周报数据(Claude 自动写入)
```

GitHub Pages 会把 `web/` 目录作为网站根目录,所以:
- `web/index.html` → `https://qlqymzhybmr.github.io/robotaxi-news/`
- `web/data/daily.json` → `https://qlqymzhybmr.github.io/robotaxi-news/data/daily.json`
