# AI文本检测器部署指南

## 📋 目录

- [快速开始](#快速开始)
- [本地开发](#本地开发)
- [Docker部署](#docker部署)
- [云平台部署](#云平台部署)
- [GitHub发布](#github发布)
- [API服务](#api服务)

## 🚀 快速开始

### 1. 环境要求
- Python 3.11+
- Node.js 18+
- Docker (可选)

### 2. 克隆项目
```bash
git clone https://github.com/hoyo0210/aigc-detector.git
cd aigc-detector
```

### 3. 配置环境变量
```bash
# 后端配置
cp backend/.env.example backend/.env
# 编辑 backend/.env 添加 DASHSCOPE_API_KEY

# 前端配置
cp frontend/.env.example frontend/.env
```

## 🛠️ 本地开发

### 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 启动前端
```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`

## 🐳 Docker部署

### 单容器部署
```bash
# 构建镜像
docker build -t ai-detector .

# 运行容器
docker run -p 8000:8000 -e DASHSCOPE_API_KEY=your_key ai-detector
```

### Docker Compose部署（推荐）
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，设置 DASHSCOPE_API_KEY=sk-...

./deploy.sh
# 或: docker compose up -d --build

# 前端默认 http://localhost:8080 （FRONTEND_PORT 可改）
# 后端健康检查 http://localhost:8000/api/health
# 停止: docker compose down
```

Compose 使用 `backend/.env`；前端 Nginx 将 `/api` 反代到服务名 `backend:8000`。

## ☁️ 云平台部署

### Vercel (前端)
```bash
# 安装Vercel CLI
npm i -g vercel

# 部署前端
cd frontend
vercel --prod
```

### Railway (全栈)
```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录并部署
railway login
railway link
railway up
```

### Render
1. 连接GitHub仓库
2. 创建Web Service (后端)
3. 创建Static Site (前端)
4. 配置环境变量

### Fly.io
```bash
# 安装Fly CLI
curl -L https://fly.io/install.sh | sh

# 部署
fly launch
fly deploy
```

## 🔧 API服务部署

### 阿里云/腾讯云服务器
```bash
# 1. 安装Docker
curl -fsSL https://get.docker.com | bash

# 2. 克隆项目
git clone https://github.com/hoyo0210/aigc-detector.git

# 3. 配置环境变量
cp backend/.env.example backend/.env
# 编辑.env文件

# 4. 使用Docker Compose启动
docker-compose up -d

# 5. 配置Nginx反向代理 (可选)
```

### AWS EC2
```bash
# 1. 启动EC2实例 (Ubuntu)
# 2. 安装Docker
sudo apt update && sudo apt install -y docker.io

# 3. 配置安全组 (开放80, 443, 8000端口)
# 4. 部署应用
git clone https://github.com/hoyo0210/aigc-detector.git
cd aigc-detector
docker-compose up -d
```

## 📦 GitHub发布

### 1. 创建仓库
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/hoyo0210/aigc-detector.git
git push -u origin master
```

### 2. 添加GitHub Actions
创建 `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Build and push Docker image
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker build -t hoyo0210/aigc-detector:${{ github.sha }} .
        docker push hoyo0210/aigc-detector:${{ github.sha }}
```

### 3. 配置GitHub Pages
```bash
# 构建前端
cd frontend
npm run build

# 推送到gh-pages分支
npx gh-pages -d dist
```

## 🔐 环境变量配置

### 必需变量
```bash
# DashScope API Key (必需)
DASHSCOPE_API_KEY=your_api_key_here

# 模型配置 (可选)
QWEN_MODEL=qwen-plus
QWEN_TIMEOUT=15
DETECT_TEMPERATURE=0.2
```

### 生产环境建议
- 使用环境变量管理敏感信息
- 配置HTTPS证书
- 设置API速率限制
- 添加日志监控

## 📊 监控和维护

### 健康检查
```bash
# API健康检查
curl http://your-domain.com/api/health

# 容器状态检查
docker ps
docker stats
```

### 日志查看
```bash
# Docker日志
docker-compose logs -f backend

# 系统日志
tail -f /var/log/nginx/access.log
```

## 🚀 性能优化

### 后端优化
- 使用Gunicorn替代Uvicorn生产环境
- 配置数据库连接池
- 添加Redis缓存
- 设置API限流

### 前端优化
- 启用gzip压缩
- 配置CDN
- 代码分割
- 图片优化

## 🔒 安全建议

1. **API密钥安全**
   - 永不提交到代码库
   - 使用环境变量
   - 定期轮换密钥

2. **HTTPS配置**
   - 生产环境必须启用HTTPS
   - 配置SSL证书

3. **访问控制**
   - 添加API认证
   - 配置CORS策略
   - 设置请求限流

## 📞 支持

如遇部署问题，请：
1. 检查日志文件
2. 验证环境变量配置
3. 确认网络连接
4. 查看官方文档

## 📈 扩展建议

- 添加用户管理系统
- 集成数据库存储检测历史
- 支持批量检测API
- 添加WebSocket实时检测
- 集成第三方AI服务
