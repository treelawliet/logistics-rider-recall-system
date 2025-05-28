# 即时物流骑手智能召回系统 - 多Agent协同Demo

[![部署状态](https://github.com/你的用户名/logistics-rider-recall-system/workflows/部署到%20GitHub%20Pages/badge.svg)](https://github.com/你的用户名/logistics-rider-recall-system/actions)
[![许可证](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python版本](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)

## 🌐 在线演示

**🚀 [立即体验在线演示](https://你的用户名.github.io/logistics-rider-recall-system/demo_web.html)**

## 📖 项目简介

这是一个基于CrewAI框架的多Agent协同系统，专门为即时物流行业设计，用于解决节假日前运力不足的问题。系统通过智能预测、自动召回、意愿分析等功能，实现高效的骑手调度管理。

## ✨ 主要特色

- 🤖 **多Agent协同**：5个专业Agent协同工作
- 🎯 **智能预测**：基于历史数据和趋势分析
- 📞 **自动召回**：智能筛选和电话召回
- 📊 **效果分析**：实时监控和数据分析
- 🎮 **交互演示**：多种演示模式和可视化界面
- 🌐 **在线体验**：无需安装，浏览器直接访问

## 🚀 快速开始

### 方式一：在线体验（推荐）
直接访问：**[在线演示页面](https://你的用户名.github.io/logistics-rider-recall-system/demo_web.html)**

### 方式二：本地运行
```bash
# 克隆项目
git clone https://github.com/你的用户名/logistics-rider-recall-system.git
cd logistics-rider-recall-system

# 启动演示服务器
python3 start_demo_server.py

# 浏览器访问 http://localhost:8080/demo_web.html
```

### 方式三：简化演示
```bash
# 不需要任何依赖，直接运行
python3 simple_demo.py
```

## 🎯 核心目标

- 召回成功率提升至85%以上（较当前基线提升20%）
- 平均响应时间缩短至5分钟以内（减少50%）
- 骑手到岗率提升至90%以上
- 整体调度效率提升30%

## 🏗️ 系统架构

### Agent角色设计

1. **PredictionAgent** - 预测分析师
   - 负责节假日前3天的订单增量与运力缺口预测
   - 基于历史数据、天气、趋势等多维度分析

2. **DecisionAgent** - 决策协调员
   - 处理站长确认反馈
   - 决定是否启动召回流程

3. **RiderProfilerAgent** - 骑手画像专家
   - 生成符合召回需求的骑手画像
   - 筛选最优候选骑手名单

4. **CallAgent** - 召回执行员
   - 执行电话召回任务
   - 记录通话过程和初步反馈

5. **AnalysisAgent** - 数据分析师
   - 汇总召回效果，计算关键指标
   - 生成优化建议和趋势报告

## 🔧 技术栈

- **框架**: CrewAI (多Agent协同)
- **语言**: Python 3.8+
- **前端**: HTML5 + CSS3 + JavaScript
- **数据处理**: Pandas, NumPy
- **可视化**: 原生JavaScript + Chart.js
- **部署**: GitHub Pages + GitHub Actions

## 📦 运行方式

### 🌐 Web演示页面
```bash
python3 start_demo_server.py
# 访问 http://localhost:8080/demo_web.html
```

### 🎮 交互式演示
```bash
python3 interactive_demo.py
```

### 🔧 完整工作流
```bash
python3 main.py --site-id "site_001" --date "2024-02-08"
```

### 📊 Streamlit界面（需安装依赖）
```bash
pip install streamlit
streamlit run app.py
```

## 📊 核心功能模块

### 预测模块
- 输入：站点ID、目标日期
- 输出：运力缺口预测、建议行动

### 召回模块  
- 输入：骑手画像要求
- 输出：候选骑手名单、召回执行结果

### 分析模块
- 输入：召回执行数据
- 输出：成功率、准确率、优化建议

## 🔄 工作流程

1. **预测阶段**: PredictionAgent → 站长确认 → DecisionAgent
2. **筛选阶段**: RiderProfilerAgent → 候选名单生成
3. **召回阶段**: CallAgent → 电话执行 → 结果记录
4. **分析阶段**: AnalysisAgent → 效果评估

## 📈 关键指标

- **召回成功率**: 实际出勤骑手数 / 拨打总次数
- **召回损耗比**: 拨打总次数 / 实际出勤骑手数  
- **意愿预测准确率**: 通话分析预测与实际出勤的匹配率
- **响应时间**: 从预测到召回完成的总耗时

## 🚀 部署指南

详细部署说明请查看：[DEPLOY.md](DEPLOY.md)

### GitHub Pages 部署
1. Fork 本项目
2. 在仓库设置中启用 GitHub Pages
3. 访问 `https://你的用户名.github.io/logistics-rider-recall-system/demo_web.html`

### 其他部署选项
- **Vercel**: 一键部署，自动HTTPS
- **Netlify**: 支持表单和函数
- **Railway**: 支持Python后端

## 📚 文档

- [使用指南](USAGE_GUIDE.md) - 详细的使用说明
- [项目总结](PROJECT_SUMMARY.md) - 完整的项目概述
- [演示指南](演示页面使用指南.md) - Web演示页面说明
- [部署指南](DEPLOY.md) - 各种部署方式
- [贡献指南](CONTRIBUTING.md) - 如何参与贡献

## 🤝 贡献

我们欢迎各种形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**🎉 立即体验：[在线演示](https://你的用户名.github.io/logistics-rider-recall-system/demo_web.html)** 