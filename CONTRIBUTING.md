# 🤝 贡献指南

感谢你对即时物流骑手智能召回系统的关注！我们欢迎各种形式的贡献。

## 🎯 贡献方式

### 🐛 报告Bug
- 使用 GitHub Issues 报告问题
- 提供详细的复现步骤
- 包含错误信息和环境信息

### 💡 功能建议
- 在 Issues 中提出新功能想法
- 描述功能的使用场景和价值
- 讨论实现方案

### 📝 改进文档
- 修正文档中的错误
- 补充使用示例
- 翻译文档到其他语言

### 💻 代码贡献
- 修复Bug
- 实现新功能
- 优化性能
- 增加测试

## 🔧 开发环境设置

### 1. Fork 项目
点击 GitHub 页面右上角的 "Fork" 按钮

### 2. 克隆代码
```bash
git clone https://github.com/你的用户名/logistics-rider-recall-system.git
cd logistics-rider-recall-system
```

### 3. 创建开发分支
```bash
git checkout -b feature/你的功能名称
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 运行测试
```bash
python -m pytest tests/
```

## 📋 代码规范

### Python 代码风格
- 遵循 PEP 8 规范
- 使用有意义的变量名
- 添加适当的注释
- 函数和类需要文档字符串

### 提交信息格式
```
类型(范围): 简短描述

详细描述（可选）

关闭的Issue（可选）
Closes #123
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 示例
```
feat(agents): 添加新的预测算法

实现基于LSTM的订单预测模型，提高预测准确率

Closes #45
```

## 🧪 测试要求

### 单元测试
- 新功能必须包含测试
- 测试覆盖率不低于80%
- 使用 pytest 框架

### 集成测试
- 测试Agent之间的协作
- 验证完整工作流程
- 模拟真实场景

## 📤 提交流程

### 1. 确保代码质量
```bash
# 运行测试
python -m pytest

# 检查代码风格
flake8 .

# 类型检查（如果使用）
mypy .
```

### 2. 提交代码
```bash
git add .
git commit -m "feat: 你的功能描述"
git push origin feature/你的功能名称
```

### 3. 创建 Pull Request
- 在 GitHub 上创建 PR
- 填写详细的描述
- 关联相关的 Issue
- 等待代码审查

## 🔍 代码审查

### 审查要点
- 代码逻辑正确性
- 性能影响
- 安全考虑
- 文档完整性
- 测试覆盖

### 审查流程
1. 自动化测试通过
2. 至少一位维护者审查
3. 解决所有评论
4. 合并到主分支

## 🏷️ 版本发布

### 版本号规则
遵循语义化版本控制 (SemVer)：
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 发布流程
1. 更新版本号
2. 更新 CHANGELOG
3. 创建 Release Tag
4. 发布到各平台

## 🎨 设计原则

### 代码设计
- 单一职责原则
- 开闭原则
- 依赖倒置原则
- 保持简单（KISS）

### Agent设计
- 明确的角色定义
- 清晰的输入输出
- 可测试的工具函数
- 良好的错误处理

## 📚 学习资源

### 相关技术
- [CrewAI 文档](https://docs.crewai.com/)
- [Python 最佳实践](https://docs.python-guide.org/)
- [多Agent系统](https://en.wikipedia.org/wiki/Multi-agent_system)

### 业务知识
- 即时物流行业
- 运力调度算法
- 人工智能应用

## 🙋‍♀️ 获取帮助

### 联系方式
- GitHub Issues：技术问题
- GitHub Discussions：一般讨论
- Email：紧急问题

### 响应时间
- Issues：通常24小时内响应
- PR审查：通常48小时内
- 紧急问题：尽快处理

## 🎉 贡献者认可

### 贡献者列表
所有贡献者都会在 README 中得到认可

### 特殊贡献
- 重大功能贡献者
- 长期维护者
- 文档贡献者
- 社区建设者

---

**感谢你的贡献，让我们一起打造更好的智能召回系统！** 🚀 