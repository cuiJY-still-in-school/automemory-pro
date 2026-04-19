#!/usr/bin/env python3
"""
AutoMemory Pro - 数据导出
Export - 导出记忆为各种格式

支持: JSON, Markdown, CSV, HTML

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from io import StringIO

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
sys.path.insert(0, str(PLUGIN_DIR))


def load_all_memories(days: int = None, limit: int = None) -> list:
    """加载记忆"""
    memories = []
    cutoff = None
    
    if days:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        if cutoff:
                            ts = datetime.fromisoformat(m.get('timestamp', ''))
                            if ts < cutoff:
                                continue
                        memories.append(m)
                        if limit and len(memories) >= limit:
                            break
                    except:
                        continue
        except:
            continue
    
    return memories[:limit] if limit else memories


def export_json(memories: list, output_file: Path = None) -> str:
    """导出为JSON"""
    data = {
        "exported_at": datetime.now().isoformat(),
        "total_count": len(memories),
        "memories": memories
    }
    
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    if output_file:
        output_file.write_text(json_str, encoding='utf-8')
        return str(output_file)
    
    return json_str


def export_markdown(memories: list, output_file: Path = None) -> str:
    """导出为Markdown"""
    lines = []
    lines.append("# AutoMemory 记忆导出")
    lines.append("")
    lines.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**记忆总数**: {len(memories)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 按日期分组
    by_date = {}
    for m in memories:
        date = m.get('timestamp', '')[:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(m)
    
    for date in sorted(by_date.keys(), reverse=True):
        lines.append(f"## 📅 {date}")
        lines.append("")
        
        for m in by_date[date]:
            time = m.get('timestamp', '')[11:16]
            tool = m.get('tool', '?')
            success = "✅" if m.get('success', True) else "❌"
            summary = m.get('summary', '无描述')
            category = m.get('category', '')
            
            lines.append(f"- **{time}** {success} [{tool}] {summary}")
            
            if errors := m.get('errors', []):
                for err in errors[:2]:
                    lines.append(f"  - 🔴 {err[:80]}")
        
        lines.append("")
    
    md_str = "\n".join(lines)
    
    if output_file:
        output_file.write_text(md_str, encoding='utf-8')
        return str(output_file)
    
    return md_str


def export_csv(memories: list, output_file: Path = None) -> str:
    """导出为CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    # 标题行
    writer.writerow(['时间', '工具', '状态', '类别', '摘要', '错误'])
    
    for m in memories:
        writer.writerow([
            m.get('timestamp', ''),
            m.get('tool', ''),
            '成功' if m.get('success', True) else '失败',
            m.get('category', ''),
            m.get('summary', ''),
            '; '.join(m.get('errors', [])[:3])
        ])
    
    csv_str = output.getvalue()
    
    if output_file:
        output_file.write_text(csv_str, encoding='utf-8')
        return str(output_file)
    
    return csv_str


def export_html(memories: list, output_file: Path = None) -> str:
    """导出为HTML"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AutoMemory 记忆导出</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .memory {{ padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; background: #f9f9f9; }}
        .error {{ border-left-color: #f44336; background: #fff0f0; }}
        .time {{ color: #666; font-size: 0.9em; }}
        .success {{ color: #4CAF50; }}
        .failure {{ color: #f44336; }}
    </style>
</head>
<body>
    <h1>🧠 AutoMemory 记忆导出</h1>
    <p>导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>记忆总数: {len(memories)}</p>
    <hr>
"""
    
    # 按日期分组
    by_date = {}
    for m in memories:
        date = m.get('timestamp', '')[:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(m)
    
    for date in sorted(by_date.keys(), reverse=True):
        html += f'<h2>📅 {date}</h2>\n'
        
        for m in by_date[date]:
            time = m.get('timestamp', '')[11:16]
            tool = m.get('tool', '?')
            success = m.get('success', True)
            summary = m.get('summary', '无描述')
            is_error = not success
            
            status_icon = '✅' if success else '❌'
            status_class = '' if success else 'error'
            
            html += f'<div class="memory {status_class}">\n'
            html += f'  <span class="time">{time}</span> '
            html += f'  <span class="{"success" if success else "failure"}">{status_icon} {tool}</span>\n'
            html += f'  <p>{summary}</p>\n'
            
            if errors := m.get('errors', []):
                html += '<ul>'
                for err in errors[:2]:
                    html += f'<li>🔴 {err[:100]}</li>\n'
                html += '</ul>\n'
            
            html += '</div>\n'
    
    html += """
</body>
</html>"""
    
    if output_file:
        output_file.write_text(html, encoding='utf-8')
        return str(output_file)
    
    return html


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] == "-h" or args[0] == "--help":
        print("""
📦 AutoMemory 数据导出

用法:
    export [格式] [选项]

格式:
    json      - 导出为 JSON
    md        - 导出为 Markdown
    csv       - 导出为 CSV
    html      - 导出为 HTML

选项:
    -d <天数>   导出最近天数 (默认: 30)
    -n <数量>   导出数量限制 (默认: 1000)
    -o <文件>   输出文件 (默认: 标准输出)

示例:
    export json -d 7           # 导出最近7天为JSON
    export md -o memories.md   # 导出为Markdown文件
    export csv                 # 导出为CSV
    export html -n 100         # 导出最近100条为HTML
""")
        return
    
    # 解析参数
    fmt = args[0] if args else "json"
    days = 30
    limit = 1000
    output_file = None
    
    i = 1
    while i < len(args):
        if args[i] == "-d" and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        elif args[i] == "-n" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "-o" and i + 1 < len(args):
            output_file = Path(args[i + 1])
            i += 2
        else:
            i += 1
    
    # 加载数据
    print(f"📥 加载最近 {days} 天的记忆...")
    memories = load_all_memories(days=days, limit=limit)
    print(f"📊 已加载 {len(memories)} 条记忆")
    
    if not memories:
        print("❌ 没有找到记忆数据")
        return
    
    # 导出
    if fmt == "json":
        result = export_json(memories, output_file)
        if output_file:
            print(f"✅ 已导出为 JSON: {result}")
        else:
            print(result[:500] + "...")
    
    elif fmt == "md":
        result = export_markdown(memories, output_file)
        if output_file:
            print(f"✅ 已导出为 Markdown: {result}")
        else:
            print(result[:500] + "...")
    
    elif fmt == "csv":
        result = export_csv(memories, output_file)
        if output_file:
            print(f"✅ 已导出为 CSV: {result}")
        else:
            print(result[:500] + "...")
    
    elif fmt == "html":
        result = export_html(memories, output_file)
        if output_file:
            print(f"✅ 已导出为 HTML: {result}")
        else:
            print(result[:500] + "...")
    
    else:
        print(f"❌ 未知格式: {fmt}")


if __name__ == "__main__":
    main()
