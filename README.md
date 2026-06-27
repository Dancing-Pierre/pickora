# 一念

一念是一个移动端优先的选择抽卡网站：当你不知道吃什么、喝什么、去哪玩、看什么时，先生成一组卡牌，再凭手感翻开一张。

当前仓库根目录仍保留项目代号 `pickora`，对外产品名为「一念」。

## 功能

- Vue 3 + Vite + TypeScript 单页前端
- FastAPI 后端 API
- 猫眼正在热映电影 spider 定时任务
- 手动输入 3 到 12 个选项生成卡牌
- `吃什么` / `去哪玩` / `喝什么` 通过固定分类生成候选
- `看什么` 从 `maoyan_film` 表随机抽取 `state = 1` 的正在热映电影
- 电影卡牌翻开后使用海报背景，并可再次点击查看详情
- 最近 5 组卡牌保存在浏览器 `localStorage`
- API 固定分类 allowlist、请求大小限制、每 IP 限流

## 目录结构

```text
.
├── api/                 # FastAPI 后端，负责生成选项、读取电影表、隐藏服务端密钥
├── frontend/            # Vue 前端，一念抽卡界面
├── spider/              # 猫眼电影定时采集任务
├── .claude/             # Claude Code / Trellis 本地协作配置
├── .trellis/            # Trellis 任务、规格和工作流记录
└── README.md
```
真实配置文件已通过 `.gitignore` 排除。发布时请使用各子项目的示例文件创建本地配置，不要提交真实密码。

## API 环境变量

API 独立部署时，在 `api/` 目录复制环境变量模板：

```bash
cd api
cp .env.example .env
```

填写：

```env
API_PORT=8000
DASHSCOPE_API_KEY=replace-with-your-dashscope-api-key
DASHSCOPE_MODEL=qwen-turbo
FRONTEND_ORIGIN=https://your-domain.example
AI_RATE_LIMIT_PER_MINUTE=5
AI_RATE_LIMIT_PER_HOUR=30
MAX_REQUEST_BYTES=1024
MYSQL_HOST=replace-with-your-mysql-host
MYSQL_PORT=3306
MYSQL_USER=replace-with-your-mysql-user
MYSQL_PASSWORD=replace-with-your-mysql-password
MYSQL_DATABASE=replace-with-your-mysql-database
MYSQL_CONNECT_TIMEOUT=5
```

说明：

- `DASHSCOPE_API_KEY` 只允许放在后端环境变量中，不要提交真实值。
- `MYSQL_*` 用于读取 spider 已写入的 `maoyan_film` 表。
- `看什么` 只抽取 `state = 1` 且 `name` 非空的电影；不足 6 条时返回受控错误。

## 本地开发

### 前端

```bash
cd frontend
npm install
npm run dev
```

### API

```bash
cd api
python -m venv .venv
# Windows Git Bash / Linux / macOS
. .venv/Scripts/activate || . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Docker 部署

API 只维护自己的后端容器，前端域名反向代理由外部服务处理。

```bash
cd api
cp .env.example .env
# 编辑 .env

docker compose up -d --build
```

`api/docker-compose.yml` 会：

- 默认暴露 `8000:8000`，可通过 `API_PORT` 调整宿主机端口
- 挂载外部 Docker 网络 `1panel-network`
- 使用 `host.docker.internal:host-gateway` 保持与 spider 类似的主机访问方式

## Spider 说明

spider 负责采集猫眼正在热映电影并写入 MySQL 表 `maoyan_film`。

首次部署前复制配置模板：

```bash
cd spider/volumes
cp config.example.ini config.ini
```

然后编辑 `config.ini`，填入 MySQL 和采集配置。`config.ini` 已被 `.gitignore` 忽略，不应提交。

Docker 启动：

```bash
cd spider
docker compose up -d --build
```

核心字段：

- `movieid`
- `name`
- `detail_url`
- `poster`
- `type`
- `actors`
- `release_date`
- `score`
- `ticket_buy`
- `state`

API 使用这些字段展示电影卡牌和详情。

## 安全与发布前检查

发布到 GitHub 前请确认：

- 不提交真实 `.env`。
- 不提交 spider 的真实 `config.ini`。
- 不提交 `node_modules/`、`dist/`、`__pycache__/`、日志文件。
- 不提交数据库密码、DashScope Key、生产 Token。

建议检查：

```bash
cd frontend
npm run build
```

```bash
cd api
python -m compileall app
```

```bash
cd api
docker compose config
```

## License

MIT
