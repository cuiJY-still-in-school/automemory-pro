# AutoMemory Pro 🧠

> 让AI真正拥有"记忆"和"智慧"的OpenClaw插件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash
```

或者手动安装：
```bash
git clone https://github.com/cuiJY-still-in-school/automemory-pro.git
cd automemory-pro
chmod +x install.sh && ./install.sh
```

## 🚀 快速开始

```python
from automemory_pro import AutoMemoryPro

# 初始化
plugin = AutoMemoryPro()

# 会话开始 - 自动推荐相关记忆
recommendations = plugin.on_session_start({
    "current_task": "继续monetization项目"
})

# AI工作时会自动记录...

# 获取工作摘要
summary = plugin.get_work_summary()
print(summary["summary_text"])
```

## 🎯 核心功能

| 功能 | 描述 | 效果 |
|------|------|------|
| 🧠 **自动记忆** | AI使用工具时自动记录 | 不再遗忘重要信息 |
| 🎯 **主动推荐** | 根据任务自动推荐相关记忆 | 上下文恢复1秒完成 |
| 📋 **任务追踪** | 自动追踪TODO完成状态 | 不再遗漏任务 |
| 🤖 **智能摘要** | 自动生成工作日报 | 复盘效率提升90% |

## 📊 效果对比

**使用前**：
```
用户：继续昨天的项目
AI：抱歉，我不记得了...
    [重新检查5分钟]
```

**使用后**：
```
用户：继续昨天的项目
AI：好的！根据记忆：
   1. Fiverr已注册 ✅
   2. 还有3个任务待完成
   3. 昨天遇到头像上传限制
   建议：今天创建Gig
```

## 🛠️ 快捷命令

安装后可以使用 `automemory` 命令：

```bash
automemory test       # 运行测试
automemory demo       # 查看演示
automemory status     # 查看状态
automemory visualize  # 显示统计
automemory update     # 更新到最新版
```

## 📖 详细文档

- [完整文档](README.md) - 详细使用说明
- [快速开始](QUICKSTART.md) - 5分钟上手
- [Pro版特性](README_PRO.md) - 高级功能
- [未来想法](FUTURE_IDEAS.md) - 开发路线图

## 💡 核心优势

1. **零配置** - 安装即用，自动工作
2. **零侵入** - 无需修改现有代码
3. **高效率** - 上下文恢复从5分钟到1秒
4. **智能化** - 自动分类、评分、推荐

## 🔧 系统要求

- Python 3.8+
- OpenClaw (可选，也可独立使用)
- 依赖：纯标准库，无需额外安装

## 📁 项目结构

```
~/.openclaw/plugins/automemory/
├── automemory.py          # 基础版
├── automemory_pro.py      # Pro版 ⭐
├── install.sh             # 一键安装
└── ...

~/.openclaw/automemory/     # 数据目录
├── memories_*.jsonl       # 记忆数据
├── tasks.json            # 任务数据
└── session_*.json        # 会话摘要
```

## 🎬 使用示例

### 示例1: 项目管理
```python
# 第1天创建计划
plugin.on_tool_call("write", {
    "path": "plan.md", 
    "content": "- [ ] Task 1\n- [ ] Task 2"
})

# 第2天自动恢复上下文
recommendations = plugin.on_session_start({
    "current_task": "继续project"
})
# 自动找到昨天的计划
```

### 示例2: 错误追踪
```python
# 遇到错误
plugin.on_tool_result("exec", {...}, {
    "exit_code": 1,
    "stderr": "Permission denied"
})

# 下次自动提醒
# "上次遇到权限错误，建议检查权限"
```

## 🤝 贡献

欢迎提交Issue和PR！

```bash
# 开发模式安装
git clone https://github.com/cuiJY-still-in-school/automemory-pro.git
cd automemory-pro
pip install -r requirements-dev.txt
pytest
```

## 📄 许可证

[MIT](LICENSE) © ClawQuant

## 🙏 致谢

感谢OpenClaw社区和所有测试用户！

---

**让AI真正拥有记忆，开启智能工作新时代！** 🚀

如果这个项目对你有帮助，请给我们一个 ⭐ Star！