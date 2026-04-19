# GitHub 发布指南

## 🚀 将 AutoMemory Pro 发布到 GitHub

### 方法1: 使用 GitHub CLI (推荐)

```bash
# 1. 安装 GitHub CLI (如果还没有安装)
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# 2. 登录 GitHub
gh auth login

# 3. 创建仓库
cd ~/.openclaw/plugins/automemory
gh repo create automemory-pro --public --source=. --remote=origin --push

# 完成！🎉
```

### 方法2: 手动创建

#### 步骤1: 在 GitHub 上创建空仓库

1. 访问 https://github.com/new
2. 输入仓库名: `automemory-pro`
3. 选择: Public (或 Private)
4. 不要勾选 "Initialize this repository with a README" (我们已经有README了)
5. 点击 "Create repository"

#### 步骤2: 推送本地代码

```bash
cd ~/.openclaw/plugins/automemory

# 添加远程仓库 (替换 yourusername 为你的GitHub用户名)
git remote add origin https://github.com/yourusername/automemory-pro.git

# 推送代码
git branch -M main
git push -u origin main

# 完成！🎉
```

### 方法3: 我来帮你创建

如果你授权我访问你的GitHub账户，我可以直接帮你创建。请运行：

```bash
# 生成GitHub Personal Access Token
# 1. 访问: https://github.com/settings/tokens
# 2. 点击 "Generate new token (classic)"
# 3. 选择权限: repo (完整仓库访问)
# 4. 生成token并复制

# 5. 在本地设置token
export GITHUB_TOKEN=your_token_here

# 6. 使用GitHub API创建仓库
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/user/repos \
     -d '{
       "name": "automemory-pro",
       "description": "让AI真正拥有记忆和智慧的OpenClaw插件",
       "private": false,
       "has_issues": true,
       "has_projects": true,
       "has_wiki": true
     }'

# 7. 推送代码
git remote add origin https://github.com/yourusername/automemory-pro.git
git push -u origin main
```

## 📋 发布后设置

### 1. 设置仓库信息

在 GitHub 仓库页面点击 "⚙️ Settings"：

- **About**: 填写描述 "让AI真正拥有记忆和智慧的OpenClaw插件"
- **Topics**: 添加标签 `openclaw`, `ai`, `memory`, `plugin`, `python`
- **Social Preview**: 上传项目封面图（可选）

### 2. 启用功能

在 Settings 中启用：

- ✅ Issues (问题追踪)
- ✅ Discussions (讨论区)
- ✅ Projects (项目管理)
- ✅ Wiki (文档)
- ✅ Sponsorships (赞助)

### 3. 添加说明文档

创建 `.github/` 目录：

```bash
mkdir -p ~/.openclaw/plugins/automemory/.github
```

创建 Issue 模板：

```bash
cat > ~/.openclaw/plugins/automemory/.github/ISSUE_TEMPLATE.md << 'EOF'
---
name: Bug report
about: 报告问题或错误
title: '[BUG] '
labels: bug
assignees: ''

---

**描述问题**
清晰简洁地描述问题。

**复现步骤**
1. 运行 '...'
2. 调用 '...'
3. 出现错误

**期望行为**
清晰描述你期望发生什么。

**环境信息**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.9]
- OpenClaw: [e.g. 1.0.0]

**附加信息**
添加任何其他上下文或截图。
EOF
```

### 4. 创建 Release

在 GitHub 页面：

1. 点击右侧 "📦 Releases"
2. 点击 "Create a new release"
3. 选择标签: `v1.0.0`
4. 标题: `AutoMemory Pro v1.0.0 - Initial Release`
5. 内容: 复制下面内容

```markdown
## 🎉 AutoMemory Pro v1.0.0

### ✨ 新功能

- 🧠 **自动记忆捕获** - AI使用工具时自动记录
- 🎯 **主动记忆推荐** - 根据任务自动推荐相关记忆
- 📋 **任务状态追踪** - 自动追踪TODO完成情况
- 🤖 **智能工作流** - 完整的会话管理和摘要生成

### 📦 安装

```bash
git clone https://github.com/yourusername/automemory-pro.git
cd automemory-pro
# 复制到OpenClaw插件目录
cp *.py *.json ~/.openclaw/plugins/automemory/
```

### 🚀 快速开始

```python
from automemory_pro import AutoMemoryPro

plugin = AutoMemoryPro()
recommendations = plugin.on_session_start({
    "current_task": "你的工作描述"
})
```

### 📖 文档

- [README](README.md) - 完整文档
- [快速开始](QUICKSTART.md) - 5分钟上手
- [API参考](API_REFERENCE.md) - API文档

### 🙏 感谢

感谢所有测试用户的反馈！

---

**让AI真正拥有记忆！** 🚀
```

6. 点击 "Publish release"

## 🎨 美化仓库

### 添加徽章

在 README.md 顶部添加：

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/automemory-pro.svg)](https://github.com/yourusername/automemory-pro/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/automemory-pro.svg)](https://github.com/yourusername/automemory-pro/issues)
```

### 添加贡献者指南

创建 `CONTRIBUTING.md`:

```markdown
# 贡献指南

感谢你的贡献！🎉

## 如何贡献

### 报告问题
- 使用 Issue 模板
- 提供详细的环境信息
- 附上复现步骤

### 提交代码
1. Fork 仓库
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8
- 添加类型提示
- 编写测试
- 更新文档

## 开发设置

```bash
git clone https://github.com/yourusername/automemory-pro.git
cd automemory-pro
pip install -r requirements-dev.txt
pytest
```

## 联系方式

有问题？开 Issue 或邮件联系！
```

## 🚀 推广

### 分享到社区

- [ ] Reddit: r/OpenClaw, r/Python
- [ ] Twitter: @OpenClaw, @Python
- [ ] Discord: OpenClaw 社区
- [ ] 知乎: AI, Python话题
- [ ] V2EX: Python节点

### 添加到 Awesome 列表

- [ ] awesome-openclaw
- [ ] awesome-python
- [ ] awesome-ai-tools

## 📊 维护

### 定期更新

- [ ] 每月检查 Issues
- [ ] 每季度发布新版本
- [ ] 每年更新依赖

### 收集反馈

创建 Discussion 分类：
- 💡 Ideas (功能建议)
- ❓ Q&A (问题解答)
- 🎉 Show and tell (用户展示)

---

🎉 **恭喜！你的项目已成功发布到 GitHub！**

现在全世界都可以使用你的 AutoMemory Pro 了！🚀
