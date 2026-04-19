#!/usr/bin/env python3
"""
AutoMemory Pro - 快速笔记
Quick Note - 随手记录灵感、想法、待办

用法:
    note "我的灵感"
    note -t todo "要完成的任务"
    note -t idea "好想法"
    note -t bug "发现的问题"
    note -t decision "做的决定"

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加插件路径
PLUGIN_DIR = Path(__file__).parent
sys.path.insert(0, str(PLUGIN_DIR))

NOTE_TYPES = {
    "note": "📝 普通笔记",
    "todo": "☑️ 待办",
    "idea": "💡 灵感",
    "bug": "🐛 问题",
    "decision": "📋 决定",
    "learn": "📚 学到",
    "link": "🔗 链接",
    "quote": "💬 引用"
}

def get_notes_dir():
    """获取笔记目录"""
    notes_dir = Path.home() / ".openclaw" / "automemory" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    return notes_dir

def save_note(content: str, note_type: str = "note") -> str:
    """保存笔记"""
    notes_dir = get_notes_dir()
    
    note = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "type": note_type,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "tags": []
    }
    
    filename = notes_dir / f"{note_type}_{note['id']}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(note, f, ensure_ascii=False, indent=2)
    
    return filename.name

def load_notes(limit: int = 10, note_type: str = None) -> list:
    """加载笔记"""
    notes_dir = get_notes_dir()
    notes = []
    
    pattern = f"{note_type}_*.json" if note_type else "*.json"
    
    for f in sorted(notes_dir.glob(pattern), reverse=True)[:limit]:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                notes.append(json.load(file))
        except:
            continue
    
    return notes

def format_note(note: dict) -> str:
    """格式化单条笔记"""
    icon = NOTE_TYPES.get(note.get("type", "note"), "📝")
    timestamp = note.get("timestamp", "")[:16]
    content = note.get("content", "")
    return f"{icon} [{timestamp}] {content}"

def show_notes(note_type: str = None, limit: int = 10):
    """显示笔记"""
    notes = load_notes(limit=limit, note_type=note_type)
    
    if not notes:
        print("📭 暂无笔记")
        return
    
    # 按类型分组显示
    if note_type:
        print(f"📂 {NOTE_TYPES.get(note_type, note_type)}")
        for n in notes:
            print(f"  {format_note(n)}")
    else:
        # 全部显示，按时间
        print(f"📚 最近笔记 (共{len(notes)}条)")
        print("-" * 50)
        for n in notes:
            print(format_note(n))

def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] in ["-h", "--help"]:
        print("""
🖊️ AutoMemory Quick Note

用法:
    note [选项] [内容]

选项:
    -t <类型>   笔记类型 (默认: note)
    -l [数量]   显示最近笔记 (默认: 10)
    -h          显示帮助

类型:
    note      📝 普通笔记
    todo      ☑️ 待办
    idea      💡 灵感
    bug       🐛 问题
    decision  📋 决定
    learn     📚 学到
    link      🔗 链接
    quote     💬 引用

示例:
    note "灵光一现的想法"
    note -t todo "要完成的任务"
    note -t idea "可以做X项目"
    note -l 20           # 显示最近20条
    note -l 5 -t idea    # 显示最近5条灵感
""")
        return
    
    # 显示模式
    if args[0] == "-l":
        limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
        note_type = None
        if len(args) > 2 and args[2] == "-t" and len(args) > 3:
            note_type = args[3]
        show_notes(note_type=note_type, limit=limit)
        return
    
    # 添加笔记模式
    note_type = "note"
    content_parts = []
    
    i = 0
    while i < len(args):
        if args[i] == "-t" and i + 1 < len(args):
            note_type = args[i + 1]
            i += 2
        else:
            content_parts.append(args[i])
            i += 1
    
    content = " ".join(content_parts)
    
    if not content:
        print("❌ 请输入内容")
        return
    
    if note_type not in NOTE_TYPES:
        print(f"❌ 未知类型: {note_type}")
        print(f"   可用类型: {', '.join(NOTE_TYPES.keys())}")
        return
    
    # 保存
    filename = save_note(content, note_type)
    icon = NOTE_TYPES[note_type]
    print(f"✅ {icon} 已保存: {content[:50]}")

if __name__ == "__main__":
    main()