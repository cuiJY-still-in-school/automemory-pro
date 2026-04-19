# AutoMemory Pro 🧠

> 让AI真正拥有"记忆"和"智慧"的OpenClaw插件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v1.3.0-green.svg)]()

## ✨ 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash
```

## 🎯 核心功能

| 功能 | 描述 | 效果 |
|------|------|------|
| 🧠 **自动记忆** | AI使用工具时自动记录 | 不再遗忘重要信息 |
| 🔔 **智能提醒** | 逾期任务、定期提醒、上下文提示 | 想到就能做到 |
| 💬 **自然语言查询** | "我昨天做了什么？" | 像问助手一样自然 |
| 📋 **任务追踪** | 自动追踪TODO完成状态 | 不再遗漏任务 |
| 🗜️ **记忆压缩** | 自动生成日/周/月报 | 让记忆长期可用 |
| 🤖 **智能摘要** | 自动生成工作日报 | 复盘效率提升90% |

## 🚀 快速开始

```python
from automemory_pro import AutoMemoryPro

# 初始化
plugin = AutoMemoryPro()

# 会话开始 - 自动推荐相关记忆
recommendations = plugin.on_session_start({
    "current_task": "继续monetization项目"
})

# 自然语言查询
result = nq.ask("我昨天做了什么？")
print(result)

# 获取提醒摘要
reminders = plugin.get_reminder_summary()
print(reminders)
```

## 📖 详细文档

### 1. 智能提醒系统 🔔

```python
# 添加定期提醒
plugin.add_routine_reminder(
    title="每天检查Signal Arena",
    time="09:00",
    days=["Mon", "Tue", "Wed", "Thu", "Fri"]
)

# 添加上下文提示
plugin.add_context_tip(
    trigger="exec",
    tip="执行 rm 命令前注意检查路径",
    severity="warning"
)

# 检查所有提醒
reminders = plugin.check_reminders(current_tool="exec")
```

**提醒类型：**
- ⚠️ 逾期任务提醒
- 📅 定期任务提醒
- 💡 上下文智能提示
- 🏆 成就系统
- ⚠️ 错误模式检测

### 2. 自然语言查询 💬

```python
from natural_query import NaturalQuerySystem

nq = NaturalQuerySystem()

# 支持8种查询意图
result = nq.query("我昨天做了什么？")
result = nq.query("有什么待完成的任务？")
result = nq.query("这周遇到了什么错误？")
result = nq.query("项目进展如何？")
result = nq.query("总结一下这周的工作")

print(result.answer)     # 自然语言回答
print(result.summary)    # 简短总结
```

### 3. 记忆压缩 🗜️

```python
from memory_compressor import MemoryCompressor

compressor = MemoryCompressor()

# 获取统计
stats = compressor.get_memory_stats()
print(f"总记忆: {stats.total_memories}条")

# 生成每日摘要
result = compressor.compress_daily(datetime.now())
print(result.summary)

# 压缩旧记忆
results = compressor.compress_old_memories(days=30)

# 查看压缩报告
print(compressor.get_compression_report())
```

## 📊 效果对比

**使用前：**
```
用户：继续昨天的项目
AI：抱歉，我不记得了...
    [重新检查5分钟]
```

**使用后：**
```
用户：继续昨天的项目
AI：好的！根据记忆：
   1. Fiverr已注册 ✅
   2. 还有3个任务待完成
   ⚠️ 有1个任务已逾期3天
   3. 昨天遇到头像上传限制
   建议：今天创建Gig
   
💡 提示：执行命令前注意检查路径和权限
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

## 🔧 系统要求

- Python 3.8+
- OpenClaw (可选，也可独立使用)
- 依赖：纯标准库，无需额外安装

## 📁 项目结构

```
~/.openclaw/plugins/automemory/
├── automemory.py           # 基础版
├── automemory_pro.py       # Pro版核心
├── smart_reminder.py       # 🔔 智能提醒
├── natural_query.py        # 💬 自然语言查询
├── memory_compressor.py    # 🗜️ 记忆压缩
├── install.sh              # 一键安装
└── ...

~/.openclaw/automemory/     # 数据目录
├── memories_*.jsonl       # 记忆数据
├── tasks.json             # 任务数据
├── summaries/             # 摘要数据
│   └── summary_*.json
├── reminders/             # 提醒数据
│   ├── routine_tasks.json
│   ├── context_tips.json
│   └── achievements.json
└── session_*.json         # 会话摘要
```

## 📈 版本历史

### v1.3.0 (2026-04-19)
- 🗜️ 新增记忆压缩系统
- 每日/每周/每月摘要自动生成
- 记忆数量监控和压缩建议
- 压缩阈值可配置

### v1.2.0 (2026-04-19)
- 💬 新增自然语言查询系统
- 8种查询意图识别
- 语义解析和智能回答
- 支持时间范围、类型、状态过滤

### v1.1.0 (2026-04-19)
- 🔔 新增智能提醒系统
- 逾期任务提醒
- 定期任务提醒
- 上下文提示
- 成就系统
- 错误模式检测

### v1.0.0 (2026-04-19)
- 初始版本
- 自动记忆捕获
- 主动记忆推荐
- 任务状态追踪

## 🤝 贡献

欢迎提交Issue和PR！

```bash
git clone https://github.com/cuiJY-still-in-school/automemory-pro.git
cd automemory-pro
pip install -r requirements.txt
```

## 🙏 致谢

感谢OpenClaw社区和所有测试用户！

---

**让AI真正拥有记忆，开启智能工作新时代！** 🚀

如果这个项目对你有帮助，请给我们一个 ⭐ Star！