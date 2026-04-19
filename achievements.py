#!/usr/bin/env python3
"""
AutoMemory Pro - 成就系统
Achievements - AI工作的成就和里程碑

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
ACHIEVEMENTS_FILE = MEMORY_DIR / "achievements.json"
sys.path.insert(0, str(PLUGIN_DIR))


# 成就定义
ACHIEVEMENTS = {
    # 数量成就
    "first_memory": {
        "name": "🌱 初识",
        "desc": "记录第一条记忆",
        "icon": "🌱",
        "condition": lambda stats: stats.get("total_memories", 0) >= 1
    },
    "ten_memories": {
        "name": "📝 小试牛刀",
        "desc": "记录10条记忆",
        "icon": "📝",
        "condition": lambda stats: stats.get("total_memories", 0) >= 10
    },
    "hundred_memories": {
        "name": "💯 百分成就",
        "desc": "记录100条记忆",
        "icon": "💯",
        "condition": lambda stats: stats.get("total_memories", 0) >= 100
    },
    
    # 连续活跃
    "first_day": {
        "name": "📅 第一天",
        "desc": "第一次使用",
        "icon": "📅",
        "condition": lambda stats: stats.get("active_days", 0) >= 1
    },
    "week_streak": {
        "name": "📆 周周不休",
        "desc": "连续活跃7天",
        "icon": "📆",
        "condition": lambda stats: stats.get("streak_days", 0) >= 7
    },
    "month_streak": {
        "name": "🗓️ 月月坚持",
        "desc": "连续活跃30天",
        "icon": "🗓️",
        "condition": lambda stats: stats.get("streak_days", 0) >= 30
    },
    
    # 任务成就
    "first_task": {
        "name": "☑️ 任务起点",
        "desc": "创建第一个任务",
        "icon": "☑️",
        "condition": lambda stats: stats.get("total_tasks", 0) >= 1
    },
    "ten_tasks": {
        "name": "✅ 十全十美",
        "desc": "完成10个任务",
        "icon": "✅",
        "condition": lambda stats: stats.get("completed_tasks", 0) >= 10
    },
    
    # 效率成就
    "error_free_day": {
        "name": "✨ 完美一天",
        "desc": "一天内无错误",
        "icon": "✨",
        "condition": lambda stats: stats.get("today_errors", 0) == 0 and stats.get("today_memories", 0) > 5
    },
    "high_productivity": {
        "name": "🚀 高效日",
        "desc": "一天完成20+操作",
        "icon": "🚀",
        "condition": lambda stats: stats.get("today_memories", 0) >= 20
    },
    
    # 里程碑
    "weekend_warrior": {
        "name": "⚔️ 周末战士",
        "desc": "周末也工作",
        "icon": "⚔️",
        "condition": lambda stats: stats.get("is_weekend", False)
    },
    "night_owl": {
        "name": "🦉 猫头鹰",
        "desc": "在23点后工作",
        "icon": "🦉",
        "condition": lambda stats: stats.get("is_late_night", False)
    },
    
    # 工具成就
    "all_tools": {
        "name": "🛠️ 全能工具",
        "desc": "使用过所有主要工具",
        "icon": "🛠️",
        "condition": lambda stats: len(stats.get("tools_used", [])) >= 5
    },
}


def load_achievements() -> dict:
    """加载已获得的成就"""
    if ACHIEVEMENTS_FILE.exists():
        try:
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"achievements": [], "stats": {}}


def save_achievements(data: dict):
    """保存成就数据"""
    ACHIEVEMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_stats() -> dict:
    """获取统计数据"""
    stats = {
        "total_memories": 0,
        "today_memories": 0,
        "active_days": 0,
        "streak_days": 1,
        "total_tasks": 0,
        "completed_tasks": 0,
        "today_errors": 0,
        "tools_used": set(),
        "is_weekend": datetime.now().weekday() >= 5,
        "is_late_night": datetime.now().hour >= 23
    }
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    dates_seen = set()
    
    for mem_file in MEMORY_DIR.glob("memories_*.jsonl"):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        stats["total_memories"] += 1
                        
                        # 今天
                        if today_str in m.get("timestamp", ""):
                            stats["today_memories"] += 1
                            if not m.get("success", True):
                                stats["today_errors"] += 1
                        
                        # 工具
                        tool = m.get("tool")
                        if tool:
                            stats["tools_used"].add(tool)
                        
                        # 日期
                        date = m.get("timestamp", "")[:10]
                        if date:
                            dates_seen.add(date)
                        
                    except:
                        continue
        except:
            continue
    
    # 加载任务统计
    tasks_file = MEMORY_DIR / "tasks.json"
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                stats["total_tasks"] = len(tasks_data.get("tasks", []))
                stats["completed_tasks"] = sum(
                    1 for t in tasks_data.get("tasks", [])
                    if t.get("status") == "completed"
                )
        except:
            pass
    
    # 计算活跃天数
    stats["active_days"] = len(dates_seen)
    
    # 计算连续天数
    dates = sorted(dates_seen, reverse=True)
    streak = 0
    check_date = now.date()
    for d in dates:
        d_obj = datetime.fromisoformat(d).date()
        if d_obj == check_date or d_obj == check_date - timedelta(days=1):
            streak += 1
            check_date = d_obj
        else:
            break
    stats["streak_days"] = streak
    
    # set转list
    stats["tools_used"] = list(stats["tools_used"])
    
    return stats


def check_achievements() -> list:
    """检查成就"""
    data = load_achievements()
    earned_ids = set(data.get("achievements", []))
    stats = get_stats()
    
    new_achievements = []
    
    for aid, ach in ACHIEVEMENTS.items():
        if aid not in earned_ids:
            try:
                if ach["condition"](stats):
                    earned_ids.add(aid)
                    new_achievements.append({
                        "id": aid,
                        "name": ach["name"],
                        "desc": ach["desc"],
                        "icon": ach["icon"],
                        "earned_at": datetime.now().isoformat()
                    })
            except:
                pass
    
    # 保存新成就
    if new_achievements:
        data["achievements"].extend([a["id"] for a in new_achievements])
        data["stats"] = stats
        save_achievements(data)
    
    return new_achievements


def show_all_achievements():
    """显示所有成就"""
    data = load_achievements()
    earned_ids = set(data.get("achievements", []))
    stats = data.get("stats", get_stats())
    
    print("\n🏆 AutoMemory 成就墙")
    print("=" * 50)
    
    # 统计
    print(f"\n📊 当前统计:")
    print(f"   记忆总数: {stats.get('total_memories', 0)}")
    print(f"   今日操作: {stats.get('today_memories', 0)}")
    print(f"   活跃天数: {stats.get('active_days', 0)}")
    print(f"   连续活跃: {stats.get('streak_days', 0)}天")
    print(f"   完成任务: {stats.get('completed_tasks', 0)}")
    
    print(f"\n🎖️ 已解锁 ({len(earned_ids)}/{len(ACHIEVEMENTS)}):")
    
    earned_list = []
    locked_list = []
    
    for aid, ach in ACHIEVEMENTS.items():
        if aid in earned_ids:
            earned_list.append(ach)
        else:
            locked_list.append(ach)
    
    for ach in earned_list:
        print(f"   {ach['icon']} {ach['name']} - {ach['desc']}")
    
    if locked_list:
        print(f"\n🔒 未解锁:")
        for ach in locked_list[:5]:
            print(f"   {ach['icon']} {ach['name']} - {ach['desc']}")
        if len(locked_list) > 5:
            print(f"   ...还有{len(locked_list)-5}个")


def main():
    """主函数"""
    # 检查新成就
    new_achs = check_achievements()
    
    if new_achs:
        print("\n🎉🎉🎉 新成就解锁！🎉🎉🎉")
        for ach in new_achs:
            print(f"\n  {ach['icon']} {ach['name']}")
            print(f"     {ach['desc']}")
    
    # 显示成就墙
    show_all_achievements()


if __name__ == "__main__":
    main()
