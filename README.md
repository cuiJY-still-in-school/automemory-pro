# AutoMemory Plugin - 自动记忆保存插件

让AI自动记住重要信息的OpenClaw插件。

## 🎯 功能特性

- **自动捕获**: 在AI使用工具时自动保存重要信息
- **智能分析**: 自动分类（决策、行动、发现、错误、偏好）
- **重要性评分**: 自动计算每条记忆的重要性（0-1分）
- **语义搜索**: 支持关键词搜索历史记忆
- **自动清理**: 自动清理过期记忆（默认30天）
- **集成MEMORY.md**: 高重要性记忆自动同步到MEMORY.md

## 📦 安装

### 1. 克隆或复制插件
```bash
# 插件目录
mkdir -p ~/.openclaw/plugins/automemory
# 复制文件到该目录
cp automemory.py plugin.json hook.py ~/.openclaw/plugins/automemory/
```

### 2. 安装依赖
```bash
# 无需额外依赖，使用Python标准库
```

### 3. 启用Hook（可选）
```bash
# 创建hook链接
ln -s ~/.openclaw/plugins/automemory/hook.py ~/.openclaw/hooks/automemory_hook.py
```

### 4. 配置（可选）
创建配置文件 `~/.openclaw/automemory.json`:
```json
{
  "enabled": true,
  "auto_save": true,
  "importance_threshold": 0.5,
  "max_memories_per_session": 50,
  "memory_retention_days": 30,
  "categories": ["decisions", "actions", "discoveries", "errors", "preferences"],
  "excluded_tools": ["memory_search", "memory_get", "session_status"]
}
```

## 🚀 使用方法

### 作为独立模块使用
```python
from automemory import AutoMemoryPlugin

# 初始化插件
plugin = AutoMemoryPlugin()

# 模拟会话开始
plugin.on_session_start({
    "session_id": "session_001",
    "working_dir": "/home/user/project"
})

# 在工具调用时记录
plugin.on_tool_call("write", {
    "path": "/home/user/project/README.md",
    "content": "# Project\n..."
}, {
    "working_dir": "/home/user/project",
    "current_task": "creating documentation"
})

# 在工具返回时记录结果
plugin.on_tool_result("write", {...}, {
    "status": "success"
}, {...})

# 搜索历史记忆
memories = plugin.search_memories("README")
for memory in memories:
    print(f"[{memory['timestamp']}] {memory['summary']}")

# 获取会话统计
stats = plugin.get_session_stats()
print(f"本会话记录了 {stats['memories_count']} 条记忆")

# 会话结束
plugin.on_session_end({"session_id": "session_001"})
```

### 在OpenClaw中使用
安装后自动生效，AI使用工具时会自动记录。

## 📁 文件结构

```
~/.openclaw/automemory/
├── memories_2026-04-19.jsonl    # 每日记忆文件
├── memories_2026-04-20.jsonl    # 每日记忆文件
├── session_xxx_20260419.json    # 会话摘要
└── ...
```

## 🔍 记忆格式

每条记忆包含以下字段：

```json
{
  "id": "唯一ID",
  "type": "tool_call|tool_result",
  "tool": "工具名称",
  "params": {"清理后的参数"},
  "timestamp": "2026-04-19T10:30:00",
  "session_id": "会话ID",
  "category": "decisions|actions|discoveries|errors|preferences",
  "importance": 0.8,
  "summary": "摘要描述",
  "key_data": {"关键数据"},
  "discoveries": ["发现1", "发现2"],
  "decisions": ["决策1"],
  "errors": ["错误1"],
  "success": true|false
}
```

## 🎛️ 配置选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `enabled` | true | 是否启用插件 |
| `auto_save` | true | 是否自动保存 |
| `importance_threshold` | 0.5 | 重要性阈值，低于此值不保存 |
| `max_memories_per_session` | 50 | 每会话最大记忆数 |
| `memory_retention_days` | 30 | 记忆保留天数 |
| `categories` | [...] | 记忆分类列表 |
| `excluded_tools` | [...] | 排除的工具列表 |

## 🧠 工作原理

### 1. 工具调用时
- 记录工具名称、参数、上下文
- 计算重要性分数
- 如果超过阈值，保存到记忆文件

### 2. 工具返回时
- 分析结果（成功/失败/发现/错误）
- 提取关键信息
- 生成分类和摘要
- 保存到记忆文件
- 高重要性记忆同步到MEMORY.md

### 3. 重要性评分算法
基础分（0.5）+ 工具类型权重 + 关键词加权 + 路径加权

例如：
- `write`/`edit` 工具：+0.8（创建/修改文件很重要）
- `exec` 命令：+0.6（执行命令有风险）
- 包含"error"/"fail"关键词：+0.1
- 涉及config/memory等关键路径：+0.15

### 4. 自动分类
- **decisions**: 决策类（计划、策略、选择）
- **actions**: 行动类（创建、修改、执行）
- **discoveries**: 发现类（找到、注意到、检测到）
- **errors**: 错误类（失败、异常、警告）
- **preferences**: 偏好类（喜欢、需要、想要）

## 💡 使用场景

### 场景1：项目管理
```python
# AI执行项目任务时自动记录
plugin.on_tool_call("write", {"path": "project/plan.md", ...})
# 保存：创建了项目计划文件

plugin.on_tool_result("exec", {...}, {"stdout": "Build successful"})
# 保存：构建成功，项目可运行
```

### 场景2：错误追踪
```python
# AI遇到错误时自动记录
plugin.on_tool_result("exec", {...}, {"exit_code": 1, "stderr": "Error: ..."})
# 保存：执行命令失败，错误信息...
# 自动标记为error分类，高重要性
```

### 场景3：知识积累
```python
# AI发现重要信息时
plugin.on_tool_result("web_fetch", {...}, {"text": "Important API change..."})
# 保存：发现API变更，关键信息...
# 自动标记为discoveries分类
```

### 场景4：用户偏好学习
```python
# 记录用户偏好
# 当AI检测到用户说"我喜欢..."、"我需要..."
# 自动保存为preferences分类
```

## 🔍 查询记忆

### 方法1：直接读取文件
```bash
# 查看今天的记忆
cat ~/.openclaw/automemory/memories_2026-04-19.jsonl

# 搜索关键词
grep "Signal Arena" ~/.openclaw/automemory/memories_*.jsonl
```

### 方法2：使用Python API
```python
from automemory import AutoMemoryPlugin

plugin = AutoMemoryPlugin()

# 搜索记忆
memories = plugin.search_memories("monetization", limit=10)
for m in memories:
    print(f"[{m['timestamp']}] {m['tool']}: {m['summary']}")
```

### 方法3：查看会话摘要
```bash
# 查看最近的会话摘要
ls -lt ~/.openclaw/automemory/session_*.json | head -5
cat ~/.openclaw/automemory/session_xxx_20260419.json
```

## 📊 统计信息

获取当前会话的统计：
```python
stats = plugin.get_session_stats()
print(f"""
会话ID: {stats['session_id']}
记忆数量: {stats['memories_count']}
会话时长: {stats['duration_minutes']:.1f} 分钟
""")
```

## 🧹 自动清理

插件会自动清理：
- 超过`memory_retention_days`天的旧记忆文件
- 过期的会话摘要
- 保留最近30天的记忆（可配置）

## 🔐 安全考虑

- **敏感信息脱敏**: API密钥、密码等自动替换为`***REDACTED***`
- **本地存储**: 所有记忆保存在本地，不上传云端
- **访问控制**: 记忆文件存储在用户目录下，受系统权限保护

## 🐛 故障排除

### 问题1：记忆没有保存
**检查**:
- 插件是否启用：`enabled: true`
- 重要性阈值是否过高：`importance_threshold: 0.5`
- 工具是否在排除列表中

### 问题2：MEMORY.md没有更新
**检查**:
- 记忆的重要性是否≥0.8
- MEMORY.md文件是否存在
- 文件权限是否正确

### 问题3：搜索不到记忆
**检查**:
- 记忆文件是否存在：`~/.openclaw/automemory/`
- 搜索关键词是否匹配
- 记忆是否已过期被清理

## 🔄 与其他工具集成

### 与Signal Arena集成
```python
# 自动记录投资组合变化
plugin.on_tool_result("exec", 
    {"command": "curl signal.coze.site/api/portfolio"},
    {"stdout": "{\"rank\": 8853, ...}"}
)
# 保存：投资组合排名变化到8853
```

### 与Monetization项目集成
```python
# 记录Fiverr设置进度
plugin.on_tool_call("exec", {"command": "fiverr setup"})
plugin.on_tool_result("exec", {...}, {"stdout": "Fiverr account created"})
# 保存：成功创建Fiverr账号
```

## 📝 开发计划

- [ ] 支持更多工具类型的智能分析
- [ ] 添加向量数据库支持语义搜索
- [ ] 支持记忆导出为PDF/Markdown
- [ ] 添加可视化仪表盘
- [ ] 支持团队协作记忆共享
- [ ] 集成LLM进行记忆摘要生成

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 License

MIT License

---

**让AI真正记住重要的事情！** 🧠✨