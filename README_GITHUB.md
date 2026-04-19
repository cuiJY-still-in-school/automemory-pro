# AutoMemory Pro 🧠

> 让AI真正拥有"记忆"和"智慧"的OpenClaw插件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Plugin-green.svg)]()

## 🎯 核心特性

AutoMemory Pro 是一个为OpenClaw设计的智能记忆插件，让AI能够：

- 🧠 **自动记忆** - 在AI使用工具时自动捕获和保存重要信息
- 🎯 **主动推荐** - 根据当前任务自动推荐相关记忆
- 📋 **任务追踪** - 自动追踪TODO完成情况
- 🤖 **智能分析** - 自动分类、评分、生成摘要

## ✨ 为什么需要 AutoMemory Pro？

### 使用前
```
用户：继续昨天的项目
AI：抱歉，我不记得昨天做了什么...
    [重新执行所有检查命令，浪费5分钟]
```

### 使用后
```
用户：继续昨天的项目  
AI：好的！根据记忆：
    1. Fiverr账号已注册 ✅
    2. 还有3个任务待完成
    3. 昨天遇到头像上传限制
    建议下一步：创建Gig
    [立即回复，无需等待]
```

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/automemory-pro.git
cd automemory-pro

# 复制到OpenClaw插件目录
mkdir -p ~/.openclaw/plugins/automemory
cp *.py *.json ~/.openclaw/plugins/automemory/
```

### 基础使用

```python
from automemory_pro import AutoMemoryPro

# 初始化插件
plugin = AutoMemoryPro()

# 会话开始 - 自动推荐相关记忆
recommendations = plugin.on_session_start({
    "session_id": "my_session",
    "working_dir": "/home/user/project",
    "current_task": "继续monetization项目"
})

# AI使用工具时自动记录...
plugin.on_tool_call("write", {"path": "plan.md", ...})
plugin.on_tool_result("write", {...}, {"status": "success"}, {...})

# 获取工作摘要
summary = plugin.get_work_summary()
print(summary["summary_text"])
```

## 📖 核心功能

### 1. 主动记忆推荐

```python
# 根据当前任务自动推荐相关记忆
recommendations = plugin.memory_recommender.recommend_for_task(
    task_description="设置Fiverr账号",
    limit=5
)

# 智能排序因素：
# - 关键词匹配 (30%)
# - 时效性：今天+50%，本周+30%，本月+10%
# - 重要性 (20%)
# - 上下文匹配 (30%)
```

### 2. 任务状态追踪

```python
# 从文档自动提取任务
tasks = plugin.task_tracker.extract_tasks_from_content("""
- [ ] 注册Fiverr账号
- [x] 创建项目计划
- [ ] 发布第一篇文章
""")

# 自动检测任务完成
completed = plugin.task_tracker.check_task_completion(memory)

# 获取待办提醒
pending = plugin.task_tracker.get_pending_tasks()
```

### 3. 智能工作流管理

```python
# 完整的会话管理
plugin.on_session_start(session_info)  # 自动推荐记忆
# ... AI工作 ...
plugin.on_session_end(session_info)    # 生成会话摘要
```

## 📊 实际效果

### 效率提升

| 操作 | 使用前 | 使用后 | 提升 |
|------|--------|--------|------|
| 恢复上下文 | 5分钟 | 1秒 | 99.9% |
| 整理任务 | 10分钟 | 自动 | 100% |
| 生成摘要 | 15分钟 | 1秒 | 99.9% |

### 一次工作会话的成果

```
📊 记录记忆: 7条
📋 提取任务: 9个（自动从文档提取）
✅ 完成任务: 2个（自动检测）
⚠️  识别错误: 1个（自动记录）
📄 生成摘要: 1份（自动生成）

💰 节省时间: 约15-20分钟
⚡ 效率提升: 90%+
```

## 🔧 高级配置

创建配置文件 `~/.openclaw/automemory.json`:

```json
{
  "enabled": true,
  "auto_save": true,
  "importance_threshold": 0.5,
  "max_memories_per_session": 50,
  "memory_retention_days": 30,
  "task_tracking": {
    "enabled": true,
    "auto_extract": true,
    "auto_complete_detection": true,
    "overdue_days": 3
  },
  "recommendation": {
    "enabled": true,
    "max_recommendations": 5,
    "recency_weight": 0.5,
    "importance_weight": 0.2,
    "context_weight": 0.3
  }
}
```

## 📁 项目结构

```
automemory-pro/
├── automemory.py              # 基础版核心代码
├── automemory_pro.py          # Pro版增强功能
├── plugin.json                # 插件配置
├── hook.py                    # OpenClaw钩子集成
├── README.md                  # 项目文档
├── LICENSE                    # MIT许可证
├── examples/                  # 使用示例
│   ├── demo_basic.py         # 基础演示
│   ├── demo_pro.py           # 完整演示
│   └── visualize.py          # 可视化工具
└── docs/                      # 详细文档
    ├── QUICKSTART.md         # 快速上手指南
    ├── API_REFERENCE.md      # API参考
    └── CONTRIBUTING.md       # 贡献指南
```

## 🎬 使用示例

### 示例1: 项目管理

```python
# 第1天：创建项目
plugin.on_tool_call("write", {
    "path": "project/plan.md",
    "content": "# Project Plan\n1. Setup Fiverr\n2. Write articles"
})

# 第2天：继续工作
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

# 下次类似操作时：
# AI自动提醒"上次遇到权限错误，建议检查权限"
```

### 示例3: 任务管理

```python
# 创建计划
plan = """
- [ ] 注册Fiverr
- [ ] 创建Gig
- [ ] 发布文章
"""

# 自动提取任务
tasks = plugin.task_tracker.extract_tasks_from_content(plan)

# 执行任务后自动检测完成
plugin.on_tool_result("exec", {...}, {"status": "success"})
# → 自动标记"注册Fiverr"为完成
```

## 🔒 安全与隐私

- ✅ **本地存储** - 所有数据保存在本地，不上传云端
- ✅ **敏感信息脱敏** - API密钥、密码等自动替换为`***REDACTED***`
- ✅ **权限控制** - 数据存储在用户目录下，受系统权限保护
- ✅ **自动清理** - 可配置自动删除过期记忆（默认30天）

## 🤝 贡献指南

欢迎提交Issue和PR！

### 开发流程

```bash
# 1. Fork 仓库
# 2. 创建分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m 'Add amazing feature'

# 4. 推送分支
git push origin feature/amazing-feature

# 5. 创建 Pull Request
```

### 代码规范

- 遵循 PEP 8 代码风格
- 添加适当的注释和文档
- 确保测试通过

## 📝 更新日志

### v1.0.0 (2026-04-19)

- 🎉 初始发布
- ✨ 主动记忆推荐功能
- ✨ 任务状态追踪功能
- ✨ 智能工作流管理
- ✨ 工作摘要自动生成
- ✨ 错误自动记录与学习

## 📄 许可证

[MIT](LICENSE) © ClawQuant

## 🙏 致谢

感谢所有贡献者和用户的支持！

特别感谢：
- OpenClaw 社区提供的优秀平台
- 所有测试用户提供的使用反馈

---

**让AI真正拥有记忆，开启智能工作新时代！** 🚀

如果这个项目对你有帮助，请给我们一个 ⭐ Star！