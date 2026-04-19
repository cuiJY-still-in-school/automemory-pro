#!/usr/bin/env python3
"""
AutoMemory Pro - 定时提醒
Scheduled Reminders - 系统通知集成

用法:
    remind add "内容" --time "09:00" --repeat daily
    remind list
    remind delete <id>
    remind check

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
REMIND_DIR = Path.home() / ".openclaw" / "automemory" / "reminders"
REMIND_FILE = REMIND_DIR / "scheduled_reminders.json"


def ensure_dir():
    """确保目录存在"""
    REMIND_DIR.mkdir(parents=True, exist_ok=True)


def load_reminders() -> list:
    """加载提醒"""
    ensure_dir()
    if REMIND_FILE.exists():
        try:
            with open(REMIND_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []


def save_reminders(reminders: list):
    """保存提醒"""
    ensure_dir()
    with open(REMIND_FILE, 'w', encoding='utf-8') as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)


def add_reminder(content: str, time_str: str = None, repeat: str = None, note_type: str = "reminder") -> dict:
    """添加提醒"""
    reminders = load_reminders()
    
    reminder = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "content": content,
        "time": time_str or "09:00",
        "repeat": repeat,  # daily, weekly, monthly, None
        "type": note_type,
        "created_at": datetime.now().isoformat(),
        "last_triggered": None,
        "enabled": True
    }
    
    reminders.append(reminder)
    save_reminders(reminders)
    
    return reminder


def list_reminders() -> list:
    """列出所有提醒"""
    return load_reminders()


def delete_reminder(reminder_id: str) -> bool:
    """删除提醒"""
    reminders = load_reminders()
    original_count = len(reminders)
    reminders = [r for r in reminders if r["id"] != reminder_id]
    
    if len(reminders) < original_count:
        save_reminders(reminders)
        return True
    return False


def check_reminders() -> list:
    """检查是否需要触发提醒"""
    reminders = load_reminders()
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_weekday = now.strftime("%a")
    current_day = now.day
    
    triggered = []
    
    for r in reminders:
        if not r.get("enabled", True):
            continue
        
        # 检查时间
        if r.get("time") != current_time:
            continue
        
        # 检查重复
        repeat = r.get("repeat")
        last_triggered = r.get("last_triggered")
        
        if repeat == "daily":
            # 每天都触发
            r["last_triggered"] = now.isoformat()
            triggered.append(r)
            
        elif repeat == "weekly" and current_weekday == "Mon":
            # 每周一触发
            if not last_triggered or (now - datetime.fromisoformat(last_triggered)).days >= 7:
                r["last_triggered"] = now.isoformat()
                triggered.append(r)
                
        elif repeat == "monthly" and current_day == 1:
            # 每月1号触发
            if not last_triggered or (now - datetime.fromisoformat(last_triggered)).days >= 30:
                r["last_triggered"] = now.isoformat()
                triggered.append(r)
    
    if triggered:
        save_reminders(reminders)
    
    return triggered


def send_notification(title: str, body: str):
    """发送系统通知"""
    # 尝试不同系统的通知命令
    commands = [
        # Linux (notify-send)
        ["notify-send", title, body],
        # macOS
        ["osascript", "-e", f'display notification "{body}" with title "{title}"'],
        # Windows
        ["powershell", "-Command", f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); $text = $template.GetElementsByTagName("text"); $text.Item(0).AppendChild($template.CreateTextNode("{title}")) | Out-Null; $text.Item(1).AppendChild($template.CreateTextNode("{body}")) | Out-Null; [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("AutoMemory").Show([Windows.UI.Notifications.ToastNotification]::new($template))'],
    ]
    
    for cmd in commands:
        try:
            import subprocess
            subprocess.run(cmd, capture_output=True, timeout=5)
            return True
        except:
            continue
    
    return False


def format_reminder(r: dict, index: int = None) -> str:
    """格式化提醒"""
    repeat_str = {
        "daily": "📅 每天",
        "weekly": "📆 每周",
        "monthly": "🗓️ 每月",
        None: "⏰ 单次"
    }.get(r.get("repeat"), "⏰")
    
    enabled = "✅" if r.get("enabled", True) else "❌"
    idx = f"{index}. " if index is not None else ""
    
    return f"{idx}{enabled} {repeat_str} {r.get('time')} - {r.get('content')[:40]}"


def show_reminders():
    """显示所有提醒"""
    reminders = list_reminders()
    
    if not reminders:
        print("\n📭 暂无定时提醒")
        print("   使用 'remind add \"内容\" --time 09:00' 添加")
        return
    
    print(f"\n⏰ 定时提醒 (共{len(reminders)}个)")
    print("=" * 50)
    
    for i, r in enumerate(reminders, 1):
        print(f"  {format_reminder(r, i)}")


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] == "-h" or args[0] == "--help":
        print("""
⏰ AutoMemory 定时提醒

用法:
    remind add "内容" [--time HH:MM] [--repeat daily|weekly|monthly]
    remind list
    remind delete <id>
    remind check
    remind now "内容"

示例:
    remind add "检查Signal Arena" --time 09:00 --repeat daily
    remind add "周总结" --time 17:00 --repeat weekly
    remind list
    remind delete 1
    remind check
    remind now "测试通知"
""")
        return
    
    if args[0] == "add":
        # 解析参数
        content = None
        time_str = "09:00"
        repeat = None
        
        i = 1
        while i < len(args):
            if args[i] == "--time" and i + 1 < len(args):
                time_str = args[i + 1]
                i += 2
            elif args[i] == "--repeat" and i + 1 < len(args):
                repeat = args[i + 1]
                i += 2
            else:
                content = args[i]
                i += 1
        
        if not content:
            print("❌ 请输入提醒内容")
            return
        
        r = add_reminder(content, time_str, repeat)
        print(f"✅ 已添加: {format_reminder(r)}")
    
    elif args[0] == "list":
        show_reminders()
    
    elif args[0] == "delete":
        if len(args) < 2:
            print("❌ 请指定要删除的提醒ID")
            return
        
        if delete_reminder(args[1]):
            print(f"✅ 已删除提醒")
        else:
            print(f"❌ 未找到提醒: {args[1]}")
    
    elif args[0] == "check":
        triggered = check_reminders()
        if triggered:
            print(f"\n🔔 触发 {len(triggered)} 个提醒:")
            for r in triggered:
                print(f"  - {r['content']}")
                send_notification("AutoMemory 提醒", r['content'])
        else:
            print("✅ 暂无需要触发的提醒")
    
    elif args[0] == "now":
        if len(args) < 2:
            print("❌ 请输入通知内容")
            return
        
        content = " ".join(args[1:])
        if send_notification("AutoMemory", content):
            print(f"✅ 通知已发送: {content}")
        else:
            print(f"⚠️ 通知发送失败（可能不支持系统通知）")


if __name__ == "__main__":
    main()
