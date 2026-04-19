#!/usr/bin/env python3
"""
AutoMemory Pro - 标签系统
Tags - 记忆标签管理

用法:
    tags                    # 显示所有标签
    tags add <记忆ID> <标签>  # 添加标签
    tags remove <记忆ID> <标签> # 删除标签
    tags search <标签>      # 按标签搜索

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
TAGS_FILE = MEMORY_DIR / "tags.json"
sys.path.insert(0, str(PLUGIN_DIR))


def load_tags() -> dict:
    """加载标签"""
    if TAGS_FILE.exists():
        try:
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"memory_tags": {}, "tag_counts": defaultdict(int)}


def save_tags(tags: dict):
    """保存标签"""
    # 确保defaultdict能序列化
    data = {
        "memory_tags": tags.get("memory_tags", {}),
        "tag_counts": dict(tags.get("tag_counts", {}))
    }
    with open(TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_tag(memory_id: str, tag: str) -> bool:
    """添加标签"""
    tags = load_tags()
    
    if memory_id not in tags["memory_tags"]:
        tags["memory_tags"][memory_id] = []
    
    if tag not in tags["memory_tags"][memory_id]:
        tags["memory_tags"][memory_id].append(tag)
        tags["tag_counts"][tag] = tags["tag_counts"].get(tag, 0) + 1
        save_tags(tags)
        return True
    
    return False


def remove_tag(memory_id: str, tag: str) -> bool:
    """删除标签"""
    tags = load_tags()
    
    if memory_id in tags["memory_tags"] and tag in tags["memory_tags"][memory_id]:
        tags["memory_tags"][memory_id].remove(tag)
        tags["tag_counts"][tag] = max(0, tags["tag_counts"].get(tag, 1) - 1)
        save_tags(tags)
        return True
    
    return False


def show_all_tags():
    """显示所有标签"""
    tags = load_tags()
    
    if not tags["tag_counts"]:
        print("\n🏷️ 暂无标签")
        return
    
    print("\n🏷️ 标签列表")
    print("=" * 50)
    
    # 按使用次数排序
    sorted_tags = sorted(tags["tag_counts"].items(), key=lambda x: -x[1])
    
    for tag, count in sorted_tags:
        bar = "█" * min(count, 20)
        print(f"  {tag:15} {bar} ({count})")


def search_by_tag(tag: str, limit: int = 20):
    """按标签搜索记忆"""
    tags = load_tags()
    
    # 找到有这个标签的记忆
    memory_ids = [mid for mid, tlist in tags["memory_tags"].items() if tag in tlist]
    
    if not memory_ids:
        print(f"\n🔍 没有找到标签「{tag}」的记忆")
        return
    
    print(f"\n🔍 标签「{tag}」相关记忆 ({len(memory_ids)}条):")
    print("-" * 50)
    
    # 加载并显示这些记忆
    found = 0
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        mid = m.get('id', '')
                        if mid in memory_ids and found < limit:
                            time = m.get('timestamp', '')[:16]
                            tool = m.get('tool', '?')
                            success = "✅" if m.get('success', True) else "❌"
                            summary = m.get('summary', '无描述')[:50]
                            print(f"  {time} {success} [{tool}] {summary}")
                            found += 1
                    except:
                        continue
        except:
            continue
    
    if found >= limit:
        print(f"  ... 还有{len(memory_ids) - found}条")


def tag_memory_from_content(keyword: str, tag: str, dry_run: bool = True):
    """根据关键词自动给记忆打标签"""
    memories = []
    
    # 搜索包含关键词的记忆
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        text = f"{m.get('tool', '')} {m.get('summary', '')}".lower()
                        if keyword.lower() in text:
                            memories.append(m)
                    except:
                        continue
        except:
            continue
    
    if not memories:
        print(f"❌ 没有找到包含「{keyword}」的记忆")
        return
    
    if dry_run:
        print(f"\n🏷️ 将为 {len(memories)} 条记忆添加标签「{tag}」:")
        print("   (预览模式，使用 --apply 生效)")
        for m in memories[:5]:
            print(f"   - {m.get('timestamp', '')[:16]} {m.get('summary', '')[:40]}")
        if len(memories) > 5:
            print(f"   ... 还有{len(memories) - 5}条")
    else:
        tags = load_tags()
        for m in memories:
            mid = m.get('id', '')
            if mid not in tags["memory_tags"]:
                tags["memory_tags"][mid] = []
            if tag not in tags["memory_tags"][mid]:
                tags["memory_tags"][mid].append(tag)
                tags["tag_counts"][tag] = tags["tag_counts"].get(tag, 0) + 1
        
        save_tags(tags)
        print(f"✅ 已为 {len(memories)} 条记忆添加标签「{tag}」")


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] == "-h" or args[0] == "--help":
        print("""
🏷️ AutoMemory 标签系统

用法:
    tags                          # 显示所有标签
    tags add <记忆ID> <标签>       # 添加标签
    tags remove <记忆ID> <标签>    # 删除标签
    tags search <标签>             # 按标签搜索
    tags auto <关键词> <标签>      # 自动打标签
    tags auto <关键词> <标签> --apply  # 自动打标签(生效)

示例:
    tags                          # 查看所有标签
    tags add abc123 工作         # 添加标签
    tags search 工作              # 搜索工作相关记忆
    tags auto Fiverr 项目        # 预览Fiverr相关记忆
    tags auto Fiverr 项目 --apply # 生效
""")
        return
    
    if args[0] == "add":
        if len(args) < 3:
            print("❌ 请提供记忆ID和标签")
            return
        if add_tag(args[1], args[2]):
            print(f"✅ 已添加标签「{args[2]}」")
        else:
            print(f"⚠️ 标签「{args[2]}」已存在")
    
    elif args[0] == "remove":
        if len(args) < 3:
            print("❌ 请提供记忆ID和标签")
            return
        if remove_tag(args[1], args[2]):
            print(f"✅ 已删除标签「{args[2]}」")
        else:
            print(f"❌ 未找到标签「{args[2]}」")
    
    elif args[0] == "search":
        if len(args) < 2:
            print("❌ 请提供标签名")
            return
        search_by_tag(args[1])
    
    elif args[0] == "auto":
        if len(args) < 3:
            print("❌ 请提供关键词和标签名")
            return
        keyword = args[1]
        tag = args[2]
        apply = "--apply" in args
        tag_memory_from_content(keyword, tag, dry_run=not apply)
    
    else:
        show_all_tags()


if __name__ == "__main__":
    main()
