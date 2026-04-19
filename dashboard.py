#!/usr/bin/env python3
"""
AutoMemory Pro - 仪表盘
Dashboard - 一目了然看到所有关键信息

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# 添加插件路径
PLUGIN_DIR = Path(__file__).parent
sys.path.insert(0, str(PLUGIN_DIR))

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING)

try:
    from automemory_pro import AutoMemoryPro
    from memory_compressor import MemoryCompressor
    from daily_briefing import DailyBriefingGenerator
except ImportError:
    print("❌ AutoMemory Pro 未安装")
    print("   运行: curl -fsSL ... | bash 安装")
    sys.exit(1)


def get_dashboard_data() -> Dict:
    """获取仪表盘数据"""
    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stats": {},
        "pending_tasks": [],
        "overdue_tasks": [],
        "recent_memories": [],
        "goals": [],
        "tips": []
    }
    
    try:
        # 获取记忆统计
        compressor = MemoryCompressor()
        stats = compressor.get_memory_stats()
        data["stats"] = {
            "total": stats.total_memories,
            "today": stats.today_memories,
            "week": stats.week_memories,
            "month": stats.month_memories,
            "active_days": len(set(
                m.get("timestamp", "")[:10] 
                for m in []  # 简化统计
            ))
        }
    except:
        data["stats"] = {"total": 0, "today": 0, "week": 0, "month": 0}
    
    try:
        # 获取任务
        plugin = AutoMemoryPro()
        pending = plugin.task_tracker.get_pending_tasks(limit=10)
        data["pending_tasks"] = [
            {"text": t.get("text", "")[:40], "days": calculate_days(t.get("created_at", ""))}
            for t in pending[:5]
        ]
        
        # 获取逾期任务
        summary = plugin.task_tracker.get_task_summary()
        data["overdue_tasks"] = summary.get("overdue", 0)
        
    except Exception as e:
        data["pending_tasks"] = []
        data["overdue_tasks"] = 0
    
    try:
        # 获取提醒
        reminders = plugin.check_reminders()
        if reminders.get("routine"):
            data["tips"].append(f"📅 {len(reminders['routine'])}个定时任务待执行")
        if reminders.get("context"):
            data["tips"].append(f"💡 {len(reminders['context'])}条智能提示")
    except:
        pass
    
    # 添加时间建议
    hour = datetime.now().hour
    if 6 <= hour < 9:
        data["time_tip"] = "☕ 早上好！适合制定计划"
    elif 9 <= hour < 12:
        data["time_tip"] = "🧠 上午黄金时间，适合专注工作"
    elif 12 <= hour < 14:
        data["time_tip"] = "🍜 午休时间，适当休息"
    elif 14 <= hour < 17:
        data["time_tip"] = "📧 下午适合沟通协调"
    elif 17 <= hour < 19:
        data["time_tip"] = "📋 傍晚适合整理收工"
    elif 19 <= hour < 22:
        data["time_tip"] = "🌙 晚上了，注意休息"
    else:
        data["time_tip"] = "🌃 夜深了，早点休息"
    
    return data


def calculate_days(timestamp: str) -> int:
    """计算天数"""
    if not timestamp:
        return 0
    try:
        created = datetime.fromisoformat(timestamp)
        return (datetime.now() - created).days
    except:
        return 0


def format_dashboard(data: Dict) -> str:
    """格式化仪表盘"""
    lines = []
    
    # 顶部边框
    lines.append("╔" + "═" * 50 + "╗")
    lines.append("║" + " 🧠 AutoMemory Dashboard ".center(50) + "║")
    lines.append("║" + f" 📅 {data['date']} ".center(50) + "║")
    lines.append("╠" + "═" * 50 + "╣")
    
    # 统计信息
    stats = data.get("stats", {})
    lines.append("║" + " 📊 记忆统计 ".ljust(50) + "║")
    lines.append("║" + f"   总记忆: {stats.get('total', 0)} 条".ljust(50) + "║")
    lines.append("║" + f"   今日: {stats.get('today', 0)} 条 | 本周: {stats.get('week', 0)} 条".ljust(50) + "║")
    lines.append("╠" + "═" * 50 + "╣")
    
    # 待办任务
    lines.append("║" + " 🎯 待办任务 ".ljust(50) + "║")
    pending = data.get("pending_tasks", [])
    if pending:
        for task in pending[:5]:
            days = task.get("days", 0)
            days_str = f"({days}天前)" if days > 0 else ""
            text = task.get("text", "")[:35]
            lines.append("║" + f"   □ {text} {days_str}".ljust(50) + "║")
    else:
        lines.append("║" + "   ✅ 暂无待办任务".ljust(50) + "║")
    lines.append("╠" + "═" * 50 + "╣")
    
    # 逾期提醒
    overdue = data.get("overdue_tasks", 0)
    lines.append("║" + " ⚠️ 逾期提醒 ".ljust(50) + "║")
    if overdue > 0:
        lines.append("║" + f"   🚨 有 {overdue} 个任务已逾期！".ljust(50) + "║")
    else:
        lines.append("║" + "   ✅ 没有逾期任务，继续保持！".ljust(50) + "║")
    lines.append("╠" + "═" * 50 + "╣")
    
    # 时间建议
    time_tip = data.get("time_tip", "")
    lines.append("║" + f" {time_tip} ".ljust(50) + "║")
    
    # 智能提示
    tips = data.get("tips", [])
    if tips:
        lines.append("╠" + "═" * 50 + "╣")
        lines.append("║" + " 💡 智能提示 ".ljust(50) + "║")
        for tip in tips[:2]:
            lines.append("║" + f"   {tip}".ljust(50) + "║")
    
    # 底部
    lines.append("╠" + "═" * 50 + "╣")
    lines.append("║" + " 🚀 快捷命令 ".ljust(50) + "║")
    lines.append("║" + "   automemory briefing  - 生成简报".ljust(50) + "║")
    lines.append("║" + "   automemory status   - 查看状态".ljust(50) + "║")
    lines.append("╚" + "═" * 50 + "╝")
    
    return "\n".join(lines)


def main():
    """主函数"""
    print()
    data = get_dashboard_data()
    print(format_dashboard(data))
    print()


if __name__ == "__main__":
    main()