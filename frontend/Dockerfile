# 多阶段构建 - 前端 Dockerfile
# 用于 Vercel 部署或独立 Docker 部署

# 阶段 1: 依赖安装
FROM node:20-alpine AS deps

WORKDIR /app

# 复制 package 文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci

# 阶段 2: 构建
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 设置环境变量
ENV NEXT_TELEMETRY_DISABLED=1

# 构建应用
RUN npm run build

# 阶段 3: 运行时
FROM node:20-alpine AS runner

WORKDIR /app

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制必要的文件
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 设置环境变量
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

USER nextjs

EXPOSE 3000

# 启动命令
CMD ["node", "server.js"]
