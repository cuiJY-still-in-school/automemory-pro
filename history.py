#!/usr/bin/env python3
"""
AutoMemory Pro - 会话历史查看器
Session History Viewer - 查看AI的工作历史

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
sys.path.insert(0, str(PLUGIN_DIR))


def load_memories(days: int = 7, limit: int = 50) -> list:
    """加载最近记忆"""
    memories = []
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        ts = datetime.fromisoformat(m.get('timestamp', ''))
                        if ts >= cutoff:
                            memories.append(m)
                            if len(memories) >= limit:
                                break
                    except:
                        continue
        except:
            continue
    
    return memories


def group_by_date(memories: list) -> dict:
    """按日期分组"""
    groups = {}
    for m in memories:
        date = m.get('timestamp', '')[:10]
        if date not in groups:
            groups[date] = []
        groups[date].append(m)
    return groups


def format_tool_name(tool: str) -> str:
    """格式化工具名"""
    icons = {
        'write': '📝',
        'edit': '✏️',
        'exec': '⚙️',
        'browser': '🌐',
        'read': '📖',
        'search': '🔍',
        'message': '💬',
        'file': '📄',
        'folder': '📁',
        'default': '🔧'
    }
    return icons.get(tool, icons['default'])


def show_timeline(memories: list, limit: int = 30):
    """显示时间线"""
    if not memories:
        print("📭 暂无历史记录")
        return
    
    print(f"📜 最近活动时间线 (共{len(memories)}条)")
    print("=" * 60)
    
    groups = group_by_date(memories)
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for date in sorted(groups.keys(), reverse=True):
        if date == today:
            date_str = "📅 今天"
        elif date == yesterday:
            date_str = "📅 昨天"
        else:
            date_str = f"📅 {date}"
        
        print(f"\n{date_str}")
        print("-" * 50)
        
        for m in groups[date][:limit // len(groups)]:
            tool = m.get('tool', '?')
            icon = format_tool_name(tool)
            time = m.get('timestamp', '')[11:16]
            summary = m.get('summary', '')[:45]
            success = m.get('success', True)
            
            status = "✅" if success else "❌"
            print(f"  {time} {icon} {status} {summary}")


def show_stats(memories: list):
    """显示统计"""
    if not memories:
        print("📊 暂无数据")
        return
    
    print("\n📊 活动统计")
    print("=" * 60)
    
    # 按工具统计
    by_tool = {}
    by_category = {}
    success_count = 0
    error_count = 0
    
    for m in memories:
        tool = m.get('tool', 'unknown')
        by_tool[tool] = by_tool.get(tool, 0) + 1
        
        cat = m.get('category', 'unknown')
        by_category[cat] = by_category.get(cat, 0) + 1
        
        if m.get('success', True):
            success_count += 1
        else:
            error_count += 1
    
    print("\n🔧 工具使用排行:")
    for tool, count in sorted(by_tool.items(), key=lambda x: -x[1])[:5]:
        icon = format_tool_name(tool)
        print(f"  {icon} {tool}: {count}次")
    
    print("\n🏷️ 操作类型:")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1])[:5]:
        print(f"  • {cat}: {count}次")
    
    total = success_count + error_count
    success_rate = success_count / total * 100 if total > 0 else 0
    print(f"\n📈 成功率: {success_rate:.1f}% ({success_count}成功 / {error_count}失败)")


def show_errors(memories: list, limit: int = 10):
    """显示错误"""
    errors = [m for m in memories if not m.get('success', True)]
    
    if not errors:
        print("\n✅ 没有记录到错误，太棒了！")
        return
    
    print(f"\n🐛 最近错误 (共{len(errors)}个)")
    print("=" * 60)
    
    for m in errors[:limit]:
        tool = m.get('tool', '?')
        icon = format_tool_name(tool)
        time = m.get('timestamp', '')[:19]
        summary = m.get('summary', '未知错误')
        errors_list = m.get('errors', [])
        
        print(f"\n  🕐 {time}")
        print(f"  {icon} {summary}")
        if errors_list:
            for e in errors_list[:2]:
                print(f"     └ {e[:60]}")


def show_projects(memories: list):
    """显示项目活动"""
    # 简单按路径分组
    paths = {}
    for m in memories:
        summary = m.get('summary', '')
        # 尝试提取路径
        import re
        path_match = re.search(r'[/~/\w+]+\.\w+', summary)
        if path_match:
            path = path_match.group()
            # 提取项目名
            parts = path.split('/')
            for part in parts[-3:]:
                if len(part) > 2 and '.' not in part:
                    paths[part] = paths.get(part, 0) + 1
                    break
    
    if not paths:
        return
    
    print(f"\n📂 项目活动")
    print("=" * 60)
    for proj, count in sorted(paths.items(), key=lambda x: -x[1])[:5]:
        print(f"  📁 {proj}: {count}次操作")


def main():
    """主函数"""
    days = 7
    limit = 50
    show_errors_flag = False
    
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("""
📜 AutoMemory Session History

用法: history [选项]

选项:
  -d <天数>   查看最近天数 (默认: 7)
  -n <数量>   显示数量 (默认: 50)
  -e         只显示错误
  -s         只显示统计
  -h         显示帮助

示例:
  history          # 最近7天
  history -d 30   # 最近30天
  history -e       # 只看错误
  history -s       # 只看统计
""")
        return
    
    if "-d" in args:
        idx = args.index("-d")
        days = int(args[idx + 1]) if idx + 1 < len(args) else 7
    
    if "-n" in args:
        idx = args.index("-n")
        limit = int(args[idx + 1]) if idx + 1 < len(args) else 50
    
    show_errors_flag = "-e" in args
    show_stats_only = "-s" in args
    
    print()
    print(f"📥 加载最近 {days} 天的数据...")
    memories = load_memories(days=days, limit=limit)
    print(f"📊 已加载 {len(memories)} 条记录")
    
    if show_stats_only:
        show_stats(memories)
    elif show_errors_flag:
        show_errors(memories)
    else:
        show_timeline(memories, limit=limit)
        show_stats(memories)
        show_errors(memories)
        show_projects(memories)
    
    print()


if __name__ == "__main__":
    main()
