#!/usr/bin/env python3
"""
AutoMemory Pro - 内存清理
Cleanup - 清理重复、过期、无用的记忆

用法:
    cleanup --dry-run        # 预览要清理的内容
    cleanup --execute       # 执行清理
    cleanup --duplicates    # 只清理重复
    cleanup --old <天数>    # 清理旧记忆

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


def find_duplicates() -> list:
    """查找重复记忆"""
    seen = {}
    duplicates = []
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl")):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        # 用工具+摘要作为key
                        key = f"{m.get('tool', '')}:{m.get('summary', '')}"
                        if key in seen:
                            duplicates.append({
                                "file": mem_file.name,
                                "timestamp": m.get('timestamp', ''),
                                "id": m.get('id', ''),
                                "key": key,
                                "summary": m.get('summary', '')[:50]
                            })
                        else:
                            seen[key] = m
                    except:
                        continue
        except:
            continue
    
    return duplicates


def find_old_memories(days: int = 30) -> list:
    """查找旧记忆"""
    cutoff = datetime.now() - timedelta(days=days)
    old_memories = []
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl")):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        ts = datetime.fromisoformat(m.get('timestamp', ''))
                        if ts < cutoff:
                            old_memories.append({
                                "file": mem_file.name,
                                "timestamp": m.get('timestamp', ''),
                                "id": m.get('id', ''),
                                "tool": m.get('tool', ''),
                                "summary": m.get('summary', '')[:50]
                            })
                    except:
                        continue
        except:
            continue
    
    return old_memories


def find_empty_memories() -> list:
    """查找空记忆"""
    empty = []
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl")):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        summary = m.get('summary', '').strip()
                        errors = m.get('errors', [])
                        # 没有摘要、没有错误、没有实质内容的记忆
                        if not summary and not errors and m.get('success', True):
                            empty.append({
                                "file": mem_file.name,
                                "timestamp": m.get('timestamp', ''),
                                "id": m.get('id', ''),
                                "tool": m.get('tool', '')
                            })
                    except:
                        continue
        except:
            continue
    
    return empty


def remove_memories(memories: list) -> int:
    """删除指定的记忆"""
    removed = 0
    removed_files = defaultdict(list)
    
    for mem in memories:
        file_path = MEMORY_DIR / mem["file"]
        if not file_path.exists():
            continue
        
        # 读取文件，排除要删除的行
        remaining = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    m = json.loads(line.strip())
                    if m.get('id', '') != mem.get('id', ''):
                        remaining.append(line)
                except:
                    remaining.append(line)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        removed_files[mem["file"]].append(mem["id"])
        removed += 1
    
    # 报告
    for fname, ids in removed_files.items():
        print(f"  ✅ {fname}: 删除了 {len(ids)} 条")
    
    return removed


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or "-h" in args or "--help" in args:
        print("""
🧹 AutoMemory 内存清理

用法:
    cleanup --dry-run        # 预览要清理的内容
    cleanup --execute        # 执行清理（需要确认）
    cleanup --duplicates     # 只查重复
    cleanup --old <天数>     # 查看旧记忆（默认30天）
    cleanup --empty          # 查看空记忆

示例:
    cleanup --dry-run       # 预览所有问题
    cleanup --execute        # 确认后执行清理
    cleanup --duplicates --execute  # 只清理重复
    cleanup --old 7 --execute  # 清理7天前的记忆
""")
        return
    
    dry_run = "--dry-run" in args
    execute = "--execute" in args
    duplicates_only = "--duplicates" in args
    empty_only = "--empty" in args
    
    # 解析天数
    days = 30
    if "--old" in args:
        idx = args.index("--old")
        days = int(args[idx + 1]) if idx + 1 < len(args) else 30
    
    all_to_clean = []
    
    print("\n🧹 AutoMemory 内存清理")
    print("=" * 50)
    
    if duplicates_only or (not empty_only and "--old" not in args):
        # 查找重复
        print("\n📦 查找重复记忆...")
        dups = find_duplicates()
        if dups:
            print(f"   找到 {len(dups)} 条重复记忆")
            for d in dups[:10]:
                print(f"   ❌ {d['timestamp'][:16]} {d['summary']}")
            if len(dups) > 10:
                print(f"   ... 还有 {len(dups) - 10} 条")
            all_to_clean.extend(dups)
        else:
            print("   ✅ 没有重复记忆")
    
    if not duplicates_only and "--old" not in args:
        # 查找空记忆
        print("\n📭 查找空记忆...")
        empty = find_empty_memories()
        if empty:
            print(f"   找到 {len(empty)} 条空记忆")
            for e in empty[:5]:
                print(f"   ❌ {e['timestamp'][:16]} [{e['tool']}]")
            if len(empty) > 5:
                print(f"   ... 还有 {len(empty) - 5} 条")
            all_to_clean.extend(empty)
        else:
            print("   ✅ 没有空记忆")
    
    if "--old" in args or duplicates_only:
        # 查找旧记忆
        print(f"\n📅 查找 {days} 天前的记忆...")
        old = find_old_memories(days)
        if old:
            print(f"   找到 {len(old)} 条旧记忆")
            for o in old[:5]:
                print(f"   ❌ {o['timestamp'][:16]} {o['summary']}")
            if len(old) > 5:
                print(f"   ... 还有 {len(old) - 5} 条")
            all_to_clean.extend(old)
        else:
            print("   ✅ 没有旧记忆")
    
    # 执行清理
    if execute:
        if not all_to_clean:
            print("\n✅ 没有需要清理的记忆")
            return
        
        confirm = input(f"\n确认删除 {len(all_to_clean)} 条记忆？(y/N): ")
        if confirm.lower() == 'y':
            removed = remove_memories(all_to_clean)
            print(f"\n✅ 清理完成！释放了 {removed} 条记忆")
        else:
            print("\n❌ 取消清理")
    elif dry_run:
        if all_to_clean:
            print(f"\n🔍 预览模式: 建议清理 {len(all_to_clean)} 条记忆")
            print("   使用 --execute 确认执行")
        else:
            print("\n✅ 没有需要清理的内容")


if __name__ == "__main__":
    main()
