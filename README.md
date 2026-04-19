# AutoMemory Pro 🧠

> 让AI真正拥有"记忆"和"智慧"的OpenClaw插件

## ✨ 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash
```

## 🚀 快速开始

```bash
# 仪表盘（默认）
automacity

# 每日简报
automacity briefing

# 快速记笔记
automacity note "我的灵感"

# 查看历史
automacity history

# 智能搜索
automacity search Fiverr

# 成就系统
automacity achievements
```

## 🎯 核心功能

| 命令 | 功能 | 说明 |
|------|------|------|
| `automacity` | 📊 仪表盘 | 一眼看清所有状态 |
| `automacity briefing` | 📋 每日简报 | 每天自动生成 |
| `automacity note "内容"` | 🖊️ 快速笔记 | 随手记录灵感 |
| `automacity history` | 📜 会话历史 | 查看活动时间线 |
| `automacity search` | 🔍 智能搜索 | 自然语言搜索 |
| `automacity achievements` | 🏆 成就系统 | 解锁成就激励 |

## 📊 仪表盘预览

```
╔══════════════════════════════════════════════════╗
║              🧠 AutoMemory Dashboard              ║
║                📅 2026-04-19 14:42                ║
╠══════════════════════════════════════════════════╣
║ 📊 记忆统计                                           ║
║   总记忆: 59 条                                      ║
╠══════════════════════════════════════════════════╣
║ 🎯 待办任务                                           ║
║   □ 完善个人资料                                       ║
╠══════════════════════════════════════════════════╣
║ ⚠️ 逾期提醒                                          ║
║   ✅ 没有逾期任务，继续保持！                                 ║
╚══════════════════════════════════════════════════╝
```

## 📜 会话历史

```bash
automacity history -d 7    # 最近7天
automacity history -e      # 只看错误
```

## 🔍 智能搜索

```bash
automacity search Fiverr      # 搜索关键词
automacity search 今天的命令   # 今天执行的命令
automacity search 错误        # 所有错误
```

## 🏆 成就系统

```
🎉🎉🎉 新成就解锁！

  🌱 初识 - 记录第一条记忆
  📝 小试牛刀 - 记录10条记忆
  📅 第一天 - 第一次使用

🏆 成就墙: 7/13 已解锁
```

## 📖 快速笔记

```bash
automacity note "灵光一现的想法"
automacity note -t todo "要完成的任务"
automacity note -t idea "可以做X项目"
```

## 📁 项目结构

```
~/.openclaw/plugins/automemory/
├── dashboard.py       # 仪表盘
├── daily_briefing.py # 每日简报
├── note.py          # 快速笔记
├── history.py       # 会话历史
├── search.py        # 智能搜索
├── achievements.py  # 成就系统
└── install.sh      # 安装脚本
```

## 📈 版本历史

### v1.7.0 (2026-04-19)
- 🆕 会话历史查看器
- 🆕 智能搜索系统
- 🆕 成就系统

### v1.6.0 (2026-04-19)
- 🆕 仪表盘
- 🆕 快速笔记

### v1.5.0 (2026-04-19)
- 📋 每日简报生成器

---

**让AI真正拥有记忆！** 🧠