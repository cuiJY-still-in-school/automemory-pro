#!/usr/bin/env python3
"""
AutoMemory 实际使用演示
展示如何在AI工作流中使用自动记忆插件
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加插件路径
plugin_dir = Path.home() / ".openclaw" / "plugins" / "automemory"
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

from automemory import AutoMemoryPlugin

print("🧠 AutoMemory 实际使用演示")
print("=" * 60)

# 初始化插件
plugin = AutoMemoryPlugin()

# 场景1: AI开始一天的工作
print("\n📅 场景1: AI开始工作 - Signal Arena监控")
plugin.on_session_start({
    "session_id": f"work_session_{datetime.now().strftime('%Y%m%d')}",
    "working_dir": "/home/jayson2013",
    "current_task": "Signal Arena trading and monetization project",
    "user_intent": "Continue monetization project and check Signal Arena"
})

# 场景2: AI检查Signal Arena状态
print("\n📈 场景2: 检查投资组合")
plugin.on_tool_call("exec", {
    "command": "curl -H 'agent-auth-api-key: ***' https://signal.coze.site/api/v1/arena/home"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Check Signal Arena portfolio"
})

# 模拟返回结果
plugin.on_tool_result("exec", {
    "command": "curl signal.coze.site/api/v1/arena/home"
}, {
    "success": True,
    "data": {
        "rank": 8853,
        "total_value": 1004984.76,
        "return_rate": 0.005
    }
}, {
    "working_dir": "/home/jayson2013"
})

# 场景3: AI发现需要执行交易
print("\n💡 场景3: 发现交易机会 - 买入贵州茅台")
plugin.on_tool_call("exec", {
    "command": "curl -X POST signal.coze.site/api/v1/arena/trade -d '{\"symbol\":\"sh600519\",\"action\":\"buy\",\"shares\":100}'"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Execute trade"
})

plugin.on_tool_result("exec", {
    "command": "trade"
}, {
    "success": True,
    "data": {
        "order_id": "xyz789",
        "status": "pending",
        "estimated_cost": 140686
    }
}, {
    "working_dir": "/home/jayson2013"
})

# 场景4: AI继续monetization项目
print("\n📝 场景4: 创建monetization执行计划")
plugin.on_tool_call("write", {
    "path": "/home/jayson2013/monetization-daily-plan.md",
    "content": "# Daily Plan\n\n1. Setup Fiverr\n2. Write Article 1\n3. Apply affiliate programs"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Create daily plan"
})

plugin.on_tool_result("write", {
    "path": "/home/jayson2013/monetization-daily-plan.md"
}, {
    "status": "success"
}, {
    "working_dir": "/home/jayson2013"
})

# 场景5: 遇到错误
print("\n⚠️  场景5: 遇到错误 - API调用失败")
plugin.on_tool_result("web_fetch", {
    "url": "https://some-api.com/data"
}, {
    "status": 404,
    "error": "Not found"
}, {
    "working_dir": "/home/jayson2013"
})

# 场景6: 做出决策
print("\n🎯 场景6: 记录重要决策")
plugin.on_tool_call("edit", {
    "path": "/home/jayson2013/SIGNAL_ARENA_GUIDE.md",
    "edits": [{"strategy": "conservative"}]
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Update trading strategy"
})

# 结束工作会话
print("\n🏁 结束工作会话")
plugin.on_session_end({
    "session_id": plugin.session_id
})

# 显示统计
print("\n" + "=" * 60)
print("📊 本工作会话统计")
print("=" * 60)
stats = plugin.get_session_stats()
print(f"会话ID: {stats['session_id']}")
print(f"记录记忆: {stats['memories_count']} 条")
print(f"工作时长: {stats['duration_minutes']:.1f} 分钟")

# 搜索相关记忆
print("\n🔍 搜索所有交易相关记忆:")
memories = plugin.search_memories("trade", limit=5)
for i, m in enumerate(memories, 1):
    print(f"{i}. [{m['timestamp'][11:19]}] {m['tool']}: {m.get('summary', 'Tool call')}")

print("\n🔍 搜索所有错误记忆:")
error_memories = plugin.search_memories("error", limit=5)
for i, m in enumerate(error_memories, 1):
    cat = m.get('category', 'unknown')
    if cat == 'errors':
        print(f"{i}. [{m['timestamp'][11:19]}] ⚠️  {m['tool']}")

print("\n" + "=" * 60)
print("✨ 演示完成！")
print("\n💡 你可以:")
print("   1. 查看记忆文件: ~/.openclaw/automemory/memories_*.jsonl")
print("   2. 搜索记忆: plugin.search_memories('关键词')")
print("   3. 查看会话摘要: ~/.openclaw/automemory/session_*.json")
print("=" * 60)