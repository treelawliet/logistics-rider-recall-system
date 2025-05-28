# 🚀 即时物流骑手智能召回系统 - 部署指南

## 📋 部署概述

本项目支持多种部署方式，从本地演示到云端部署，满足不同场景的需求。

## 🏠 本地部署

### 1. 环境要求
- Python 3.8+
- Git

### 2. 快速启动
```bash
# 克隆项目
git clone https://github.com/你的用户名/logistics-rider-recall-system.git
cd logistics-rider-recall-system

# 安装依赖（可选，基础演示不需要）
pip install -r requirements.txt

# 启动演示服务器
python3 start_demo_server.py
```

### 3. 访问演示
浏览器访问：http://localhost:8080/demo_web.html

## 🌐 GitHub Pages 部署

### 1. 启用 GitHub Pages
1. 进入你的 GitHub 仓库
2. 点击 Settings 标签
3. 滚动到 Pages 部分
4. Source 选择 "Deploy from a branch"
5. Branch 选择 "main"
6. 点击 Save

### 2. 访问在线演示
- 地址：https://你的用户名.github.io/logistics-rider-recall-system/demo_web.html
- 通常需要等待几分钟生效

## ☁️ 云端部署选项

### Vercel 部署
1. 访问 [vercel.com](https://vercel.com)
2. 连接 GitHub 账号
3. 导入项目仓库
4. 自动部署完成

### Netlify 部署
1. 访问 [netlify.com](https://netlify.com)
2. 连接 GitHub 账号
3. 选择项目仓库
4. 部署设置：
   - Build command: `echo "Static site"`
   - Publish directory: `/`

### Railway 部署（支持Python后端）
1. 访问 [railway.app](https://railway.app)
2. 连接 GitHub 账号
3. 部署项目
4. 自动检测 Python 环境

## 🔧 配置说明

### 环境变量（可选）
```bash
# .env 文件
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### 自定义配置
编辑 `config/settings.py` 文件：
- 修改业务参数
- 调整算法阈值
- 配置外部API

## 📊 监控和日志

### 本地监控
- 日志文件：`logs/system.log`
- 演示结果：`demo_result_*.json`

### 云端监控
- Vercel：内置分析面板
- Netlify：访问统计
- Railway：应用监控

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用进程
   lsof -i :8080
   # 杀死进程
   kill -9 PID
   ```

2. **Python版本问题**
   ```bash
   # 检查版本
   python3 --version
   # 使用虚拟环境
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   # 使用国内源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

## 🔄 更新部署

### 本地更新
```bash
git pull origin main
python3 start_demo_server.py
```

### 云端更新
- 推送到 GitHub 后自动部署
- 通常需要1-3分钟生效

## 📈 性能优化

### 静态资源优化
- HTML/CSS/JS 已压缩
- 图片资源优化
- 缓存策略配置

### 服务器优化
- 启用 Gzip 压缩
- 设置适当的缓存头
- 使用 CDN 加速

## 🔒 安全考虑

### 生产环境
- 关闭 DEBUG 模式
- 配置 HTTPS
- 设置访问限制
- 定期更新依赖

### API 安全
- 添加认证机制
- 限制请求频率
- 输入验证和过滤

## 📞 技术支持

如遇到部署问题：
1. 查看项目 Issues
2. 参考文档说明
3. 提交新的 Issue

---

**部署成功后，你就拥有了一个完整的多Agent协同演示系统！** 🎉 