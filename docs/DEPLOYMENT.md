# AdSense Evaluator 部署文档

本文档介绍如何将 AdSense Evaluator 部署到生产环境。

---

## 目录

1. [本地开发部署](#本地开发部署)
2. [Docker Compose 部署](#docker-compose-部署)
3. [后端部署（Railway/Render）](#后端部署 railwayrender)
4. [前端部署（Vercel）](#前端部署-vercel)
5. [环境变量配置](#环境变量配置)
6. [数据库迁移](#数据库迁移)
7. [生产环境注意事项](#生产环境注意事项)

---

## 本地开发部署

### 前置要求

- Python 3.11+
- Node.js 20+
- Git

### 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可选）
export SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-openai-api-key"

# 运行服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

### 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 设置环境变量
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 运行开发服务器
npm run dev
```

访问 http://localhost:3000 查看应用。

---

## Docker Compose 部署

适合本地完整环境测试或小型生产部署。

### 步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/skystmm/adsense-evaluator.git
   cd adsense-evaluator
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置必要的环境变量
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **查看日志**
   ```bash
   docker-compose logs -f
   ```

5. **访问应用**
   - 前端：http://localhost:3000
   - 后端 API: http://localhost:8000
   - API 文档：http://localhost:8000/docs

### 停止服务

```bash
docker-compose down
```

### 重置数据

```bash
docker-compose down -v  # 删除所有数据卷
```

---

## 后端部署（Railway/Render）

### Railway 部署

1. **安装 Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **登录 Railway**
   ```bash
   railway login
   ```

3. **创建新项目**
   ```bash
   railway init
   ```

4. **添加后端服务**
   ```bash
   cd backend
   railway up
   ```

5. **配置环境变量**
   ```bash
   railway variables set SECRET_KEY="your-secret-key"
   railway variables set OPENAI_API_KEY="your-openai-api-key"
   railway variables set DATABASE_URL="postgresql://..."
   ```

6. **查看部署**
   ```bash
   railway open
   ```

### Render 部署

1. **登录 Render 控制台**
   访问 https://render.com

2. **创建新 Web Service**
   - 连接 GitHub 仓库
   - 选择 `backend` 目录作为 Root Directory
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **配置环境变量**
   在 Render 控制台中添加：
   - `SECRET_KEY`
   - `OPENAI_API_KEY`
   - `DATABASE_URL`
   - `PORT` (Render 自动设置)

4. **部署**
   点击 "Create Web Service"，等待部署完成。

---

## 前端部署（Vercel）

### 使用 Vercel CLI

1. **安装 Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录 Vercel**
   ```bash
   vercel login
   ```

3. **部署**
   ```bash
   cd frontend
   vercel
   ```

4. **配置环境变量**
   在 Vercel 控制台中添加：
   - `NEXT_PUBLIC_API_URL`: 后端 API 地址（如 https://your-backend.railway.app）

5. **生产部署**
   ```bash
   vercel --prod
   ```

### 使用 GitHub 集成

1. **登录 Vercel 控制台**
   访问 https://vercel.com

2. **导入项目**
   - 点击 "Add New Project"
   - 选择 GitHub 仓库
   - 设置 Root Directory 为 `frontend`

3. **配置构建设置**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **添加环境变量**
   - `NEXT_PUBLIC_API_URL`: 后端 API 地址

5. **部署**
   点击 "Deploy"，等待构建完成。

---

## 环境变量配置

### 后端环境变量

| 变量名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `SECRET_KEY` | 是 | JWT 签名密钥（生产环境请使用强随机字符串） | `your-secret-key-change-in-production` |
| `OPENAI_API_KEY` | 否 | OpenAI API 密钥（用于 AI 建议生成） | `sk-...` |
| `DATABASE_URL` | 否 | 数据库连接字符串（默认 SQLite） | `sqlite:///./adsense_evaluator.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 否 | Token 过期时间（分钟） | `30` |
| `PORT` | 否 | 服务端口 | `8000` |

### 前端环境变量

| 变量名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `NEXT_PUBLIC_API_URL` | 是 | 后端 API 地址 | `https://api.yourdomain.com` |

### 生成安全密钥

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

---

## 数据库迁移

### SQLite（默认）

SQLite 会自动创建表，无需手动迁移。

### PostgreSQL（生产推荐）

1. **安装 PostgreSQL 依赖**
   ```bash
   pip install psycopg2-binary
   ```

2. **创建数据库**
   ```sql
   CREATE DATABASE adsense_evaluator;
   CREATE USER adsense_user WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE adsense_evaluator TO adsense_user;
   ```

3. **配置 DATABASE_URL**
   ```
   postgresql://adsense_user:your-password@localhost:5432/adsense_evaluator
   ```

4. **使用 Alembic 迁移（可选）**
   ```bash
   # 初始化 Alembic
   alembic init alembic
   
   # 配置 alembic.ini
   # 创建迁移脚本
   alembic revision --autogenerate -m "Initial migration"
   
   # 应用迁移
   alembic upgrade head
   ```

---

## 生产环境注意事项

### 安全

1. **修改默认密钥**
   - 务必更改 `SECRET_KEY`
   - 使用强随机字符串（至少 32 字符）

2. **启用 HTTPS**
   - 使用 Let's Encrypt 免费证书
   - 或使用云平台提供的 HTTPS

3. **CORS 配置**
   - 在 `backend/main.py` 中限制允许的来源
   - 仅允许生产域名访问

4. **速率限制**
   - 考虑添加 API 速率限制（如使用 slowapi）
   - 防止滥用和 DDoS 攻击

### 性能

1. **数据库优化**
   - 生产环境使用 PostgreSQL
   - 添加适当的索引
   - 配置连接池

2. **缓存**
   - 使用 Redis 缓存评估结果
   - 减少重复爬取

3. **静态资源**
   - 使用 CDN 服务前端静态资源
   - 启用 Gzip/Brotli 压缩

### 监控

1. **日志**
   - 配置结构化日志
   - 使用日志聚合服务（如 ELK、Datadog）

2. **健康检查**
   - `/health` 端点已提供
   - 配置云平台健康检查

3. **错误追踪**
   - 集成 Sentry 或类似服务
   - 及时捕获和处理错误

### 备份

1. **数据库备份**
   - 定期备份 SQLite 文件或 PostgreSQL 数据库
   - 使用云平台自动备份功能

2. **报告备份**
   - 定期备份 `reports/` 目录
   - 考虑使用云存储（S3、OSS 等）

---

## 故障排查

### 后端无法启动

```bash
# 查看日志
docker-compose logs backend

# 检查依赖
pip install -r requirements.txt

# 测试数据库连接
python -c "from models.database import init_db; init_db()"
```

### 前端无法连接后端

1. 检查 `NEXT_PUBLIC_API_URL` 是否正确
2. 确认后端 CORS 配置允许前端域名
3. 检查网络连接和防火墙

### PDF 生成失败

1. 确保安装了 reportlab: `pip install reportlab`
2. 检查中文字体是否可用
3. 查看后端日志获取详细错误信息

---

## 更新部署

### Docker Compose

```bash
# 拉取最新代码
git pull

# 重新构建并重启
docker-compose up -d --build
```

### Railway/Render

推送代码到 GitHub 后会自动触发重新部署。

### Vercel

推送代码到 GitHub 后会自动触发重新构建和部署。

---

## 联系支持

如有部署问题，请提交 Issue 或联系开发团队。

**GitHub**: https://github.com/skystmm/adsense-evaluator
