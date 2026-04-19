#!/usr/bin/env python3
"""
AutoMemory Pro - 快速统计
Quick Stats - 快速查看关键指标

用法:
    qstat               # 快速统计
    qstat --json        # JSON格式输出

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
sys.path.insert(0, str(PLUGIN_DIR))


def get_quick_stats() -> dict:
    """获取快速统计"""
    stats = {
        "total": 0,
        "today": 0,
        "week": 0,
        "success_rate": 0,
        "top_tools": [],
        "active_days": set(),
        "errors_today": 0
    }
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_ago = now - timedelta(days=7)
    
    tool_counts = defaultdict(int)
    success = 0
    errors = 0
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl")):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        stats["total"] += 1
                        
                        ts_str = m.get('timestamp', '')
                        ts = datetime.fromisoformat(ts_str)
                        
                        # 今天
                        if ts_str.startswith(today_str):
                            stats["today"] += 1
                            if not m.get('success', True):
                                stats["errors_today"] += 1
                        
                        # 本周
                        if ts >= week_ago:
                            stats["week"] += 1
                        
                        # 活跃天数
                        stats["active_days"].add(ts_str[:10])
                        
                        # 工具统计
                        tool = m.get('tool', 'unknown')
                        tool_counts[tool] += 1
                        
                        # 成功率
                        if m.get('success', True):
                            success += 1
                        else:
                            errors += 1
                    
                    except:
                        continue
        except:
            continue
    
    # 计算成功率
    if success + errors > 0:
        stats["success_rate"] = success / (success + errors) * 100
    
    # Top工具
    stats["top_tools"] = sorted(tool_counts.items(), key=lambda x: -x[1])[:5]
    
    return stats


def print_stats_json(stats: dict):
    """JSON格式输出"""
    # set转list
    data = {
        **stats,
        "active_days": len(stats["active_days"]),
        "timestamp": datetime.now().isoformat()
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_stats_text(stats: dict):
    """文本格式输出"""
    # 进度条
    def bar(count, max_count, width=20):
        if max_count == 0:
            return "░" * width
        filled = min(int(count / max_count * width), width)
        return "█" * filled + "░" * (width - filled)
    
    print()
    print(f"📊 AutoMemory 快速统计")
    print("=" * 40)
    print(f"  总记忆:   {stats['total']}")
    print(f"  今日:    {stats['today']} {bar(stats['today'], max(stats['total'], 1), 10)}")
    print(f"  本周:    {stats['week']}")
    print(f"  活跃天数: {len(stats['active_days'])}")
    print()
    print(f"  成功率:  {stats['success_rate']:.1f}%")
    print(f"  今日错误: {stats['errors_today']}")
    print()
    print("🔧 Top工具:")
    for tool, count in stats["top_tools"]:
        print(f"  {tool:12} {count:4}")
    print()


def main():
    """主函数"""
    args = sys.argv[1:]
    
    stats = get_quick_stats()
    
    if "--json" in args:
        print_stats_json(stats)
    else:
        print_stats_text(stats)


if __name__ == "__main__":
    main()
