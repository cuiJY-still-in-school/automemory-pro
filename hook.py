# OpenClaw Hook - AutoMemory 插件集成
#
# 将此文件放入 ~/.openclaw/hooks/ 目录
# 功能：在工具调用前后自动保存记忆

import sys
import json
from pathlib import Path

# 添加插件目录到路径
plugin_dir = Path.home() / ".openclaw" / "plugins" / "automemory"
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

try:
    from automemory import init_plugin, on_tool_call, on_tool_result, on_session_start, on_session_end
    
    # 初始化插件
    _plugin = init_plugin()
    
    def before_tool_call(tool_name: str, params: dict, context: dict) -> dict:
        """工具调用前的钩子"""
        try:
            result = on_tool_call(tool_name, params, context)
            if result:
                return result
        except Exception as e:
            print(f"[AutoMemory] 工具调用前处理失败: {e}")
        return {}
    
    def after_tool_call(tool_name: str, params: dict, result: any, context: dict) -> dict:
        """工具调用后的钩子"""
        try:
            memory_result = on_tool_result(tool_name, params, result, context)
            if memory_result:
                return memory_result
        except Exception as e:
            print(f"[AutoMemory] 工具结果处理失败: {e}")
        return {}
    
    def on_session_start_hook(session_info: dict):
        """会话开始钩子"""
        try:
            on_session_start(session_info)
        except Exception as e:
            print(f"[AutoMemory] 会话开始处理失败: {e}")
    
    def on_session_end_hook(session_info: dict):
        """会话结束钩子"""
        try:
            on_session_end(session_info)
        except Exception as e:
            print(f"[AutoMemory] 会话结束处理失败: {e}")
    
    # 注册钩子
    HOOKS = {
        "before_tool_call": before_tool_call,
        "after_tool_call": after_tool_call,
        "session_start": on_session_start_hook,
        "session_end": on_session_end_hook
    }
    
    print("[AutoMemory] 插件已加载")
    
except ImportError as e:
    print(f"[AutoMemory] 插件加载失败: {e}")
    HOOKS = {}
except Exception as e:
    print(f"[AutoMemory] 插件初始化失败: {e}")
    HOOKS = {}