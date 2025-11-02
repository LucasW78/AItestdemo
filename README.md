# AItestdemo - AI测试用例生成平台

一个基于人工智能的测试用例生成平台，支持文档上传、RAG检索和思维导图输出。

## 🌟 功能特性

- 📄 **多格式文件支持** - 支持 txt, pdf, xls, xlsx, jpg, jpeg, png 等多种文件格式
- 🔍 **OCR图片文字识别** - 使用 Tesseract 进行高精度图片文字提取
- 🧠 **RAG智能检索** - 基于 ChromaDB 的向量相似度搜索
- 🤖 **AI驱动生成** - 使用 Google Gemini API 生成高质量测试用例
- 🎯 **交互式思维导图** - 基于 D3.js 的可视化思维导图
- 📱 **响应式界面** - 基于 Vue.js 3 和 Element Plus 的现代化 UI
- ⚡ **实时处理** - WebSocket 支持的实时进度跟踪
- 🔐 **安全认证** - JWT token 认证和权限管理

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.11+** - 主要编程语言
- **FastAPI** - 高性能 Web 框架
- **PostgreSQL** - 主数据库
- **ChromaDB** - 向量数据库（RAG检索）
- **Redis** - 缓存和会话存储
- **Gemini API** - AI 模型服务
- **MinIO** - 对象存储服务

### 前端技术栈
- **Vue.js 3** - 前端框架
- **Element Plus** - UI 组件库
- **D3.js** - 数据可视化
- **Pinia** - 状态管理
- **TypeScript** - 类型安全

## 🚀 快速开始

### 系统要求

- **操作系统**: Linux/macOS/Windows
- **Docker**: 20.0+
- **Docker Compose**: 2.0+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 10GB 可用空间

### 一键部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd AItestdemo

# 2. 复制环境配置
cp .env.example .env

# 3. 编辑配置文件，添加 Gemini API Key
nano .env

# 4. 启动所有服务
docker-compose up -d

# 5. 等待服务启动完成（约2-3分钟）
docker-compose logs -f
```

### 环境配置

在 `.env` 文件中配置以下必要参数：

```bash
# AI 服务配置
GEMINI_API_KEY=your_gemini_api_key_here

# 应用配置
SECRET_KEY=your_secret_key_here
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/aidemo
REDIS_URL=redis://localhost:6379/0

# 文件存储配置
MAX_FILE_SIZE=50MB
UPLOAD_PATH=/app/uploads

# ChromaDB 配置
CHROMA_DB_PATH=/app/data/chroma_db
```

#### 获取 Gemini API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录您的 Google 账号
3. 点击 "Create API Key"
4. 复制生成的 API Key 到 `.env` 文件中

### 服务访问地址

启动成功后，可以通过以下地址访问：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **API文档(ReDoc)**: http://localhost:8000/redoc

## 📖 详细使用指南

### 1. 文档上传与管理

#### 支持的文件格式
- **文本文档**: `.txt`
- **PDF文档**: `.pdf`
- **Excel表格**: `.xls`, `.xlsx`
- **图片文件**: `.jpg`, `.jpeg`, `.png`

#### 上传步骤
1. 访问前端应用 http://localhost:3000
2. 点击"文档管理"页面
3. 拖拽文件到上传区域或点击选择文件
4. 等待文件处理完成（OCR、文本提取）
5. 处理完成后可在文档列表中查看

#### 文件大小限制
- 单个文件最大：50MB
- 同时上传文件数：最多10个

### 2. 测试用例生成

#### 基本流程
1. **选择文档**: 在文档列表中选择要分析的文档
2. **配置参数**:
   - 测试类型：功能测试、性能测试、安全测试等
   - 复杂度：简单、中等、复杂
   - 生成数量：1-50个测试用例
   - 目标平台：Web、移动端、API等
3. **开始生成**: 点击"生成测试用例"按钮
4. **查看结果**: 实时查看生成进度和结果

#### 高级配置
```json
{
  "test_type": "functional",
  "complexity": "medium",
  "count": 20,
  "target_platform": "web",
  "include_negative_cases": true,
  "include_edge_cases": true,
  "custom_requirements": "用户登录、权限验证、数据处理"
}
```

### 3. 思维导图可视化

#### 功能特点
- **交互式节点**: 点击节点展开/折叠子节点
- **多种布局**: 层次结构、径向布局、力导向布局
- **导出功能**: PNG、SVG、PDF 格式导出
- **实时编辑**: 支持节点内容编辑和样式调整

#### 使用方法
1. 在测试用例列表中选择要可视化的用例
2. 点击"生成思维导图"按钮
3. 选择布局方式和显示选项
4. 与思维导图进行交互操作
5. 使用导出功能保存结果

### 4. RAG智能检索

#### 检索功能
- **语义搜索**: 基于文档内容的智能匹配
- **关键词搜索**: 支持布尔查询和模糊匹配
- **相似度过滤**: 可调整相似度阈值
- **结果排序**: 按相关性和时间排序

#### 搜索技巧
- 使用具体的关键词而非宽泛词汇
- 可以使用自然语言描述搜索需求
- 结合多个关键词提高搜索精度
- 使用引号进行精确匹配

## 🔧 开发指南

### 本地开发环境

#### 后端开发
```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 启动数据库（如果使用Docker）
docker-compose up -d postgres redis chromadb

# 6. 运行数据库迁移
alembic upgrade head

# 7. 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发
```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env.local
# 编辑环境变量

# 4. 启动开发服务器
npm run dev
```

### 项目结构详解

```
AItestdemo/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/            # API 路由
│   │   │   └── endpoints/     # 具体端点
│   │   │       ├── documents.py    # 文档管理
│   │   │       ├── test_cases.py   # 测试用例
│   │   │       └── mind_maps.py    # 思维导图
│   │   ├── core/              # 核心处理模块
│   │   │   ├── ocr_processor.py    # OCR处理
│   │   │   ├── file_processor.py   # 文件处理
│   │   │   └── rag_pipeline.py     # RAG流程
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── tests/                 # 测试文件
│   ├── requirements.txt       # Python依赖
│   └── main.py               # 应用入口
├── frontend/                  # Vue.js 前端
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/            # 页面视图
│   │   ├── services/         # API服务
│   │   ├── store/            # 状态管理
│   │   └── router/           # 路由配置
│   ├── public/               # 静态资源
│   ├── package.json          # Node.js依赖
│   └── vite.config.ts        # Vite配置
├── scripts/                  # 部署脚本
│   ├── start.sh             # 启动脚本
│   ├── deploy.sh            # 部署脚本
│   └── init-db.sql          # 数据库初始化
├── data/                    # 数据存储
│   ├── documents/           # 文档文件
│   ├── chroma_db/          # 向量数据库
│   └── temp/               # 临时文件
├── docker-compose.yml       # 生产环境
├── docker-compose.dev.yml   # 开发环境
└── README.md               # 项目文档
```

### 代码规范

#### 后端代码规范
- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 使用 **flake8** 进行代码检查
- 使用 **mypy** 进行类型检查

```bash
# 代码格式化
black app/
isort app/

# 代码检查
flake8 app/
mypy app/
```

#### 前端代码规范
- 使用 **ESLint** 进行代码检查
- 使用 **Prettier** 进行代码格式化
- 使用 **TypeScript** 进行类型检查

```bash
# 代码检查和格式化
npm run lint
npm run format
npm run type-check
```

## 📚 API 文档

### 主要 API 端点

#### 文档管理
```http
# 上传文档
POST /api/v1/documents/upload
Content-Type: multipart/form-data

# 获取文档列表
GET /api/v1/documents/

# 删除文档
DELETE /api/v1/documents/{document_id}
```

#### 测试用例生成
```http
# 生成测试用例
POST /api/v1/test_cases/generate
Content-Type: application/json

{
  "document_ids": ["doc1", "doc2"],
  "config": {
    "test_type": "functional",
    "complexity": "medium",
    "count": 20
  }
}

# 获取测试用例列表
GET /api/v1/test_cases/

# 获取测试用例详情
GET /api/v1/test_cases/{case_id}
```

#### 思维导图
```http
# 生成思维导图
POST /api/v1/mind_maps/generate
Content-Type: application/json

{
  "test_case_ids": ["case1", "case2"],
  "layout": "hierarchical"
}

# 获取思维导图数据
GET /api/v1/mind_maps/{map_id}
```

### API 认证

所有 API 请求都需要在 Header 中包含 JWT token：

```http
Authorization: Bearer <your_jwt_token>
```

### 错误处理

API 使用标准 HTTP 状态码：

- `200` - 成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器内部错误

错误响应格式：
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": {
      "field": "document_id",
      "reason": "必需字段"
    }
  }
}
```

## 🛠️ 运维和故障排除

### 常见问题

#### 1. 服务启动失败
**问题**: Docker 容器无法启动
**解决方案**:
```bash
# 检查端口占用
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# 清理 Docker 资源
docker-compose down -v
docker system prune -f

# 重新启动
docker-compose up -d
```

#### 2. Gemini API 错误
**问题**: AI 生成功能无法使用
**解决方案**:
- 检查 API Key 是否正确配置
- 确认 API Key 是否有效且未过期
- 检查网络连接是否正常
- 查看 API 配额是否用完

#### 3. 文件上传失败
**问题**: 无法上传文件或处理失败
**解决方案**:
```bash
# 检查磁盘空间
df -h

# 检查文件权限
ls -la data/documents/

# 检查文件大小限制
grep MAX_FILE_SIZE .env
```

#### 4. 数据库连接错误
**问题**: 无法连接到数据库
**解决方案**:
```bash
# 检查数据库状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 日志管理

#### 查看应用日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

#### 日志级别配置
在 `.env` 文件中配置日志级别：
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_test_cases_document_id ON test_cases(document_id);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM documents WHERE created_at > '2024-01-01';
```

#### 缓存优化
```bash
# Redis 缓存配置
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600  # 缓存过期时间（秒）
```

### 备份和恢复

#### 数据库备份
```bash
# 备份数据库
docker-compose exec postgres pg_dump -U postgres aidemo > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U postgres aidemo < backup.sql
```

#### 文件备份
```bash
# 备份文档数据
tar -czf documents_backup.tar.gz data/documents/

# 备份向量数据库
tar -czf chromadb_backup.tar.gz data/chroma_db/
```

### 监控和告警

#### 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查数据库连接
docker-compose exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### 资源监控
```bash
# 查看 Docker 容器资源使用
docker stats

# 查看系统资源
htop
iostat -x 1
```

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork** 项目到您的 GitHub 账号
2. **创建** 功能分支: `git checkout -b feature/amazing-feature`
3. **提交** 您的更改: `git commit -m 'Add amazing feature'`
4. **推送** 到分支: `git push origin feature/amazing-feature`
5. **创建** Pull Request

### 开发规范
- 遵循项目的代码规范
- 添加适当的测试用例
- 更新相关文档
- 确保所有测试通过

### 提交信息规范
```
type(scope): description

[optional body]

[optional footer]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或工具相关

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持和联系

- **问题反馈**: [GitHub Issues](https://github.com/your-username/AItestdemo/issues)
- **功能建议**: [GitHub Discussions](https://github.com/your-username/AItestdemo/discussions)
- **技术支持**: support@aidemo.com

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [ChromaDB](https://www.trychroma.com/) - 开源向量数据库
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [D3.js](https://d3js.org/) - 数据可视化库

---

**AItestdemo** - 让测试用例生成更智能、更高效！