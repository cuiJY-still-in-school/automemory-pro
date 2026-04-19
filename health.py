#!/usr/bin/env python3
"""
AutoMemory Pro - 健康检查
Health Check - 系统状态诊断

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
sys.path.insert(0, str(PLUGIN_DIR))


def check_directory_structure() -> dict:
    """检查目录结构"""
    result = {
        "status": "pass",
        "issues": [],
        "warnings": []
    }
    
    # 必要目录
    required_dirs = [
        MEMORY_DIR,
        MEMORY_DIR / "notes",
        MEMORY_DIR / "reminders",
        MEMORY_DIR / "summaries"
    ]
    
    for d in required_dirs:
        if not d.exists():
            result["issues"].append(f"❌ 目录不存在: {d}")
            result["status"] = "fail"
        else:
            pass  # 正常
    
    # 可选目录
    optional_dirs = [
        MEMORY_DIR / "briefings",
        MEMORY_DIR / "reports"
    ]
    
    for d in optional_dirs:
        if not d.exists():
            result["warnings"].append(f"⚠️ 可选目录不存在: {d}")
    
    return result


def check_disk_space() -> dict:
    """检查磁盘空间"""
    result = {
        "status": "pass",
        "total": 0,
        "used": 0,
        "free": 0,
        "percent": 0
    }
    
    try:
        import shutil
        stat = shutil.disk_usage("/")
        result["total"] = stat.total / (1024**3)  # GB
        result["used"] = stat.used / (1024**3)
        result["free"] = stat.free / (1024**3)
        result["percent"] = stat.used / stat.total * 100
        
        if result["percent"] > 90:
            result["status"] = "fail"
            result["issue"] = f"磁盘空间不足！仅剩 {result['free']:.1f}GB"
        elif result["percent"] > 80:
            result["status"] = "warn"
            result["warning"] = f"磁盘空间紧张 ({result['percent']:.1f}%已用)"
    
    except Exception as e:
        result["status"] = "unknown"
        result["error"] = str(e)
    
    return result


def check_data_files() -> dict:
    """检查数据文件"""
    result = {
        "status": "pass",
        "memory_files": 0,
        "total_memories": 0,
        "oldest_file": None,
        "newest_file": None,
        "issues": []
    }
    
    memory_files = list(MEMORY_DIR.glob("memories_*.jsonl"))
    result["memory_files"] = len(memory_files)
    
    if not memory_files:
        result["issues"].append("❌ 没有记忆文件！")
        result["status"] = "fail"
        return result
    
    # 统计记忆数量
    all_memories = []
    for mf in memory_files:
        try:
            with open(mf, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f)
                result["total_memories"] += count
                
                # 提取日期
                date_str = mf.stem.replace("memories_", "")
                all_memories.append((date_str, mf))
        except:
            continue
    
    # 找最老和最新的文件
    if all_memories:
        all_memories.sort()
        result["oldest_file"] = all_memories[0][0]
        result["newest_file"] = all_memories[-1][0]
    
    # 检查文件大小
    large_files = []
    for mf in memory_files:
        size_mb = mf.stat().st_size / (1024**2)
        if size_mb > 10:
            large_files.append(f"{mf.name}: {size_mb:.1f}MB")
    
    if large_files:
        result["warnings"] = large_files
        result["status"] = "warn"
    
    return result


def check_permissions() -> dict:
    """检查权限"""
    result = {
        "status": "pass",
        "issues": []
    }
    
    # 检查关键文件可写
    test_files = [
        MEMORY_DIR / "test_write.tmp",
        MEMORY_DIR / "notes" / "test.tmp"
    ]
    
    for tf in test_files:
        try:
            tf.parent.mkdir(parents=True, exist_ok=True)
            tf.write_text("test")
            tf.unlink()
        except Exception as e:
            result["issues"].append(f"❌ 无写权限: {tf.parent}")
            result["status"] = "fail"
    
    return result


def check_config() -> dict:
    """检查配置"""
    result = {
        "status": "pass",
        "config": {},
        "issues": []
    }
    
    config_file = MEMORY_DIR.parent / "automemory.json"
    
    if not config_file.exists():
        result["warnings"] = ["⚠️ 配置文件不存在，将使用默认配置"]
        return result
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            result["config"] = config
            
            # 检查必要配置
            if not config.get("enabled", True):
                result["issues"].append("⚠️ 插件已禁用")
            
            threshold = config.get("importance_threshold", 0.5)
            if threshold > 0.8:
                result["warnings"] = [f"⚠️ 重要性阈值过高: {threshold}"]
            
    except Exception as e:
        result["status"] = "fail"
        result["issues"].append(f"❌ 配置文件读取失败: {e}")
    
    return result


def check_recent_activity() -> dict:
    """检查最近活动"""
    result = {
        "status": "pass",
        "today_count": 0,
        "week_count": 0,
        "recent_days": 0,
        "warnings": []
    }
    
    from datetime import timedelta
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_ago = now - timedelta(days=7)
    
    memory_files = list(MEMORY_DIR.glob("memories_*.jsonl"))
    recent_dates = set()
    
    for mf in memory_files:
        try:
            with open(mf, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        ts_str = m.get('timestamp', '')
                        if ts_str.startswith(today_str):
                            result["today_count"] += 1
                        
                        ts = datetime.fromisoformat(ts_str)
                        if ts >= week_ago:
                            result["week_count"] += 1
                        
                        recent_dates.add(ts_str[:10])
                    except:
                        continue
        except:
            continue
    
    result["recent_days"] = len(recent_dates)
    
    if result["today_count"] == 0:
        result["warnings"].append("⚠️ 今天没有活动记录")
    
    if result["recent_days"] < 3:
        result["status"] = "warn"
        result["warnings"].append(f"⚠️ 最近只有{result['recent_days']}天有活动")
    
    return result


def print_result(title: str, result: dict, indent: int = 2):
    """打印检查结果"""
    spaces = " " * indent
    
    status_icon = {
        "pass": "✅",
        "warn": "⚠️",
        "fail": "❌",
        "unknown": "❓"
    }.get(result.get("status", "unknown"), "❓")
    
    print(f"{spaces}{status_icon} {title}")
    
    # 打印详细信息
    for key, value in result.items():
        if key not in ["status"] and isinstance(value, (str, int, float)):
            print(f"{spaces}   {key}: {value}")
    
    # 打印问题
    for issue in result.get("issues", []):
        print(f"{spaces}   {issue}")
    
    # 打印警告
    for warning in result.get("warnings", []):
        print(f"{spaces}   {warning}")


def main():
    """主函数"""
    print()
    print("🩺 AutoMemory 健康检查")
    print("=" * 50)
    
    all_pass = True
    
    # 1. 目录结构
    print("\n📁 目录结构:")
    dir_result = check_directory_structure()
    print_result("目录检查", dir_result)
    if dir_result["status"] != "pass":
        all_pass = False
    
    # 2. 磁盘空间
    print("\n💾 磁盘空间:")
    disk_result = check_disk_space()
    if disk_result["status"] == "pass":
        print(f"   ✅ 已用: {disk_result['percent']:.1f}% ({disk_result['used']:.1f}GB / {disk_result['total']:.1f}GB)")
    else:
        print(f"   ❌ {disk_result.get('issue', disk_result.get('error', '未知错误'))}")
        all_pass = False
    
    # 3. 数据文件
    print("\n📊 数据文件:")
    data_result = check_data_files()
    print(f"   📁 记忆文件: {data_result['memory_files']}个")
    print(f"   📝 记忆总数: {data_result['total_memories']}条")
    if data_result.get("oldest_file"):
        print(f"   📅 数据范围: {data_result['oldest_file']} ~ {data_result['newest_file']}")
    for issue in data_result.get("issues", []):
        print(f"   {issue}")
        all_pass = False
    for warning in data_result.get("warnings", []):
        print(f"   ⚠️ {warning}")
    
    # 4. 权限
    print("\n🔐 权限:")
    perm_result = check_permissions()
    if perm_result["status"] == "pass":
        print("   ✅ 读写权限正常")
    else:
        for issue in perm_result["issues"]:
            print(f"   {issue}")
        all_pass = False
    
    # 5. 配置
    print("\n⚙️ 配置:")
    config_result = check_config()
    if config_result["config"]:
        enabled = config_result["config"].get("enabled", True)
        print(f"   {'✅' if enabled else '❌'} 插件: {'启用' if enabled else '禁用'}")
        threshold = config_result["config"].get("importance_threshold", 0.5)
        print(f"   📌 重要性阈值: {threshold}")
    for warning in config_result.get("warnings", []):
        print(f"   {warning}")
    
    # 6. 最近活动
    print("\n📈 最近活动:")
    activity_result = check_recent_activity()
    print(f"   📝 今日记录: {activity_result['today_count']}条")
    print(f"   📝 本周记录: {activity_result['week_count']}条")
    print(f"   📅 活跃天数: {activity_result['recent_days']}天")
    for warning in activity_result.get("warnings", []):
        print(f"   {warning}")
    
    # 总结
    print()
    print("=" * 50)
    if all_pass:
        print("✅ 健康检查通过！系统运行正常！")
    else:
        print("⚠️ 发现问题，建议修复")
    print()


if __name__ == "__main__":
    main()
