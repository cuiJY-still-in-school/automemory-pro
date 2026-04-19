#!/usr/bin/env python3
"""
AutoMemory Pro - GitHub自动备份
Auto Backup - 定时备份记忆到GitHub

用法:
    backup init [--repo <repo-url>]
    backup now
    backup status
    backup enable
    backup disable

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
BACKUP_DIR = MEMORY_DIR / "backup"
CONFIG_FILE = BACKUP_DIR / "backup_config.json"


def ensure_dir():
    """确保目录存在"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """加载配置"""
    ensure_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "enabled": False,
        "repo_url": None,
        "last_backup": None,
        "backup_count": 0,
        "auto_backup": "daily"
    }


def save_config(config: dict):
    """保存配置"""
    ensure_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def init_backup(repo_url: str = None) -> bool:
    """初始化备份仓库"""
    ensure_dir()
    
    # 如果没有指定repo，尝试使用默认的memory-backup仓库
    if not repo_url:
        # 使用GitHub的memory-backup仓库
        import os
        username = os.environ.get("USER", "user")
        repo_url = f"https://github.com/{username}/automemory-backup.git"
    
    config = load_config()
    config["repo_url"] = repo_url
    config["enabled"] = True
    
    # 创建备份仓库
    backup_repo = BACKUP_DIR / "repo"
    
    try:
        if backup_repo.exists():
            # 更新
            subprocess.run(["git", "-C", str(backup_repo), "pull"], capture_output=True, timeout=30)
        else:
            # 克隆
            subprocess.run(["git", "clone", repo_url, str(backup_repo)], 
                        capture_output=True, timeout=60)
        
        save_config(config)
        print(f"✅ 备份仓库已初始化: {repo_url}")
        return True
    
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def backup_now() -> bool:
    """立即备份"""
    config = load_config()
    
    if not config.get("enabled"):
        print("❌ 备份未启用，请先运行 'backup init'")
        return False
    
    backup_repo = BACKUP_DIR / "repo"
    
    if not backup_repo.exists():
        print("❌ 备份仓库未初始化，请先运行 'backup init'")
        return False
    
    try:
        # 复制记忆文件到备份目录
        memories_backup = backup_repo / "memories"
        memories_backup.mkdir(parents=True, exist_ok=True)
        
        # 复制所有记忆文件
        import shutil
        for mf in MEMORY_DIR.glob("memories_*.jsonl"):
            shutil.copy2(mf, memories_backup / mf.name)
        
        # 复制配置
        config_src = MEMORY_DIR.parent / "automemory.json"
        if config_src.exists():
            shutil.copy2(config_src, backup_repo / "config.json")
        
        # 提交
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        subprocess.run(["git", "-C", str(backup_repo), "add", "."], capture_output=True)
        result = subprocess.run(["git", "-C", str(backup_repo), "commit", "-m", 
                            f"Backup {timestamp}"], capture_output=True)
        
        if result.returncode == 0:
            # 推送
            push_result = subprocess.run(["git", "-C", str(backup_repo), "push"], 
                                      capture_output=True, timeout=30)
            
            if push_result.returncode == 0:
                config["last_backup"] = datetime.now().isoformat()
                config["backup_count"] = config.get("backup_count", 0) + 1
                save_config(config)
                
                print(f"✅ 备份成功！({config['backup_count']}次备份)")
                return True
            else:
                print(f"⚠️ 提交成功但推送失败: {push_result.stderr.decode()}")
                return False
        else:
            print("ℹ️ 没有新内容需要备份")
            return True
    
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False


def show_status():
    """显示状态"""
    config = load_config()
    
    print("\n📦 AutoMemory 备份状态")
    print("=" * 50)
    
    if config.get("enabled"):
        print(f"   ✅ 备份状态: 已启用")
        print(f"   📁 仓库: {config.get('repo_url', '未设置')}")
        
        last = config.get("last_backup")
        if last:
            last_dt = datetime.fromisoformat(last)
            print(f"   🕐 上次备份: {last_dt.strftime('%Y-%m-%d %H:%M')}")
        
        print(f"   📊 备份次数: {config.get('backup_count', 0)}")
        print(f"   🔄 自动备份: {config.get('auto_backup', 'daily')}")
    else:
        print("   ❌ 备份状态: 未启用")
        print("   运行 'backup init' 初始化")
    
    print()


def enable_auto_backup(interval: str = "daily"):
    """启用自动备份"""
    config = load_config()
    config["enabled"] = True
    config["auto_backup"] = interval
    save_config(config)
    print(f"✅ 已启用自动备份 ({interval})")


def disable_backup():
    """禁用备份"""
    config = load_config()
    config["enabled"] = False
    save_config(config)
    print("✅ 已禁用备份")


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] == "-h" or args[0] == "--help":
        print("""
📦 AutoMemory GitHub备份

用法:
    backup init [--repo <repo-url>]  初始化备份仓库
    backup now                        立即备份
    backup status                    查看状态
    backup enable                    启用自动备份
    backup disable                   禁用备份

示例:
    backup init                      # 使用默认仓库
    backup init --repo https://github.com/user/repo  # 指定仓库
    backup now                      # 立即备份
    backup status                   # 查看状态
    backup enable daily             # 每天自动备份
""")
        return
    
    if args[0] == "init":
        repo_url = None
        if "--repo" in args:
            idx = args.index("--repo")
            repo_url = args[idx + 1] if idx + 1 < len(args) else None
        
        init_backup(repo_url)
    
    elif args[0] == "now":
        backup_now()
    
    elif args[0] == "status":
        show_status()
    
    elif args[0] == "enable":
        interval = args[1] if len(args) > 1 else "daily"
        enable_auto_backup(interval)
    
    elif args[0] == "disable":
        disable_backup()
    
    else:
        print(f"❌ 未知命令: {args[0]}")


if __name__ == "__main__":
    main()
