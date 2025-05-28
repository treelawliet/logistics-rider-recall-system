#!/bin/bash

# 即时物流骑手智能召回系统 - GitHub部署脚本
# 使用方法: ./deploy_to_github.sh 你的GitHub用户名

echo "🚚 即时物流骑手智能召回系统 - GitHub部署脚本"
echo "=================================================="

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供你的GitHub用户名"
    echo "使用方法: ./deploy_to_github.sh 你的GitHub用户名"
    echo "示例: ./deploy_to_github.sh qirui"
    exit 1
fi

USERNAME=$1
REPO_NAME="logistics-rider-recall-system"

echo "👤 GitHub用户名: $USERNAME"
echo "📦 仓库名称: $REPO_NAME"
echo ""

# 检查Git是否已安装
if ! command -v git &> /dev/null; then
    echo "❌ 错误: Git未安装，请先安装Git"
    exit 1
fi

echo "🔍 检查Git仓库状态..."

# 检查是否已经是Git仓库
if [ ! -d ".git" ]; then
    echo "📝 初始化Git仓库..."
    git init
    git add .
    git commit -m "feat: 初始化即时物流骑手智能召回系统项目"
    git branch -M main
fi

# 检查是否已添加远程仓库
if git remote get-url origin &> /dev/null; then
    echo "🔗 远程仓库已存在，更新URL..."
    git remote set-url origin https://github.com/$USERNAME/$REPO_NAME.git
else
    echo "🔗 添加远程仓库..."
    git remote add origin https://github.com/$USERNAME/$REPO_NAME.git
fi

echo ""
echo "📋 部署前检查清单:"
echo "✅ Git仓库已初始化"
echo "✅ 文件已提交到本地仓库"
echo "✅ 远程仓库地址已设置"
echo ""

echo "🚀 准备推送到GitHub..."
echo "⚠️  请确保你已经在GitHub上创建了仓库: $REPO_NAME"
echo ""

read -p "是否继续推送到GitHub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 推送到GitHub..."
    
    if git push -u origin main; then
        echo ""
        echo "🎉 部署成功!"
        echo "=================================================="
        echo "📍 你的项目地址:"
        echo "   GitHub仓库: https://github.com/$USERNAME/$REPO_NAME"
        echo "   项目主页: https://$USERNAME.github.io/$REPO_NAME/"
        echo "   演示页面: https://$USERNAME.github.io/$REPO_NAME/demo_web.html"
        echo ""
        echo "📝 下一步操作:"
        echo "1. 访问 https://github.com/$USERNAME/$REPO_NAME"
        echo "2. 点击 Settings -> Pages"
        echo "3. Source 选择 'Deploy from a branch'"
        echo "4. Branch 选择 'main'"
        echo "5. 点击 Save"
        echo "6. 等待几分钟后访问在线演示"
        echo ""
        echo "📚 详细说明请查看: GITHUB_DEPLOY_GUIDE.md"
    else
        echo ""
        echo "❌ 推送失败!"
        echo "可能的原因:"
        echo "1. 仓库不存在，请先在GitHub创建仓库"
        echo "2. 没有推送权限，请检查GitHub登录状态"
        echo "3. 网络连接问题"
        echo ""
        echo "💡 解决方案:"
        echo "1. 访问 https://github.com/new 创建新仓库"
        echo "2. 仓库名称设置为: $REPO_NAME"
        echo "3. 设置为Public（公开）"
        echo "4. 不要勾选初始化README"
        echo "5. 重新运行此脚本"
    fi
else
    echo "❌ 取消部署"
    echo ""
    echo "💡 如需手动部署，请执行:"
    echo "git push -u origin main"
fi

echo ""
echo "�� 感谢使用即时物流骑手智能召回系统!" 