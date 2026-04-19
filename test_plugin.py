#!/usr/bin/env python3
"""
AutoMemory 插件测试脚本
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加插件目录到路径
plugin_dir = Path.home() / ".openclaw" / "plugins" / "automemory"
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

print("=" * 60)
print("AutoMemory 插件测试")
print("=" * 60)

# 1. 测试导入
print("\n1. 测试模块导入...")
try:
    from automemory import AutoMemoryPlugin
    print("   ✅ 导入成功")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

# 2. 初始化插件
print("\n2. 初始化插件...")
try:
    plugin = AutoMemoryPlugin()
    print(f"   ✅ 插件初始化成功")
    print(f"   📁 记忆目录: {plugin.memory_dir}")
    print(f"   ⚙️  配置: enabled={plugin.config.get('enabled')}, threshold={plugin.config.get('importance_threshold')}")
except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    sys.exit(1)

# 3. 测试会话开始
print("\n3. 测试会话开始...")
try:
    plugin.on_session_start({
        "session_id": f"test_session_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "working_dir": str(Path.home())
    })
    print("   ✅ 会话开始处理成功")
except Exception as e:
    print(f"   ❌ 会话开始失败: {e}")

# 4. 测试工具调用记录
print("\n4. 测试工具调用记录...")
test_cases = [
    {
        "name": "创建文件",
        "tool": "write",
        "params": {"path": "/home/user/test.txt", "content": "Hello World"},
        "context": {"working_dir": "/home/user", "current_task": "testing"}
    },
    {
        "name": "执行命令",
        "tool": "exec",
        "params": {"command": "ls -la"},
        "context": {"working_dir": "/home/user"}
    },
    {
        "name": "获取网页",
        "tool": "web_fetch",
        "params": {"url": "https://example.com"},
        "context": {}
    }
]

for i, test in enumerate(test_cases, 1):
    try:
        plugin.on_tool_call(test["tool"], test["params"], test["context"])
        plugin.on_tool_result(
            test["tool"], 
            test["params"], 
            {"status": "success", "message": f"Test {i} successful"},
            test["context"]
        )
        print(f"   ✅ {test['name']}: 已记录")
    except Exception as e:
        print(f"   ❌ {test['name']}: {e}")

# 5. 测试错误记录
print("\n5. 测试错误记录...")
try:
    plugin.on_tool_result(
        "exec",
        {"command": "invalid_command"},
        {"exit_code": 1, "stderr": "command not found"},
        {}
    )
    print("   ✅ 错误记录测试完成")
except Exception as e:
    print(f"   ❌ 错误记录失败: {e}")

# 6. 获取统计
print("\n6. 获取会话统计...")
try:
    stats = plugin.get_session_stats()
    print(f"   📊 本会话记忆数: {stats['memories_count']}")
    print(f"   ⏱️  会话时长: {stats['duration_minutes']:.1f} 分钟")
except Exception as e:
    print(f"   ❌ 获取统计失败: {e}")

# 7. 测试搜索
print("\n7. 测试记忆搜索...")
try:
    memories = plugin.search_memories("test", limit=5)
    print(f"   🔍 找到 {len(memories)} 条相关记忆")
    if memories:
        print("   📋 最近的一条:")
        print(f"      工具: {memories[0].get('tool')}")
        print(f"      时间: {memories[0].get('timestamp')}")
        print(f"      重要性: {memories[0].get('importance', 0):.2f}")
except Exception as e:
    print(f"   ❌ 搜索失败: {e}")

# 8. 测试会话结束
print("\n8. 测试会话结束...")
try:
    plugin.on_session_end({"session_id": plugin.session_id})
    print("   ✅ 会话结束处理成功")
except Exception as e:
    print(f"   ❌ 会话结束失败: {e}")

# 9. 检查记忆文件
print("\n9. 检查记忆文件...")
try:
    memory_files = list(plugin.memory_dir.glob("memories_*.jsonl"))
    print(f"   📁 发现 {len(memory_files)} 个记忆文件")
    
    if memory_files:
        latest = max(memory_files, key=lambda p: p.stat().st_mtime)
        print(f"   📝 最新文件: {latest.name}")
        print(f"   📊 文件大小: {latest.stat().st_size} 字节")
        
        # 读取几行看看
        with open(latest, 'r') as f:
            lines = f.readlines()
            print(f"   📈 记忆条目数: {len(lines)}")
            
            if lines:
                try:
                    first = json.loads(lines[0])
                    print(f"   🔍 第一条记忆:")
                    print(f"      类型: {first.get('type')}")
                    print(f"      工具: {first.get('tool')}")
                    print(f"      分类: {first.get('category')}")
                except:
                    pass
except Exception as e:
    print(f"   ❌ 检查文件失败: {e}")

# 10. 总结
print("\n" + "=" * 60)
print("测试结果总结")
print("=" * 60)

# 检查MEMORY.md是否被更新
memory_md = Path.home() / "MEMORY.md"
if memory_md.exists():
    print(f"📄 MEMORY.md存在: {memory_md}")
    print("   (高重要性记忆会自动追加到该文件)")
else:
    print("⚠️  MEMORY.md不存在，高重要性记忆不会同步")

print(f"\n✨ AutoMemory插件测试完成!")
print(f"📁 记忆存储位置: {plugin.memory_dir}")
print(f"\n💡 提示:")
print("   - 记忆文件按天存储: memories_YYYY-MM-DD.jsonl")
print("   - 使用 search_memories() 方法搜索历史")
print("   - 会话摘要保存在 session_*.json")
print("   - 重要性≥0.8的记忆会自动同步到 MEMORY.md")
print("=" * 60)