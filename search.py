#!/usr/bin/env python3
"""
AutoMemory Pro - 智能搜索
Smart Search - 用自然语言搜索记忆

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
sys.path.insert(0, str(PLUGIN_DIR))


def parse_query(query: str) -> dict:
    """解析查询"""
    result = {
        "keywords": [],
        "tool": None,
        "time": None,
        "category": None,
        "success": None
    }
    
    query_lower = query.lower()
    
    # 解析时间
    time_map = {
        "今天": 0,
        "昨天": 1,
        "前天": 2,
        "这周": 7,
        "上周": 14,
        "这个月": 30,
    }
    
    for word, days in time_map.items():
        if word in query:
            result["time"] = days
            break
    
    # 解析工具
    tool_map = {
        "写": "write",
        "编辑": "edit", 
        "执行": "exec",
        "命令": "exec",
        "读取": "read",
        "文件": "file",
        "网页": "web_fetch",
        "浏览器": "browser",
        "搜索": "search",
    }
    
    for word, tool in tool_map.items():
        if word in query:
            result["tool"] = tool
            break
    
    # 解析类别
    category_map = {
        "错误": "errors",
        "失败": "errors",
        "成功": "actions",
        "完成": "actions",
        "决定": "decisions",
        "发现": "discoveries",
        "灵感": "discoveries",
    }
    
    for word, cat in category_map.items():
        if word in query:
            result["category"] = cat
            break
    
    # 解析状态
    if "成功" in query:
        result["success"] = True
    elif "失败" in query or "错误" in query:
        result["success"] = False
    
    # 提取关键词（移除上面的词）
    keywords = query
    for word in list(time_map.keys()) + list(tool_map.keys()) + list(category_map.keys()) + ["成功", "失败"]:
        keywords = keywords.replace(word, "")
    
    # 清理
    keywords = re.sub(r'[^\w\s]', '', keywords).strip()
    if keywords:
        result["keywords"] = keywords.split()
    
    return result


def search_memories(query: str, limit: int = 20) -> list:
    """搜索记忆"""
    parsed = parse_query(query)
    
    memories = []
    now = datetime.now()
    
    # 时间过滤
    if parsed["time"]:
        cutoff = now - timedelta(days=parsed["time"])
    else:
        cutoff = now - timedelta(days=365)  # 默认1年
    
    # 加载所有记忆
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        ts = datetime.fromisoformat(m.get('timestamp', ''))
                        if ts >= cutoff:
                            memories.append(m)
                    except:
                        continue
        except:
            continue
    
    # 应用过滤
    results = []
    for m in memories:
        # 工具过滤
        if parsed["tool"] and m.get('tool') != parsed["tool"]:
            continue
        
        # 类别过滤
        if parsed["category"] and m.get('category') != parsed["category"]:
            continue
        
        # 成功状态过滤
        if parsed["success"] is not None:
            if m.get('success', True) != parsed["success"]:
                continue
        
        # 关键词过滤
        if parsed["keywords"]:
            text = f"{m.get('tool', '')} {m.get('summary', '')} {m.get('category', '')}"
            text_lower = text.lower()
            if all(kw.lower() in text_lower for kw in parsed["keywords"]):
                results.append(m)
        else:
            results.append(m)
        
        if len(results) >= limit:
            break
    
    # 按相关性排序（时间优先）
    results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return results


def format_result(m: dict, highlight: list = None) -> str:
    """格式化结果"""
    time = m.get('timestamp', '')[:16]
    tool = m.get('tool', '?')
    tool_icon = {
        'write': '📝', 'edit': '✏️', 'exec': '⚙️',
        'read': '📖', 'browser': '🌐', 'search': '🔍',
        'default': '🔧'
    }.get(tool, '🔧')
    
    success = "✅" if m.get('success', True) else "❌"
    summary = m.get('summary', '无描述')[:60]
    
    return f"{time} {tool_icon} {success} {summary}"


def show_results(results: list, query: str):
    """显示结果"""
    if not results:
        print(f"\n🔍 未找到与「{query}」相关的记忆")
        return
    
    print(f"\n🔍 找到 {len(results)} 条与「{query}」相关的结果:")
    print("=" * 60)
    
    for m in results:
        print(f"  {format_result(m)}")


def explain_query(query: str):
    """解释查询解析"""
    parsed = parse_query(query)
    
    print("\n🔧 查询解析:")
    print(f"  关键词: {parsed['keywords'] or '无'}")
    print(f"  工具: {parsed['tool'] or '不限'}")
    print(f"  时间: {parsed['time'] or '不限'}天内")
    print(f"  类别: {parsed['category'] or '不限'}")
    print(f"  状态: {'成功' if parsed['success'] == True else '失败' if parsed['success'] == False else '不限'}")


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or "-h" in args or "--help" in args:
        print("""
🔍 AutoMemory Smart Search

用法: search [选项] [关键词...]

示例:
  search Fiverr                    # 搜索Fiverr相关
  search 今天的命令                # 今天执行的命令
  search 错误                      # 所有错误
  search 成功的任务                # 成功的任务
  search -e "2024-01-01" Fiverr  # 指定日期后搜索
  search -x                       # 解释查询解析

提示:
  • 支持中文: "今天", "昨天", "这周"
  • 支持工具: "写", "编辑", "执行", "读取"
  • 支持状态: "成功", "失败"
""")
        return
    
    # 解析选项
    explain = False
    limit = 20
    
    if "-x" in args:
        explain = True
        args.remove("-x")
    
    if "-n" in args:
        idx = args.index("-n")
        limit = int(args[idx + 1])
        args.remove("-n")
        args.pop(idx)
    
    query = " ".join(args)
    
    if not query:
        print("❌ 请输入搜索关键词")
        return
    
    if explain:
        explain_query(query)
    
    results = search_memories(query, limit=limit)
    show_results(results, query)


if __name__ == "__main__":
    main()
