# AItestdemo 开发指南

## 项目概述

AItestdemo 是一个基于人工智能的测试用例生成平台，支持文档上传、RAG检索和思维导图输出。

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- PostgreSQL - 主数据库
- ChromaDB - 向量数据库
- Redis - 缓存和会话
- Gemini API - AI模型

### 前端
- Vue.js 3 - 前端框架
- Element Plus - UI组件库
- Pinia - 状态管理
- D3.js - 数据可视化
- Vite - 构建工具

### 基础设施
- Docker & Docker Compose - 容器化
- Nginx - 反向代理
- MinIO - 对象存储

## 开发环境搭建

### 1. 环境要求
- Docker 20.0+
- Docker Compose 2.0+
- Node.js 18+ (可选，用于本地前端开发)
- Python 3.11+ (可选，用于本地后端开发)

### 2. 克隆项目
```bash
git clone <repository-url>
cd AItestdemo
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
# 特别是 GEMINI_API_KEY
```

### 4. 启动开发环境
```bash
# 使用脚本启动
chmod +x scripts/start.sh
./scripts/start.sh dev up

# 或直接使用 docker-compose
docker-compose -f docker-compose.dev.yml up --build
```

### 5. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- MinIO控制台: http://localhost:9001

## 项目结构

```
AItestdemo/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心功能
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── services/       # API服务
│   │   ├── store/          # 状态管理
│   │   └── router/         # 路由配置
│   ├── package.json
│   └── Dockerfile
├── data/                   # 数据存储
├── scripts/                # 脚本文件
├── docs/                   # 文档
└── docker-compose.yml      # Docker编排
```

## 开发工作流

### 1. 后端开发

#### 本地开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 代码规范
```bash
# 代码格式化
black app/
isort app/

# 代码检查
flake8 app/

# 运行测试
pytest
```

#### API开发
1. 在 `app/api/v1/endpoints/` 中创建新的API端点
2. 在 `app/schemas/` 中定义Pydantic模式
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/models/` 中定义数据模型

### 2. 前端开发

#### 本地开发
```bash
cd frontend
npm install
npm run dev
```

#### 代码规范
```bash
# 代码格式化
npm run format

# 代码检查
npm run lint
```

#### 组件开发
1. 在 `src/components/` 中创建可复用组件
2. 在 `src/views/` 中创建页面组件
3. 在 `src/services/` 中添加API调用
4. 在 `src/store/` 中管理状态

### 3. 数据库迁移

```bash
# 创建迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

### 4. 测试

#### 后端测试
```bash
cd backend
pytest tests/ -v --cov=app
```

#### 前端测试
```bash
cd frontend
npm run test
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看自动生成的API文档。

## 核心功能模块

### 1. 文档管理
- 文件上传和存储
- 文档内容提取（文本、PDF、Excel、图片OCR）
- 文档状态跟踪

### 2. RAG系统
- 文档分块和向量化
- 相似度搜索
- 上下文检索

### 3. AI测试用例生成
- 基于Gemini API的文本生成
- 测试用例结构化输出
- 批量生成支持

### 4. 思维导图
- 测试用例可视化
- 交互式编辑
- 多格式导出

## 部署

### 开发环境
```bash
./scripts/start.sh dev up
```

### 生产环境
```bash
./scripts/deploy.sh production deploy
```

## 故障排除

### 1. 常见问题

#### 数据库连接失败
- 检查数据库服务是否启动
- 确认连接字符串正确
- 检查网络连接

#### ChromaDB连接问题
- 确认ChromaDB服务正常运行
- 检查端口配置
- 查看ChromaDB日志

#### Gemini API错误
- 验证API密钥是否正确
- 检查API配额
- 确认网络连接

### 2. 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 重置环境
```bash
# 清理所有容器和数据
./scripts/start.sh prod reset
```

## 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

## 许可证

MIT License