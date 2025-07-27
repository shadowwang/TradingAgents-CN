# 使用官方Python镜像
FROM python:3.10-slim-bookworm

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 复制项目文件
COPY . /app/app/
COPY ../tradingagents /app/tradingagents/
COPY ../config /app/config/

# 暴露端口
EXPOSE 6006

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6006/v1/get_stock_data/000001 || exit 1

# 启动命令
CMD ["python", "/app/app/main.py"]