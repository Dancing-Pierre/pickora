# Pickora

Pickora 是一个移动端优先的「选择抽卡机」网站：输入几个选项，或者点一个简单分类让 AI 生成 6 个候选，然后用卡牌抽取动画帮你快速做决定。

首版目标是简单、公开、可自部署：无登录、无数据库、本地保存最近 5 次完整选择记录。

## 功能

- Vue 3 + Vite + TypeScript 单页应用
- GSAP 游戏感卡牌洗牌 / 翻牌 / 高亮动画
- 手动输入选项：支持粘贴文本解析，也支持逐个添加标签
- 手动选项数量限制：最少 3 个，最多 12 个
- AI 生成选项：固定支持 `吃什么`、`去哪玩`、`看什么剧/电影`
- AI 每次返回 6 个候选项，然后进入抽卡
- 重抽次数：`max(1, floor(卡牌数量 / 3))`
- 重抽允许重复抽到之前结果
- 最近 5 次完整会话保存在浏览器 `localStorage`
- FastAPI 极小代理隐藏阿里百炼 / DashScope Key
- 固定分类 allowlist + 每 IP 限流，降低无登录场景下的滥用风险
- Docker Compose 自部署配置

## 安全说明

不要把真实 API Key 写进代码、README、提交历史或前端环境变量。

DashScope Key 只应该配置在服务器环境变量 `DASHSCOPE_API_KEY` 中，并由 Python API 代理在服务端调用。前端只请求 `/api/generate-options`，不会也不应该拿到真实 Key。

如果你的 Key 曾经在聊天、工单、截图或日志中暴露，请先去阿里百炼后台轮换 / 作废旧 Key，再部署本项目。

## 目录结构

```text
.
├── api/                 # FastAPI AI 代理
├── deploy/              # Nginx 配置
├── frontend/            # Vue 单页应用
├── docker-compose.yml   # 自部署编排
├── .env.example         # 环境变量示例，不包含真实密钥
├── LICENSE
└── README.md
```

## 环境变量

复制 `.env.example` 为 `.env`，再填入你自己的值：

```env
DASHSCOPE_API_KEY=replace-with-your-dashscope-api-key
DASHSCOPE_MODEL=qwen-turbo
FRONTEND_ORIGIN=https://pickora.ansion.top
AI_RATE_LIMIT_PER_MINUTE=5
AI_RATE_LIMIT_PER_HOUR=30
MAX_REQUEST_BYTES=1024
```

说明：

- `DASHSCOPE_API_KEY`：阿里百炼 / DashScope API Key。不要提交真实值。
- `DASHSCOPE_MODEL`：默认 `qwen-turbo`。
- `FRONTEND_ORIGIN`：生产环境允许访问 API 的前端域名。
- `AI_RATE_LIMIT_PER_MINUTE`：每 IP 每分钟 AI 生成次数，默认 5。
- `AI_RATE_LIMIT_PER_HOUR`：每 IP 每小时 AI 生成次数，默认 30。
- `MAX_REQUEST_BYTES`：API 请求体大小限制，默认 1024 字节。

如果没有配置 `DASHSCOPE_API_KEY`，手动抽卡仍然可用，AI 生成会提示暂未配置。

## 本地开发

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务默认会把 `/api` 代理到 `http://127.0.0.1:8000`。

### API

```bash
cd api
python -m venv .venv
# Windows Git Bash / Linux / macOS
. .venv/Scripts/activate || . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Compose 部署

```bash
cp .env.example .env
# 编辑 .env，填入服务器环境变量，尤其是 DASHSCOPE_API_KEY

docker compose up -d --build
```

默认将前端容器暴露到宿主机 `8080` 端口：

```text
http://服务器IP:8080
```

你可以在 1Panel 里使用「容器编排 / Compose」导入本仓库的 `docker-compose.yml`，并在环境变量中配置 `.env` 对应内容。随后把网站域名 `pickora.ansion.top` 反向代理到宿主机 `8080` 端口。

## 1Panel 自部署建议

1. 在服务器安装并登录 1Panel。
2. 准备域名 DNS：将 `pickora.ansion.top` 解析到服务器。
3. 在 1Panel 中创建 Compose 编排，使用本项目的 `docker-compose.yml`。
4. 配置环境变量，不要把真实 Key 写入仓库。
5. 启动编排，确认容器正常运行。
6. 创建网站 / 反向代理，把 `pickora.ansion.top` 指向 `http://127.0.0.1:8080`。
7. 配置 HTTPS 证书。
8. 访问 `https://pickora.ansion.top/health` 检查 API 健康状态。

## API 防滥用策略

首版无登录，因此防护是低摩擦方案，不是绝对防刷：

- Key 仅保存在服务端环境变量
- 前端不能传任意 prompt
- API 只接受固定分类：`food`、`play`、`movie`
- 请求体大小限制
- CORS 只允许配置的前端域名和本地开发域名
- 每 IP 默认 5 次/分钟、30 次/小时

如果上线后仍出现明显滥用，可以继续加 Cloudflare Turnstile、网关限流或登录鉴权。

## 构建检查

```bash
cd frontend
npm run build
```

```bash
cd api
python -m compileall app
```

```bash
docker compose config
```

## 页脚信息

页面底部展示：

```text
暗蚀工研科技 · 专业全栈技术服务 | © 2026 ansion.top · 保留所有权利 | 浙ICP备2025172295号-1
```

公司名称链接到 <https://www.ansion.top/>。

## License

MIT
