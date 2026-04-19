# 🚀 AutoMemory 快速上手指南

## 安装完成！

AutoMemory插件已成功安装到：
```
~/.openclaw/plugins/automemory/
```

## 3分钟快速开始

### 1️⃣ 测试插件
```bash
python3 ~/.openclaw/plugins/automemory/test_plugin.py
```

### 2️⃣ 运行演示
```bash
python3 ~/.openclaw/plugins/automemory/demo_usage.py
```

### 3️⃣ 查看记忆
```bash
# 查看今天的记忆
cat ~/.openclaw/automemory/memories_$(date +%Y-%m-%d).jsonl

# 搜索关键词
grep "你的关键词" ~/.openclaw/automemory/memories_*.jsonl

# 查看会话统计
ls -lt ~/.openclaw/automemory/session_*.json | head -5
```

## 在Python中使用

```python
# 导入插件
import sys
sys.path.insert(0, str(Path.home() / ".openclaw/plugins/automemory"))
from automemory import AutoMemoryPlugin

# 初始化
plugin = AutoMemoryPlugin()

# 开始会话
plugin.on_session_start({
    "session_id": "my_session",
    "working_dir": "/home/user/project"
})

# AI使用工具时自动记录...
# (在工具调用前后自动触发)

# 搜索记忆
memories = plugin.search_memories("关键词", limit=10)
for m in memories:
    print(f"[{m['timestamp']}] {m['tool']}: {m.get('summary', '')}")

# 结束会话
plugin.on_session_end({"session_id": "my_session"})
```

## 记忆存储位置

```
~/.openclaw/automemory/
├── memories_2026-04-19.jsonl    # 每日记忆 (JSON Lines格式)
├── memories_2026-04-20.jsonl    # 每日记忆
├── session_xxx_20260419.json    # 会话摘要
└── ...
```

## 记忆格式

```json
{
  "id": "唯一ID",
  "type": "tool_call|tool_result",
  "tool": "工具名称",
  "timestamp": "2026-04-19T11:16:20",
  "importance": 0.8,
  "category": "actions|discoveries|errors|decisions|preferences",
  "summary": "简短描述",
  "success": true|false
}
```

## 配置选项

编辑 `~/.openclaw/automemory.json`:
```json
{
  "enabled": true,
  "importance_threshold": 0.5,
  "memory_retention_days": 30
}
```

## 常见问题

### Q: 记忆没有保存？
A: 检查 `~/.openclaw/automemory/` 目录是否存在，以及配置中的 `enabled` 是否为 true

### Q: 如何搜索历史记忆？
A: 使用 `plugin.search_memories("关键词")` 或直接 grep 记忆文件

### Q: 会占用多少空间？
A: 每条记忆约500字节，每天最多50条，30天约750KB

### Q: 敏感信息会被记录吗？
A: 不会，API密钥、密码等会自动脱敏为 `***REDACTED***`

## 下一步

- 📖 阅读完整文档：`~/.openclaw/plugins/automemory/README.md`
- 🔧 自定义配置：`~/.openclaw/automemory.json`
- 🧪 运行测试：`python3 ~/.openclaw/plugins/automemory/test_plugin.py`

---

**🎉 开始使用AutoMemory，让AI真正记住重要的事情！**