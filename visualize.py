#!/usr/bin/env python3
"""
AutoMemory 可视化工具
展示记忆的使用效果和价值
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

print("🎨 AutoMemory 可视化报告")
print("=" * 70)

# 读取记忆文件
memory_dir = Path.home() / ".openclaw" / "automemory"
if not memory_dir.exists():
    print("❌ 记忆目录不存在")
    exit(1)

# 收集所有记忆
all_memories = []
for memory_file in sorted(memory_dir.glob("memories_*.jsonl")):
    with open(memory_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                memory = json.loads(line.strip())
                all_memories.append(memory)
            except:
                pass

if not all_memories:
    print("❌ 没有找到记忆")
    exit(1)

print(f"\n📊 总计记忆: {len(all_memories)} 条\n")

# 1. 时间分布
print("📅 记忆时间分布:")
print("-" * 50)
dates = Counter()
for m in all_memories:
    ts = m.get('timestamp', '')
    if ts:
        date = ts[:10]
        dates[date] += 1

for date, count in sorted(dates.items())[-7:]:  # 最近7天
    bar = "█" * min(count, 30)
    print(f"  {date}: {bar} {count}条")

# 2. 工具使用分布
print("\n🔧 工具使用分布:")
print("-" * 50)
tools = Counter(m.get('tool', 'unknown') for m in all_memories)
for tool, count in tools.most_common(10):
    bar = "█" * min(count, 20)
    pct = count / len(all_memories) * 100
    print(f"  {tool:12}: {bar} {count}条 ({pct:.1f}%)")

# 3. 分类分布
print("\n📂 分类分布:")
print("-" * 50)
categories = Counter(m.get('category', 'unknown') for m in all_memories)
emoji_map = {
    'actions': '🎯',
    'discoveries': '💡',
    'errors': '❌',
    'decisions': '🤔',
    'preferences': '❤️',
    'unknown': '📝'
}
for cat, count in categories.most_common():
    emoji = emoji_map.get(cat, '📝')
    pct = count / len(all_memories) * 100
    print(f"  {emoji} {cat:12}: {count:3}条 ({pct:5.1f}%)")

# 4. 重要性分布
print("\n⭐ 重要性分布:")
print("-" * 50)
importance_ranges = {
    '0.0-0.2': 0,
    '0.2-0.4': 0,
    '0.4-0.6': 0,
    '0.6-0.8': 0,
    '0.8-1.0': 0
}
for m in all_memories:
    imp = m.get('importance', 0)
    if imp < 0.2:
        importance_ranges['0.0-0.2'] += 1
    elif imp < 0.4:
        importance_ranges['0.2-0.4'] += 1
    elif imp < 0.6:
        importance_ranges['0.4-0.6'] += 1
    elif imp < 0.8:
        importance_ranges['0.6-0.8'] += 1
    else:
        importance_ranges['0.8-1.0'] += 1

for range_name, count in importance_ranges.items():
    bar = "█" * min(count, 25)
    print(f"  {range_name}: {bar} {count}条")

# 5. 高价值记忆
print("\n💎 高价值记忆 (重要性≥0.8):")
print("-" * 50)
high_value = [m for m in all_memories if m.get('importance', 0) >= 0.8]
for i, m in enumerate(sorted(high_value, key=lambda x: x.get('importance', 0), reverse=True)[:5], 1):
    tool = m.get('tool', 'unknown')
    imp = m.get('importance', 0)
    summary = m.get('summary', '')[:40]
    print(f"  {i}. [{imp:.2f}] {tool:10} {summary}...")

# 6. 错误记忆
print("\n⚠️  错误记录:")
print("-" * 50)
errors = [m for m in all_memories if m.get('category') == 'errors' or not m.get('success', True)]
if errors:
    for m in errors[-5:]:  # 最近5个错误
        tool = m.get('tool', 'unknown')
        ts = m.get('timestamp', '')[:16]
        print(f"  {ts} {tool}: {m.get('summary', 'Error')[:40]}...")
else:
    print("  ✅ 没有错误记录")

# 7. 会话统计
print("\n👥 会话统计:")
print("-" * 50)
sessions = Counter(m.get('session_id', 'unknown') for m in all_memories)
print(f"  总会话数: {len(sessions)}")
print(f"  平均每会话记忆: {len(all_memories) / len(sessions):.1f}条")

# 8. 存储统计
print("\n💾 存储统计:")
print("-" * 50)
total_size = sum(f.stat().st_size for f in memory_dir.glob("memories_*.jsonl"))
print(f"  记忆文件数: {len(list(memory_dir.glob('memories_*.jsonl')))}")
print(f"  总存储大小: {total_size / 1024:.1f} KB")
print(f"  平均每条约: {total_size / len(all_memories):.0f} 字节")

# 9. 价值评估
print("\n💰 价值评估:")
print("-" * 50)

# 估算节省的时间
repeated_queries = len([m for m in all_memories if m.get('tool') in ['read', 'exec']])
estimated_time_saved = repeated_queries * 0.5  # 每次查询节省0.5分钟

print(f"  重复操作记录: {repeated_queries} 次")
print(f"  估算节省时间: {estimated_time_saved:.1f} 分钟")
print(f"  避免重复错误: {len(errors)} 次")

# 10. 建议
print("\n💡 智能建议:")
print("-" * 50)

if importance_ranges['0.0-0.2'] > len(all_memories) * 0.3:
    print("  ⚠️  低重要性记忆占比高，建议调高 importance_threshold")

if len(errors) > 5:
    print(f"  ⚠️  发现 {len(errors)} 个错误，建议回顾并总结")

if tools.get('write', 0) > tools.get('read', 0) * 2:
    print("  💡 写入操作远多于读取，建议定期整理文档")

if categories.get('actions', 0) > len(all_memories) * 0.7:
    print("  💡 actions分类占主导，工作状态良好")

print("\n" + "=" * 70)
print("✨ AutoMemory 正在帮助你建立个人知识库！")
print("=" * 70)