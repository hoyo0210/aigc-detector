# 🚀 项目发布检查清单

## ✅ 基础准备

- [x] 项目代码完成
- [x] 功能测试通过
- [x] 响应式设计完成
- [x] 文档编写完成

## 📁 项目文件

- [x] README.md - 项目介绍和使用说明
- [x] LICENSE - 开源许可证
- [x] .gitignore - 忽略文件配置
- [x] DEPLOYMENT.md - 详细部署指南

## 🐳 Docker配置

- [x] Dockerfile - 后端容器化
- [x] frontend/Dockerfile - 前端容器化
- [x] docker-compose.yml - 多容器编排
- [x] backend/requirements.prod.txt - 生产依赖

## 🔧 开发工具

- [x] .github/workflows/docker-deploy.yml - CI/CD流水线
- [x] backend/.env.example - 环境变量模板
- [x] frontend/.env.example - 前端配置模板

## 🌐 部署选项

### 本地部署
- [x] Docker Compose 启动脚本（`./deploy.sh` / `docker compose`）
- [x] 环境变量配置说明（`backend/.env`）
- [x] 端口映射配置（后端 8000；前端默认 8080→80，可用 `FRONTEND_PORT`）

### 云平台部署
- [ ] GitHub Actions 自动化构建
- [ ] Vercel 前端部署配置
- [ ] Railway 全栈部署配置
- [ ] Render 服务配置
- [ ] Fly.io 全球部署配置

### 自托管部署
- [ ] AWS EC2 部署指南
- [ ] 阿里云/腾讯云部署指南
- [ ] Nginx 反向代理配置
- [ ] SSL 证书配置

## 🔐 安全配置

- [x] API密钥安全管理
- [x] CORS 策略配置（`CORS_ORIGINS`）
- [x] 请求限流建议（`RATE_LIMIT_PER_MINUTE`，实现为进程内按 IP 限流）
- [ ] HTTPS 配置指南

## 📊 监控和运维

- [x] 健康检查端点（`GET /api/health`）
- [ ] 日志收集配置
- [ ] 性能监控建议
- [ ] 备份策略

## 📚 文档完善

- [x] API 接口文档
- [ ] 故障排除指南
- [ ] 性能优化建议
- [ ] 扩展开发指南

## 🎯 发布前检查（本周期 In）

- [x] 敏感信息已移除（`.env` / `.venv` ignore；`.dockerignore`；tracked 无长 `sk-`）
- [x] 最小测试通过（`backend/tests/test_health_security.py`）
- [x] Compose 生产向路径验证（health + 前端 8080 + Nginx `/api`）
- [x] 文档链接正确（README ↔ DEPLOYMENT）
- [x] 许可证信息完整（MIT `LICENSE`）
- [x] 冒烟：`POST /api/detect` 经 `:8000` 与 `:8080/api` 均成功返回 label/score

## 📦 分发渠道

- [x] GitHub 仓库创建（`hoyo0210/aigc-detector`）
- [ ] Docker Hub 镜像推送（Out：非本周期门闩）
- [ ] PyPI 包发布 (如果适用)（Out）
- [ ] NPM 包发布 (如果适用)（Out）

## 🔗 外部集成

- [x] DashScope API 集成（冒烟已调用）
- [ ] 第三方服务配置（Out）
- [ ] CDN 配置（Out）
- [ ] 域名配置（Out）

## 🎉 发布就绪

本周期门闩 = Charter 五项成功标准。下列云/监控/多端专题保持未勾，属 Out，不阻塞「可自托管发布」。

**Approver 验收：** 回复「可发布」即关闭增量 3 / Monitor→Close 候选。
