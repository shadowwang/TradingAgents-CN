# FastAPI应用Docker配置说明

## 概述
本文档说明如何使用Docker运行FastAPI股票数据查询应用。

## 文件结构
```
app/
├── main.py          # FastAPI应用主文件
├── Dockerfile       # Docker构建文件
└── README.md        # 本说明文档
```

## Docker配置

### 1. Dockerfile配置
- 基于Python 3.10-slim-bookworm镜像
- 安装所需的Python依赖
- 暴露6006端口
- 包含健康检查配置

### 2. docker-compose.yml配置
已在项目根目录的docker-compose.yml中添加了fastapi-app服务：
- 服务名：fastapi-app
- 端口映射：6006:6006
- 依赖MongoDB和Redis服务
- 包含日志和健康检查配置

## 使用方法

### 方法1：使用docker-compose（推荐）
```bash
# 启动所有服务（包括FastAPI应用）
docker-compose up -d

# 仅启动FastAPI应用及其依赖
docker-compose up fastapi-app -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs fastapi-app
```

### 方法2：单独构建和运行
```bash
# 构建镜像
docker build -f app/Dockerfile -t tradingagents-fastapi:latest .

# 运行容器
docker run -d \
  --name tradingagents-fastapi \
  -p 6006:6006 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/logs:/app/logs \
  tradingagents-fastapi:latest
```

## API测试
应用启动后，可以通过以下方式测试：

```bash
# 测试股票数据API
curl -X GET "http://localhost:6006/v1/get_stock_data/000001"

# 查看API文档
curl http://localhost:6006/docs
```

## 环境变量
应用使用以下环境变量：
- `PYTHONUNBUFFERED=1`：确保Python输出不缓冲
- `PYTHONDONTWRITEBYTECODE=1`：不生成.pyc文件
- `PYTHONPATH=/app`：设置Python路径
- `TZ=Asia/Shanghai`：设置时区
- 数据库连接配置（MongoDB、Redis）

## 健康检查
容器包含健康检查配置，会定期检查API是否正常响应。

## 日志配置
- 容器日志：使用json-file驱动，最大100MB，保留3个文件
- 应用日志：输出到/app/logs目录，与宿主机同步

## 故障排除

### 1. 端口冲突
如果6006端口被占用，可以修改docker-compose.yml中的端口映射：
```yaml
ports:
  - "6007:6006"  # 将宿主机端口改为6007
```

### 2. 依赖服务未启动
确保MongoDB和Redis服务正常运行：
```bash
docker-compose up mongodb redis -d
```

### 3. 权限问题
确保日志目录有写入权限：
```bash
mkdir -p logs
chmod 755 logs
```

## 开发模式
开发时可以使用卷挂载实现代码热更新：
```yaml
volumes:
  - ./app:/app/app
  - ./tradingagents:/app/tradingagents
```

## 生产部署建议
1. 使用环境变量管理敏感配置
2. 配置适当的资源限制
3. 使用外部数据库服务
4. 配置负载均衡和反向代理
5. 定期备份数据和日志