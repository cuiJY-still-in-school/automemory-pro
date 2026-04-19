# AutoMemory Pro 🧠

> 让AI真正拥有"记忆"和"智慧"的OpenClaw插件

## ✨ 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash
```

## 🚀 快速开始

```bash
automacity              # 仪表盘（默认）
automacity briefing     # 每日简报
automacity note "内容"  # 快速笔记
automacity qstat        # 快速统计
```

## 📊 功能一览

| 命令 | 功能 | 说明 |
|------|------|------|
| `automacity` | 📊 仪表盘 | 一眼看清所有状态 |
| `automacity briefing` | 📋 每日简报 | 每天自动生成 |
| `automacity note` | 🖊️ 快速笔记 | 随手记录灵感 |
| `automacity history` | 📜 会话历史 | 查看活动时间线 |
| `automacity search` | 🔍 智能搜索 | 自然语言搜索 |
| `automacity achievements` | 🏆 成就系统 | 解锁成就激励 |
| `automacity remind` | ⏰ 定时提醒 | 系统通知 |
| `automacity weekly` | 📊 周报生成 | 自动生成周报 |
| `automacity export` | 📦 数据导出 | JSON/MD/CSV/HTML |
| `automacity health` | 🩺 健康检查 | 系统状态诊断 |
| `automacity backup` | 📦 GitHub备份 | 自动备份记忆 |
| `automacity tags` | 🏷️ 标签管理 | 记忆分类 |
| `automacity cleanup` | 🧹 内存清理 | 清理重复/旧记忆 |
| `automacity qstat` | 📈 快速统计 | 关键指标 |
| `automacity api` | 🌐 API服务 | HTTP API |

## 📈 快速统计

```bash
$ automacity qstat
📊 AutoMemory 快速统计
========================================
  总记忆:   59
  今日:    59 ██████████
  成功率:  91.5%

🔧 Top工具:
  exec           33
  write          16
```

## 🏆 成就系统

```
🎉🎉🎉 新成就解锁！
  🌱 初识 - 记录第一条记忆
  📝 小试牛刀 - 记录10条记忆
  📅 第一天 - 第一次使用
```

## 📦 数据导出

```bash
automacity export json -d 7    # 最近7天JSON
automacity export md -o out.md # Markdown
automacity export csv          # CSV格式
```

## 🧹 内存清理

```bash
automacity cleanup --dry-run   # 预览
automacity cleanup --execute    # 执行清理
```

## 🌐 API服务

```bash
automacity api start --port 8080
curl http://localhost:8080/api/stats
```

## 📁 项目结构

```
~/.openclaw/plugins/automemory/
├── dashboard.py      # 仪表盘
├── daily_briefing.py # 每日简报
├── note.py          # 快速笔记
├── history.py       # 会话历史
├── search.py        # 智能搜索
├── achievements.py  # 成就系统
├── remind.py        # 定时提醒
├── weekly_report.py # 周报生成
├── export.py        # 数据导出
├── health.py        # 健康检查
├── backup.py        # GitHub备份
├── tags.py          # 标签管理
├── cleanup.py       # 内存清理
├── qstat.py         # 快速统计
├── api.py           # API服务
└── install.sh      # 安装脚本
```

## 📈 版本历史

### v2.1.0 (2026-04-19)
- 🆕 标签系统 (tags)
- 🆕 内存清理 (cleanup)
- 🆕 快速统计 (qstat)
- 🆕 API服务 (api)

### v2.0.0 (2026-04-19)
- 🆕 健康检查 (health)
- 🆕 GitHub备份 (backup)

### v1.9.0 (2026-04-19)
- 🆕 数据导出 (export)

### v1.8.0 (2026-04-19)
- 🆕 周报生成 (weekly)
- 🆕 定时提醒 (remind)

### v1.7.0 (2026-04-19)
- 🆕 会话历史 (history)
- 🆕 智能搜索 (search)
- 🆕 成就系统 (achievements)

### v1.6.0 (2026-04-19)
- 🆕 仪表盘 (dashboard)
- 🆕 快速笔记 (note)

### v1.5.0 (2026-04-19)
- 📋 每日简报 (briefing)

---

**让AI真正拥有记忆！** 🧠

**GitHub**: https://github.com/cuiJY-still-in-school/automemory-pro