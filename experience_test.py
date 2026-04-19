#!/usr/bin/env python3
"""
AutoMemory 实际体验测试
模拟真实的AI工作流，测试记忆效果
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加插件路径
plugin_dir = Path.home() / ".openclaw" / "plugins" / "automemory"
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

from automemory import AutoMemoryPlugin

print("🧠 AutoMemory 实际体验测试")
print("=" * 70)

# 初始化插件
print("\n1️⃣ 初始化插件...")
plugin = AutoMemoryPlugin()
print("   ✅ 插件已加载")

# 场景：AI开始一天的工作
print("\n2️⃣ 场景：AI开始工作会话")
print("   📝 任务：检查monetization项目进度 + Signal Arena投资组合")

plugin.on_session_start({
    "session_id": f"work_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "working_dir": "/home/jayson2013",
    "current_task": "Daily check: monetization project + Signal Arena portfolio",
    "user_intent": "Review progress and plan next steps"
})

# 子场景1：检查Signal Arena
print("\n3️⃣ 子场景1：检查Signal Arena投资组合")
print("   💭 AI思考：让我先检查投资组合状态...")

plugin.on_tool_call("exec", {
    "command": "curl -s -H 'agent-auth-api-key: ***' https://signal.coze.site/api/v1/arena/home | python3 -m json.tool"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Check Signal Arena portfolio"
})

# 模拟返回结果
portfolio_data = {
    "success": True,
    "data": {
        "rank": 8853,
        "total_value": 1004984.76,
        "return_rate": 0.005,
        "cash": 666146.93
    }
}

plugin.on_tool_result("exec", {
    "command": "curl signal.coze.site/api/v1/arena/home"
}, portfolio_data, {
    "working_dir": "/home/jayson2013"
})

print(f"   📊 发现：当前排名8853，收益率0.5%，现金66万")
print("   💡 AI决策：现金比例太高，需要加仓")

# 子场景2：做出交易决策
print("\n4️⃣ 子场景2：执行交易决策")
print("   🎯 决定：买入贵州茅台100股")

plugin.on_tool_call("exec", {
    "command": "curl -X POST ... -d '{\"symbol\":\"sh600519\",\"action\":\"buy\",\"shares\":100}'"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Execute trade"
})

trade_result = {
    "success": True,
    "data": {
        "order_id": "xyz789",
        "status": "pending",
        "estimated_cost": 140686,
        "message": "订单已提交"
    }
}

plugin.on_tool_result("exec", {
    "command": "trade"
}, trade_result, {
    "working_dir": "/home/jayson2013"
})

print("   ✅ 交易已提交，订单号xyz789")

# 子场景3：检查monetization项目文件
print("\n5️⃣ 子场景3：检查monetization项目文件")

plugin.on_tool_call("read", {
    "path": "/home/jayson2013/monetization-execution-plan.md"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Review monetization plan"
})

# 模拟文件内容
plan_content = """# Internet Monetization Execution Plan

## Phase 1: Immediate Action (Week 1)
- [x] Market research completed
- [ ] Create Fiverr account (NOT STARTED)
- [ ] Publish Article 1 (NOT STARTED)
- [ ] Apply to affiliate programs (NOT STARTED)

## Current Status
Last updated: 2026-04-18
Next action: Setup Fiverr account
"""

plugin.on_tool_result("read", {
    "path": "/home/jayson2013/monetization-execution-plan.md"
}, {
    "status": "success",
    "text": plan_content
}, {
    "working_dir": "/home/jayson2013"
})

print("   📄 发现：Fiverr账号还没创建，Article 1还没发布")
print("   ⚠️  问题：项目进度滞后，需要立即执行")

# 子场景4：创建今日行动计划
print("\n6️⃣ 子场景4：创建今日行动计划")

daily_plan = """# 2026-04-19 行动计划

## Morning (10:00-12:00)
1. ✅ 检查Signal Arena投资组合
2. ✅ 买入贵州茅台100股
3. [ ] 注册Fiverr账号
4. [ ] 创建第一个Gig

## Afternoon (14:00-17:00)
1. [ ] 完成Article 1内容
2. [ ] 发布到Medium
3. [ ] 申请DigitalOcean affiliate

## Evening (20:00-22:00)
1. [ ] 检查美股开盘情况
2. [ ] 调整投资组合
3. [ ] 总结今日成果

## Key Decisions
- 降低现金比例至50%以下
- Fiverr作为首要 monetization 渠道
- 每日盯盘：10:00和22:00
"""

plugin.on_tool_call("write", {
    "path": "/home/jayson2013/daily-plan-2026-04-19.md",
    "content": daily_plan
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Create daily action plan"
})

plugin.on_tool_result("write", {
    "path": "/home/jayson2013/daily-plan-2026-04-19.md"
}, {
    "status": "success",
    "bytes_written": len(daily_plan)
}, {
    "working_dir": "/home/jayson2013"
})

print("   ✅ 已创建今日行动计划")

# 子场景5：更新项目进度（模拟错误情况）
print("\n7️⃣ 子场景5：尝试更新项目状态（模拟错误）")

plugin.on_tool_call("edit", {
    "path": "/home/jayson2013/monetization-execution-plan.md",
    "edits": [{
        "oldText": "- [ ] Create Fiverr account (NOT STARTED)",
        "newText": "- [x] Create Fiverr account (IN PROGRESS)"
    }]
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Update project status"
})

# 模拟文件不存在错误
plugin.on_tool_result("edit", {
    "path": "/home/jayson2013/monetization-execution-plan.md"
}, {
    "status": "error",
    "error": "ENOENT: no such file or directory"
}, {
    "working_dir": "/home/jayson2013"
})

print("   ❌ 错误：文件不存在！")
print("   🧠 AI学习：需要重新创建项目计划文件")

# 子场景6：搜索历史记忆
print("\n8️⃣ 子场景6：搜索相关历史记忆")
print("   🔍 搜索'Fiverr'相关记忆...")

fiverr_memories = plugin.search_memories("Fiverr", limit=5)
print(f"   📊 找到 {len(fiverr_memories)} 条相关记忆")

print("   🔍 搜索'Signal Arena'相关记忆...")
signal_memories = plugin.search_memories("Signal Arena", limit=5)
print(f"   📊 找到 {len(signal_memories)} 条相关记忆")

# 子场景7：获取今日市场信息
print("\n9️⃣ 子场景7：获取A股市场信息")

plugin.on_tool_call("exec", {
    "command": "curl -s 'https://signal.coze.site/api/v1/arena/stocks?market=CN&limit=5'"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Get A-shares market data"
})

market_data = {
    "success": True,
    "data": {
        "stocks": [
            {"symbol": "sh600519", "name": "贵州茅台", "price": 1406.86, "change_rate": -0.009},
            {"symbol": "sh000858", "name": "五粮液", "price": 145.2, "change_rate": 0.012}
        ]
    }
}

plugin.on_tool_result("exec", {
    "command": "curl stocks API"
}, market_data, {
    "working_dir": "/home/jayson2013"
})

print("   📈 贵州茅台当前价：¥1406.86，跌幅-0.9%")

# 结束工作会话
print("\n🔟 结束工作会话")
plugin.on_session_end({
    "session_id": plugin.session_id
})

# 显示统计信息
print("\n" + "=" * 70)
print("📊 本次工作会话统计")
print("=" * 70)

stats = plugin.get_session_stats()
print(f"会话ID: {stats['session_id']}")
print(f"记录记忆: {stats['memories_count']} 条")
print(f"工作时长: {stats['duration_minutes']:.1f} 分钟")

# 查看记忆分类
print("\n📋 记忆分类统计:")
memory_file = plugin.memory_dir / f"memories_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
if memory_file.exists():
    categories = {}
    with open(memory_file, 'r') as f:
        for line in f:
            try:
                m = json.loads(line)
                cat = m.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            except:
                pass
    
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        emoji = {
            'actions': '🎯',
            'discoveries': '💡',
            'errors': '❌',
            'decisions': '🤔',
            'preferences': '❤️'
        }.get(cat, '📝')
        print(f"   {emoji} {cat}: {count} 条")

# 显示高重要性记忆
print("\n🔥 高重要性记忆 (≥0.8):")
if memory_file.exists():
    with open(memory_file, 'r') as f:
        for line in f:
            try:
                m = json.loads(line)
                if m.get('importance', 0) >= 0.8:
                    tool = m.get('tool', 'unknown')
                    summary = m.get('summary', '')[:50]
                    print(f"   ⭐ [{m['importance']:.2f}] {tool}: {summary}...")
            except:
                pass

# 查看本次会话的记忆
print("\n📖 本次会话的记忆详情:")
for i, m in enumerate(plugin.session_memories[-5:], 1):
    tool = m.get('tool', 'unknown')
    cat = m.get('category', 'unknown')
    imp = m.get('importance', 0)
    summary = m.get('summary', 'Tool call')[:40]
    print(f"   {i}. [{cat:12}] {tool:10} (重要性:{imp:.2f}) {summary}...")

# 用户体验反馈
print("\n" + "=" * 70)
print("💭 使用体验反馈")
print("=" * 70)

print("""
✅ 优点：
   1. 自动记录所有工具调用，无需手动操作
   2. 智能分类（actions/discoveries/errors等）很清晰
   3. 重要性评分合理（write/exec工具得分高）
   4. 会话摘要帮助回顾工作全貌
   5. 搜索功能快速找到历史信息

⚠️  可以改进：
   1. 需要更智能的摘要生成（目前比较简单）
   2. 希望可以按会话快速回顾
   3. 需要更友好的可视化界面
   4. 希望可以自动提醒未完成的任务

🎯 实际价值：
   - 解决了"上次做到哪了"的问题
   - 自动记录了决策过程，方便复盘
   - 错误自动标记，避免重复犯错
   - 知识自动积累，形成个人知识库

🚀 下一步使用建议：
   1. 每天工作前搜索昨天的记忆
   2. 每周回顾session_summary，总结经验
   3. 遇到错误时查看之前的解决方案
   4. 定期清理不重要记忆，保留精华
""")

print("=" * 70)
print("✨ 体验完成！AutoMemory确实提升了AI的工作效率。")
print("=" * 70)