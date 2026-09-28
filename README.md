# AI 文本检测助手

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://hub.docker.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

类似朱雀AI的检测助手，使用 Qwen 大模型进行文本来源判别。支持详细的检测报告。

## 功能
- **AI文本检测**：输入文本，调用 Qwen 模型进行全面AI生成分析
  - 输出标签（人类/AI/不确定）、置信度、判断置信度级别
  - **详细分析报告**：提供多维度分析（语言模式、内容结构、写作风格、统计特征）
  - **关键指标识别**：列出最重要的AI判断依据
  - **方法论说明**：解释使用的检测算法和判断流程
- **Web 前端展示**：现代化的 Ant Design 界面

## 运行

### 后端
1. 安装依赖：`pip install -r backend/requirements.txt`
2. 配置环境变量：复制 `backend/.env.example` 为 `.env`，填入 DashScope API Key
3. 运行：`uvicorn app.main:app --reload --port 8000`

### 前端
1. 安装依赖：`npm install`
2. 配置环境变量：复制 `frontend/.env.example` 为 `.env`
3. 开发：`npm run dev`（代理到后端）
4. 构建：`npm run build`

## API 接口

### 检测接口
```
POST /api/detect
Content-Type: application/json

{
  "text": "要检测的文本内容"
}
```
返回全面的AI检测分析结果，包含：
- 基本判断（标签、分数、置信度）
- 详细分析报告（多维度特征分析）
- 关键指标列表
- 判断方法论说明

**返回示例**：
```json
{
  "result": {
    "label": "ai",
    "score": 0.85,
    "confidence": "high",
    "rationale": "文本表现出典型的AI生成特征",
    "detailed_analysis": "详细的分析报告...",
    "key_indicators": ["特征1", "特征2"],
    "methodology": "基于多维度特征分析的AI检测算法"
  }
}
```

## 注意
- 需配置 DashScope API Key
- 文本长度限制 8000 字符
- 检测温度设为 0.2 以提高一致性
- AI模型返回严格的JSON格式，确保解析稳定性
- 包含7个标准字段：label、score、confidence、rationale、detailed_analysis、key_indicators、methodology

## 🚀 部署选项

### Docker 快速启动（推荐发布路径）
```bash
git clone https://github.com/hoyo0210/aigc-detector.git
cd aigc-detector

cp backend/.env.example backend/.env
# 编辑 backend/.env，设置 DASHSCOPE_API_KEY=sk-...

# 方式 A：一键脚本（检查 Key、构建、健康检查）
./deploy.sh

# 方式 B：手动
docker compose up -d --build
curl -fsS http://127.0.0.1:8000/api/health
open http://localhost:8080   # 前端（宿主机默认 8080 → 容器 Nginx 80；可用 FRONTEND_PORT 覆盖）
```

说明：Compose 通过 `backend/.env` 注入密钥；前端容器内 Nginx 将 `/api` 反代到 `backend:8000`。若本机 8080 也被占用，启动前设置 `FRONTEND_PORT=8090` 等。
### 安全与可观测（发布最小集）
- **密钥**：只放在 `backend/.env` 或编排 secrets；仓库与镜像构建上下文忽略 `.env`（见 `.dockerignore`）
- **健康检查**：`GET /api/health` → `{ "status": "ok", "dashscope_configured": true|false }`（不返回密钥）
- **CORS**：`CORS_ORIGINS`（逗号分隔），默认仅本地 Vite 源
- **限流**：`RATE_LIMIT_PER_MINUTE`（默认 60，按 IP；`/api/health` 豁免）

### 云平台部署
- **Vercel**: 前端静态部署
- **Railway**: 全栈应用部署
- **Render**: Web服务 + 静态站点
- **Fly.io**: 全球分布式部署
- **AWS EC2**: 自托管服务器

📖 详细部署指南：[DEPLOYMENT.md](DEPLOYMENT.md)

## 📱 移动端应用

### React Native 版本
支持iOS和Android平台的原生移动应用，具有与Web版本相同的AI文本检测功能。

#### 开发环境设置
```bash
# 安装依赖
cd mobile
npm install

# iOS开发（需要macOS和Xcode）
npm run ios

# Android开发（需要Android Studio和SDK）
npm run android
```

#### 生产构建
```bash
# Android APK
npm run build:android

# iOS IPA（需要macOS）
npm run build:ios
```

#### 网络配置
- 开发环境：连接到 `http://10.0.2.2:8000` (Android) 或 `http://localhost:8000` (iOS)
- 生产环境：配置为您的API服务器地址

### 移动端功能特点
1. **页面流程**：输入页面 → 处理页面 → 结果页面
2. **Material Design**：使用React Native Paper组件库，提供现代化UI
3. **响应式设计**：适配不同屏幕尺寸和方向
4. **离线处理**：网络异常时提供友好的错误提示
5. **实时进度**：检测过程中显示进度条和状态

### 技术栈
- **React Native 0.72.6**：跨平台移动应用框架
- **React Native Paper**：Material Design组件库
- **React Navigation**：页面导航管理
- **TypeScript**：类型安全的开发体验

