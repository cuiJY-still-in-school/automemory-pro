# AutoMemory Pro 🧠

> 让AI真正拥有"记忆"和"智慧"的OpenClaw插件

## ✨ 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash
```

## 🚀 快速开始

```bash
# 查看仪表盘（默认）
automemory

# 生成每日简报
automemory briefing

# 快速记笔记
automemory note "我的灵感"

# 查看状态
automemory status
```

## 🎯 核心功能

| 命令 | 功能 | 说明 |
|------|------|------|
| `automemory` | 📊 仪表盘 | 一眼看清所有状态 |
| `automemory briefing` | 📋 每日简报 | 每天自动生成 |
| `automemory note "内容"` | 🖊️ 快速笔记 | 随手记录灵感 |
| `automemory status` | 📈 状态查看 | 查看记忆统计 |

## 📊 仪表盘预览

```
╔══════════════════════════════════════════════════╗
║              🧠 AutoMemory Dashboard              ║
║                📅 2026-04-19 14:42                ║
╠══════════════════════════════════════════════════╣
║ 📊 记忆统计                                           ║
║   总记忆: 59 条                                      ║
║   今日: 59 条 | 本周: 59 条                            ║
╠══════════════════════════════════════════════════╣
║ 🎯 待办任务                                           ║
║   □ 完善个人资料                                       ║
║   □ 申请3个Affiliate Program                        ║
╠══════════════════════════════════════════════════╣
║ ⚠️ 逾期提醒                                          ║
║   ✅ 没有逾期任务，继续保持！                                 ║
╠══════════════════════════════════════════════════╣
║ 📧 下午适合沟通协调                                       ║
╚══════════════════════════════════════════════════╝
```

## 🖊️ 快速笔记

```bash
# 记录灵感
note -t idea "可以做X项目"

# 记录待办
note -t todo "要完成的任务"

# 记录问题
note -t bug "发现了一个问题"

# 查看最近笔记
note -l 10
```

## 📋 每日简报

```bash
automemory briefing
```

```
📋 每日简报 - 2026-04-19

🎯 今日待办
  1. 🟡 [Fiverr] 完善个人资料
  2. 🟡 [Article] 完成大纲

📊 昨日进展
  • 注册Fiverr账号 ✅
  • 设置AutoMemory ✅

💡 建议
  • 下午适合沟通协调
```

## 📁 项目结构

```
~/.openclaw/plugins/automemory/
├── dashboard.py       # 仪表盘
├── daily_briefing.py # 每日简报
├── note.py          # 快速笔记
├── automemory_pro.py # 核心插件
└── install.sh       # 安装脚本

~/.openclaw/automemory/
├── memories_*.jsonl  # 记忆数据
├── notes/            # 笔记
├── tasks.json        # 任务
└── briefings/        # 简报
```

## 📈 版本历史

### v1.6.0 (2026-04-19)
- 🆕 仪表盘 - 一眼看清华
- 🆕 快速笔记 - 随手记录
- 🐛 修复日志噪音

### v1.5.0 (2026-04-19)
- 📋 每日简报生成器

### v1.0.0 (2026-04-19)
- 初始版本

---

**让AI真正拥有记忆！** 🧠