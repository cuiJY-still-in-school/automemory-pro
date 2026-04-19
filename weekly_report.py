#!/usr/bin/env python3
"""
AutoMemory Pro - 周报生成器
Weekly Report - 自动生成周报

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


def get_week_dates() -> tuple:
    """获取本周日期范围"""
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def load_week_memories() -> list:
    """加载本周记忆"""
    week_start, week_end = get_week_dates()
    memories = []
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        ts = datetime.fromisoformat(m.get('timestamp', ''))
                        if week_start <= ts <= week_end:
                            memories.append(m)
                    except:
                        continue
        except:
            continue
    
    return memories


def analyze_week(memories: list) -> dict:
    """分析本周数据"""
    analysis = {
        "total_actions": len(memories),
        "by_day": defaultdict(int),
        "by_tool": defaultdict(int),
        "by_category": defaultdict(int),
        "success_count": 0,
        "error_count": 0,
        "errors": [],
        "tools_used": set(),
        "key Accomplishments": [],
        "projects": defaultdict(int)
    }
    
    for m in memories:
        # 按天统计
        day = m.get('timestamp', '')[:10]
        analysis["by_day"][day] += 1
        
        # 按工具统计
        tool = m.get('tool', 'unknown')
        analysis["by_tool"][tool] += 1
        analysis["tools_used"].add(tool)
        
        # 按类别统计
        cat = m.get('category', 'unknown')
        analysis["by_category"][cat] += 1
        
        # 成功/失败
        if m.get('success', True):
            analysis["success_count"] += 1
        else:
            analysis["error_count"] += 1
            errors = m.get('errors', [])
            if errors:
                analysis["errors"].append({
                    "time": m.get('timestamp', '')[:16],
                    "tool": tool,
                    "error": errors[0][:100]
                })
        
        # 提取关键成就
        summary = m.get('summary', '')
        if any(kw in summary for kw in ['完成', '创建', '上线', '成功', '突破']):
            analysis["key Accomplishments"].append(summary[:60])
    
    return analysis


def format_week_report(analysis: dict) -> str:
    """格式化周报"""
    week_start, week_end = get_week_dates()
    week_num = week_start.isocalendar()[1]
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 周报 - 第{week_num}周 ({week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')})")
    lines.append("=" * 60)
    
    # 总览
    lines.append("\n📈 本周总览")
    lines.append("-" * 40)
    lines.append(f"  总操作: {analysis['total_actions']}次")
    lines.append(f"  成功: {analysis['success_count']}次")
    lines.append(f"  失败: {analysis['error_count']}次")
    
    if analysis['total_actions'] > 0:
        rate = analysis['success_count'] / analysis['total_actions'] * 100
        lines.append(f"  成功率: {rate:.1f}%")
    
    # 每日活动
    lines.append("\n📅 每日活动")
    lines.append("-" * 40)
    for day, count in sorted(analysis["by_day"].items()):
        bar = "█" * min(count // 2, 20)
        lines.append(f"  {day[-5:]}: {bar} {count}次")
    
    # 工具使用
    lines.append("\n🔧 工具使用排行")
    lines.append("-" * 40)
    tool_icons = {
        'write': '📝', 'edit': '✏️', 'exec': '⚙️',
        'read': '📖', 'browser': '🌐', 'search': '🔍'
    }
    for tool, count in sorted(analysis["by_tool"].items(), key=lambda x: -x[1])[:5]:
        icon = tool_icons.get(tool, '🔧')
        lines.append(f"  {icon} {tool}: {count}次")
    
    # 关键成就
    if analysis["key Accomplishments"]:
        lines.append("\n🎯 关键成就")
        lines.append("-" * 40)
        seen = set()
        for ach in analysis["key Accomplishments"][:5]:
            if ach not in seen:
                seen.add(ach)
                lines.append(f"  ✅ {ach}")
    
    # 错误统计
    if analysis["errors"]:
        lines.append("\n🐛 本周错误")
        lines.append("-" * 40)
        for err in analysis["errors"][:3]:
            lines.append(f"  ❌ [{err['time']}] {err['tool']}")
            lines.append(f"     {err['error']}")
    
    # 下周建议
    lines.append("\n💡 下周建议")
    lines.append("-" * 40)
    
    if analysis['total_actions'] < 20:
        lines.append("  📌 本周活动较少，建议增加工作量")
    elif analysis['error_count'] > 5:
        lines.append("  📌 错误较多，建议提高代码质量")
    else:
        lines.append("  📌 保持当前节奏，继续前进！")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def main():
    """主函数"""
    print()
    
    memories = load_week_memories()
    
    if not memories:
        print("📭 本周暂无数据")
        return
    
    analysis = analyze_week(memories)
    report = format_week_report(analysis)
    print(report)
    
    # 保存周报
    week_start, _ = get_week_dates()
    week_str = week_start.strftime("%Y-W%W")
    report_file = MEMORY_DIR / "reports" / f"week_{week_str}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 周报已保存: {report_file}")


if __name__ == "__main__":
    main()
