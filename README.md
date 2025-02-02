# AIDocSearch

AIDocSearch是一个强大的文档搜索和分析平台，集成了多个AI模型（DeepSeek、Ollama、GROQ）和RAG（检索增强生成）技术，支持智能文档处理和问答。

## 主要特性

- 多模型支持：集成DeepSeek、Ollama和GROQ等多个AI模型
- RAG技术：使用Milvus向量数据库实现智能文档检索
- 实时对话：支持流式响应的AI对话
- 文档处理：支持PDF、DOCX和TXT格式
- 安全认证：使用Keycloak实现用户认证和授权
- 现代化界面：响应式设计，支持实时反馈

## 技术栈

### 后端
- Python FastAPI
- MongoDB：存储用户数据和历史记录
- Milvus：向量数据库，用于文档检索
- Keycloak：用户认证和授权
- PostgreSQL：Keycloak数据存储

### 前端
- React
- Ant Design
- Server-Sent Events (SSE)

## 部署说明

### 环境要求
- Docker和Docker Compose
- Node.js 16+
- Python 3.8+

### 配置文件
1. 复制示例环境文件：
```bash
cp backend/.env.example backend/.env
```

2. 配置以下环境变量：
- `MONGODB_URL`：MongoDB连接URL
- `KEYCLOAK_URL`：Keycloak服务器URL
- `KEYCLOAK_REALM`：Keycloak领域名称
- `KEYCLOAK_CLIENT_ID`：客户端ID
- `KEYCLOAK_CLIENT_SECRET`：客户端密钥
- `TAVILY_API_KEY`：Tavily API密钥
- `DEEPSEEK_API_KEY`：DeepSeek API密钥
- `GROQ_API_KEY`：GROQ API密钥

### 使用Docker部署

1. 启动所有服务：
```bash
docker-compose up -d
```

2. 初始化Keycloak：
- 访问 http://localhost:8080
- 使用管理员账号登录
- 创建新的Realm：aidocsearch
- 创建新的Client：aidocsearch-client
- 配置客户端重定向URL：http://localhost:3000/*

### 手动部署

1. 后端部署：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 前端部署：
```bash
cd frontend
npm install
npm start
```

## 使用说明

1. 访问 http://localhost:3000
2. 使用Keycloak账号登录
3. 上传文档或输入问题
4. 选择合适的AI模型
5. 等待实时响应

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

## 开发说明

### 后端开发
```bash
cd backend
# 安装开发依赖
pip install -r requirements.txt
# 运行测试
pytest
```

### 前端开发
```bash
cd frontend
# 安装依赖
npm install
# 启动开发服务器
npm start
# 构建生产版本
npm run build
```

## 注意事项

1. 安全性
   - 所有API密钥都应该通过环境变量配置
   - 确保Keycloak配置了适当的安全策略
   - 定期更新依赖包以修复安全漏洞

2. 性能优化
   - Milvus向量数据库建议使用SSD存储
   - 对于大文件，建议增加文件大小限制
   - 根据需要调整文本块大小和重叠度

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

GPL License
