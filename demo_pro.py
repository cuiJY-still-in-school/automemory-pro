#!/usr/bin/env python3
"""
AutoMemory Pro 完整演示
展示主动记忆推荐和任务状态追踪的核心价值
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加路径
sys.path.insert(0, str(Path.home() / ".openclaw/plugins/automemory"))
from automemory_pro import AutoMemoryPro

print("🚀 AutoMemory Pro 完整演示")
print("=" * 70)
print("演示核心功能：")
print("  1. 主动记忆推荐 - 自动找到相关记忆")
print("  2. 任务状态追踪 - 自动追踪TODO完成情况")
print("  3. 智能工作流 - 从计划到执行的完整追踪")
print("=" * 70)

# 初始化插件
plugin = AutoMemoryPro()

# ============================================
# 场景1：新的一天开始工作
# ============================================
print("\n📅 场景1：新的一天开始工作")
print("-" * 70)

print("🌅 早上9:00，用户说：'继续推进monetization项目'")
print("\n💭 AI的思考过程：")
print("   1. 用户说'继续' → 说明之前已经开始")
print("   2. 需要知道'之前做到哪了'")
print("   3. 自动搜索相关记忆...")

# 会话开始，自动推荐相关记忆
recommendations = plugin.on_session_start({
    "session_id": f"morning_work_{datetime.now().strftime('%Y%m%d')}",
    "working_dir": "/home/jayson2013",
    "current_task": "继续推进monetization项目，完成Fiverr设置",
    "user_intent": "继续昨天的工作"
})

print("\n✨ AutoMemory自动推荐相关记忆：")
if recommendations:
    for i, m in enumerate(recommendations[:5], 1):
        relevance = m.get('relevance_score', 0)
        tool = m.get('tool', 'unknown')
        summary = m.get('summary', '')[:50]
        print(f"   {i}. [相关性:{relevance:.2f}] {tool:10} → {summary}...")
else:
    print("   （当前记忆库中暂无高度相关的记忆）")
    print("   → 将创建新的工作记忆")

# 检查待办任务
pending_tasks = plugin.task_tracker.get_pending_tasks(limit=5)
print(f"\n📋 待办任务提醒：{len(pending_tasks)}个")
if pending_tasks:
    for i, task in enumerate(pending_tasks, 1):
        created = datetime.fromisoformat(task["created_at"])
        days_ago = (datetime.now() - created).days
        status = "⚠️ 逾期" if days_ago > 3 else "⏳ 待办"
        print(f"   {i}. {status} {task['text'][:50]}... ({days_ago}天前)")
else:
    print("   ✅ 没有待办任务")

# ============================================
# 场景2：检查项目文件，提取任务
# ============================================
print("\n📂 场景2：读取项目计划文件")
print("-" * 70)

# 模拟读取项目计划文件
plan_content = """
# Monetization 项目计划

## Phase 1: 立即行动（第1周）

### 周一（今天）
- [ ] 注册Fiverr账号
- [ ] 创建第一个Gig（数据清洗服务）
- [ ] 完善个人资料

### 周二
- [ ] 申请3个Affiliate Program
- [ ] 完成Article 1大纲

### 周三-周五
- [ ] 发布Article 1到Medium
- [ ] 推广内容到社交媒体

## 关键决策
1. Fiverr作为首要变现渠道（快速看到收益）
2. 内容营销建立长期流量
3. 每日盯盘Signal Arena（10:00和22:00）

## 当前障碍
- Fiverr账号还没注册
- 没有完成的文章
- Affiliate Program还没申请
"""

print("📄 从项目计划中提取任务...")

# 模拟工具调用
plugin.on_tool_call("read", {
    "path": "/home/jayson2013/monetization-plan.md"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Review project plan"
})

# 模拟返回结果
plugin.on_tool_result("read", {
    "path": "/home/jayson2013/monetization-plan.md"
}, {
    "status": "success",
    "text": plan_content
}, {
    "working_dir": "/home/jayson2013"
})

# 提取任务
new_tasks = plugin.task_tracker.extract_tasks_from_content(
    plan_content,
    source="monetization-plan.md"
)

print(f"   ✅ 自动提取 {len(new_tasks)} 个任务")
for i, task in enumerate(new_tasks[:5], 1):
    task_id = plugin.task_tracker.add_task(
        task["text"],
        source=task["source"],
        priority="high" if "Fiverr" in task["text"] else "medium"
    )
    status = "✅ 已完成" if task["status"] == "completed" else "⏳ 待办"
    print(f"   {i}. {status} {task['text'][:45]}...")

# ============================================
# 场景3：执行任务并自动追踪完成状态
# ============================================
print("\n🎯 场景3：执行具体任务")
print("-" * 70)

print("🚀 执行任务：注册Fiverr账号")

# 模拟执行命令
plugin.on_tool_call("exec", {
    "command": "curl -X POST https://fiverr.com/api/register -d '{\"username\":\"clawquant\",\"email\":\"***\"}'"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Register Fiverr account"
})

# 模拟成功结果
plugin.on_tool_result("exec", {
    "command": "register fiverr"
}, {
    "status": "success",
    "message": "Fiverr account created successfully",
    "data": {
        "username": "clawquant",
        "account_id": "fv_123456",
        "status": "active"
    }
}, {
    "working_dir": "/home/jayson2013"
})

# 检查是否完成任务
completed = plugin.task_tracker.check_task_completion(
    plugin.session_memories[-1]
)

if completed:
    print(f"   ✅ AutoMemory自动检测到任务完成：")
    for task_text in completed:
        print(f"      → '{task_text[:50]}...' 已标记为完成")
else:
    # 手动标记完成
    plugin.task_tracker.mark_completed(
        task_text="注册Fiverr账号",
        memory_id=plugin.session_memories[-1].get("id")
    )
    print("   ✅ 任务已手动标记为完成")

# ============================================
# 场景4：创建新的工作计划
# ============================================
print("\n📝 场景4：创建今日行动计划")
print("-" * 70)

daily_plan = """# 2026-04-19 行动计划

## ✅ 已完成（上午）
1. ✅ 注册Fiverr账号（clawquant）
2. ⏳ 创建第一个Gig（待完成）
3. ⏳ 完善个人资料（待完成）

## ⏳ 待完成（下午）
1. [ ] 创建数据清洗服务Gig
2. [ ] 设置定价（$50/$80/$120）
3. [ ] 申请DigitalOcean Affiliate
4. [ ] 完成Article 1大纲

## 🎯 关键决策
- Fiverr定价策略：低价起步，积累评价后涨价
- 专注数据清洗服务（最擅长）
- 今日目标：完成Fiverr基础设置
"""

plugin.on_tool_call("write", {
    "path": "/home/jayson2013/daily-plan-2026-04-19.md",
    "content": daily_plan
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Create daily plan"
})

plugin.on_tool_result("write", {
    "path": "/home/jayson2013/daily-plan-2026-04-19.md"
}, {
    "status": "success",
    "bytes_written": len(daily_plan)
}, {
    "working_dir": "/home/jayson2013"
})

# 从新计划中再次提取任务
new_tasks_2 = plugin.task_tracker.extract_tasks_from_content(daily_plan, "daily-plan")
for task in new_tasks_2:
    if "Fiverr" in task["text"] or "Gig" in task["text"]:
        priority = "high"
    else:
        priority = "medium"
    
    plugin.task_tracker.add_task(task["text"], source="daily-plan", priority=priority)

print("   ✅ 已创建今日行动计划")
print("   ✅ 自动提取新的待办任务")

# ============================================
# 场景5：遇到错误，自动记录并学习
# ============================================
print("\n⚠️  场景5：遇到错误并记录")
print("-" * 70)

print("❌ 尝试上传头像时出错：")

plugin.on_tool_call("exec", {
    "command": "curl -X POST https://fiverr.com/api/upload-avatar -F 'file=@avatar.jpg'"
}, {
    "working_dir": "/home/jayson2013",
    "current_task": "Upload Fiverr avatar"
})

plugin.on_tool_result("exec", {
    "command": "upload avatar"
}, {
    "exit_code": 1,
    "stderr": "Error: File too large. Max size is 2MB. Current: 5.3MB"
}, {
    "working_dir": "/home/jayson2013"
})

print("   ❌ 错误：文件太大（5.3MB > 2MB限制）")
print("   🧠 AutoMemory已自动记录此错误")
print("   → 下次遇到头像上传时，AI会提醒'文件需小于2MB'")

# ============================================
# 场景6：生成工作摘要
# ============================================
print("\n📊 场景6：生成今日工作摘要")
print("-" * 70)

summary = plugin.get_work_summary()
print(summary["summary_text"])

# ============================================
# 场景7：智能搜索与推荐
# ============================================
print("\n🔍 场景7：智能搜索与推荐")
print("-" * 70)

# 用户询问相关问题
queries = [
    "Fiverr注册",
    "monetization进度",
    "今天的任务"
]

for query in queries:
    print(f"\n💬 用户问：'{query}'")
    print("   AI搜索相关记忆...")
    
    result = plugin.search_and_recommend(query, limit=3)
    
    if result["combined"]:
        print(f"   找到 {len(result['combined'])} 条相关记忆：")
        for i, m in enumerate(result["combined"], 1):
            relevance = m.get("relevance_score", 0.5)
            tool = m.get("tool", "unknown")
            summary = m.get("summary", "")[:40]
            print(f"   {i}. [{relevance:.2f}] {tool}: {summary}...")
    else:
        print("   暂无相关记忆")

# ============================================
# 场景8：结束工作，生成完整报告
# ============================================
print("\n🏁 场景8：结束工作会话")
print("-" * 70)

# 获取最终任务统计
final_stats = plugin.task_tracker.get_task_summary()
print("📈 今日任务完成情况：")
print(f"   总任务: {final_stats['total']}")
print(f"   已完成: {final_stats['completed']} ({final_stats['completion_rate']*100:.1f}%)")
print(f"   待完成: {final_stats['pending']}")
print(f"   逾期: {final_stats['overdue']}")

# 结束会话
plugin.on_session_end({
    "session_id": plugin.session_id
})

# ============================================
# 总结
# ============================================
print("\n" + "=" * 70)
print("🎉 AutoMemory Pro 演示完成！")
print("=" * 70)

print("\n📊 演示成果统计：")
print(f"   记录记忆: {len(plugin.session_memories)} 条")
print(f"   提取任务: {final_stats['total']} 个")
print(f"   完成任务: {final_stats['completed']} 个")
print(f"   识别错误: 1 个（头像上传大小限制）")

print("\n✨ 核心价值体现：")
print("   ✅ 无需手动搜索，自动推荐相关记忆")
print("   ✅ 自动从文档中提取和追踪任务")
print("   ✅ 自动检测任务完成情况")
print("   ✅ 自动记录错误，避免重复踩坑")
print("   ✅ 自动生成工作摘要")

print("\n💡 使用前后的对比：")
print("\n   使用前：")
print("   用户：'继续monetization项目'")
print("   AI：'好的，请稍等，让我重新检查一下...'")
print("       [重新执行所有检查命令，浪费5分钟]")
print("\n   使用后：")
print("   用户：'继续monetization项目'")
print("   AI：'好的！根据记忆：'")
print("       1. Fiverr账号已注册（clawquant）✅")
print("       2. 还有3个任务待完成：")
print("          - 创建Gig")
print("          - 完善资料")  
print("          - 申请Affiliate")
print("       3. 今天遇到一个问题：头像需<2MB")
print("       建议下一步：创建数据清洗Gig")

print("\n" + "=" * 70)
print("🚀 AutoMemory Pro 让AI真正拥有了'记忆'和'智慧'！")
print("=" * 70)