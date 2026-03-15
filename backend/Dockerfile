# 多阶段构建 - 后端 Dockerfile
# 用于 Railway/Render 等平台部署

# 阶段 1: 构建依赖
FROM python:3.11-slim as builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 阶段 2: 运行时
FROM python:3.11-slim

WORKDIR /app

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# 从构建阶段复制依赖
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY . .

# 设置环境变量
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
