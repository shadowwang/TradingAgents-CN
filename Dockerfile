# 基础镜像
FROM python:3.10-slim

# 系统依赖安装
RUN apt-get update && apt-get install -y \
    pandoc \
    wkhtmltopdf \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# Python依赖安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码复制
COPY . /app
WORKDIR /app

# 运行配置
EXPOSE 8501
CMD ["streamlit", "run", "web/app.py"]