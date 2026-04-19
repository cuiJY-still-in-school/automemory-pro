#!/usr/bin/env python3
"""
AutoMemory Plugin - 自动记忆保存插件

功能：
1. 监听工具调用事件
2. 自动提取重要信息
3. 保存到记忆系统
4. 提供语义搜索和检索
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# 设置日志
import logging
import sys

# 静默日志，只显示警告和错误
if '--quiet' not in sys.argv and '-q' not in sys.argv:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
else:
    logging.basicConfig(level=logging.WARNING, format='%(message)s')
logger = logging.getLogger("AutoMemory")

class AutoMemoryPlugin:
    """自动记忆保存插件主类"""
    
    def __init__(self, config_path: str = None):
        """初始化插件"""
        self.plugin_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.memory_dir = Path.home() / ".openclaw" / "automemory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前会话的记忆缓存
        self.session_memories = []
        self.session_id = None
        self.session_start_time = None
        
        logger.info(f"AutoMemory插件初始化完成 - 记忆目录: {self.memory_dir}")
    
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        default_config = {
            "enabled": True,
            "auto_save": True,
            "importance_threshold": 0.5,
            "max_memories_per_session": 50,
            "memory_retention_days": 30,
            "categories": ["decisions", "actions", "discoveries", "errors", "preferences"],
            "excluded_tools": ["memory_search", "memory_get", "session_status"],
            "extract_patterns": {
                "decisions": [
                    r"决定.*|选择.*|计划.*|策略.*",
                    r"will.*|decide.*|choose.*|plan.*|strategy.*"
                ],
                "actions": [
                    r"创建.*|修改.*|删除.*|执行.*|完成.*",
                    r"create.*|modify.*|delete.*|execute.*|complete.*"
                ],
                "discoveries": [
                    r"发现.*|找到.*|检测到.*|注意到.*",
                    r"discover.*|find.*|detect.*|notice.*|found.*"
                ],
                "errors": [
                    r"错误.*|失败.*|异常.*|警告.*",
                    r"error.*|fail.*|exception.*|warning.*"
                ],
                "preferences": [
                    r"偏好.*|喜欢.*|需要.*|想要.*",
                    r"prefer.*|like.*|need.*|want.*"
                ]
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"加载配置文件: {config_path}")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
        
        # 尝试加载plugin.json
        plugin_json = self.plugin_dir / "plugin.json"
        if plugin_json.exists():
            try:
                with open(plugin_json, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                if "config" in plugin_config:
                    default_config.update(plugin_config["config"])
            except Exception as e:
                logger.error(f"加载plugin.json失败: {e}")
        
        return default_config
    
    def on_session_start(self, session_info: Dict) -> None:
        """会话开始时的处理"""
        self.session_id = session_info.get("session_id", "unknown")
        self.session_start_time = datetime.now()
        self.session_memories = []
        
        logger.info(f"会话开始: {self.session_id}")
        
        # 加载相关历史记忆
        self._load_relevant_memories(session_info)
    
    def on_session_end(self, session_info: Dict) -> None:
        """会话结束时的处理"""
        if not self.config.get("enabled", True):
            return
        
        # 保存会话摘要
        self._save_session_summary()
        
        # 清理旧记忆
        self._cleanup_old_memories()
        
        logger.info(f"会话结束: {self.session_id}, 共保存 {len(self.session_memories)} 条记忆")
    
    def on_tool_call(self, tool_name: str, tool_params: Dict, context: Dict) -> Optional[Dict]:
        """工具调用时的处理"""
        if not self.config.get("enabled", True):
            return None
        
        # 排除不需要记录的工具
        if tool_name in self.config.get("excluded_tools", []):
            return None
        
        # 创建工具调用记忆
        memory = {
            "id": self._generate_id(f"{tool_name}_{datetime.now().isoformat()}"),
            "type": "tool_call",
            "tool": tool_name,
            "params": self._sanitize_params(tool_params),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "context": {
                "working_dir": context.get("working_dir"),
                "current_task": context.get("current_task"),
                "user_intent": context.get("user_intent")
            }
        }
        
        # 提取重要性
        memory["importance"] = self._calculate_importance(memory)
        
        # 如果重要性超过阈值，保存
        if memory["importance"] >= self.config.get("importance_threshold", 0.5):
            self._save_memory(memory)
            self.session_memories.append(memory)
            logger.debug(f"保存工具调用记忆: {tool_name}")
        
        return None
    
    def on_tool_result(self, tool_name: str, tool_params: Dict, 
                       tool_result: Any, context: Dict) -> Optional[Dict]:
        """工具返回结果时的处理"""
        if not self.config.get("enabled", True):
            return None
        
        if tool_name in self.config.get("excluded_tools", []):
            return None
        
        # 分析结果
        result_analysis = self._analyze_result(tool_name, tool_params, tool_result)
        
        # 创建结果记忆
        memory = {
            "id": self._generate_id(f"result_{tool_name}_{datetime.now().isoformat()}"),
            "type": "tool_result",
            "tool": tool_name,
            "success": result_analysis.get("success", True),
            "summary": result_analysis.get("summary", ""),
            "key_data": result_analysis.get("key_data", {}),
            "category": result_analysis.get("category", "actions"),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "importance": result_analysis.get("importance", 0.5)
        }
        
        # 提取发现/决策/错误
        if result_analysis.get("discoveries"):
            memory["discoveries"] = result_analysis["discoveries"]
        if result_analysis.get("decisions"):
            memory["decisions"] = result_analysis["decisions"]
        if result_analysis.get("errors"):
            memory["errors"] = result_analysis["errors"]
            memory["category"] = "errors"
        
        # 保存重要记忆
        if memory["importance"] >= self.config.get("importance_threshold", 0.5):
            self._save_memory(memory)
            self.session_memories.append(memory)
            
            # 同时更新到MEMORY.md
            self._update_memory_md(memory)
            
            logger.info(f"保存工具结果记忆: {tool_name} [重要性: {memory['importance']:.2f}]")
        
        return None
    
    def _analyze_result(self, tool_name: str, params: Dict, result: Any) -> Dict:
        """分析工具结果，提取关键信息"""
        analysis = {
            "success": True,
            "summary": "",
            "key_data": {},
            "category": "actions",
            "importance": 0.5,
            "discoveries": [],
            "decisions": [],
            "errors": []
        }
        
        # 根据工具类型分析
        if tool_name == "web_fetch":
            analysis.update(self._analyze_web_fetch(result))
        elif tool_name in ["exec", "process"]:
            analysis.update(self._analyze_command(result))
        elif tool_name == "read":
            analysis.update(self._analyze_read(result))
        elif tool_name == "write":
            analysis.update(self._analyze_write(params, result))
        elif tool_name == "edit":
            analysis.update(self._analyze_edit(params, result))
        elif tool_name == "memory_search":
            analysis.update(self._analyze_memory_search(result))
        elif tool_name in ["feishu_task_task", "feishu_calendar_event"]:
            analysis.update(self._analyze_feishu_action(result))
        else:
            # 通用分析
            analysis.update(self._analyze_generic(result))
        
        return analysis
    
    def _analyze_web_fetch(self, result: Any) -> Dict:
        """分析web_fetch结果"""
        analysis = {"category": "discoveries", "importance": 0.6, "errors": []}
        
        if isinstance(result, dict):
            url = result.get("url", "")
            status = result.get("status", 0)
            
            if status == 200:
                analysis["summary"] = f"成功获取网页: {url}"
                analysis["success"] = True
                
                # 提取关键内容摘要
                text = result.get("text", "")
                if text:
                    # 提取前200字符作为摘要
                    analysis["key_data"] = {"summary": text[:200] + "..." if len(text) > 200 else text}
            else:
                analysis["summary"] = f"获取网页失败: {url} (状态码: {status})"
                analysis["success"] = False
                analysis["errors"].append(f"HTTP {status}")
                analysis["importance"] = 0.7
        
        return analysis
    
    def _analyze_command(self, result: Any) -> Dict:
        """分析命令执行结果"""
        analysis = {"category": "actions", "importance": 0.5, "errors": [], "key_data": {}}
        
        if isinstance(result, dict):
            exit_code = result.get("exit_code", 0)
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            
            if exit_code == 0:
                analysis["summary"] = "命令执行成功"
                analysis["success"] = True
                
                # 提取关键输出
                if stdout:
                    lines = stdout.strip().split('\n')
                    analysis["key_data"]["output_lines"] = len(lines)
                    if lines:
                        analysis["key_data"]["last_output"] = lines[-1][:100]
            else:
                analysis["summary"] = f"命令执行失败 (退出码: {exit_code})"
                analysis["success"] = False
                analysis["errors"].append(stderr[:200] if stderr else f"Exit code: {exit_code}")
                analysis["importance"] = 0.8
        
        return analysis
    
    def _analyze_read(self, result: Any) -> Dict:
        """分析文件读取结果"""
        analysis = {"category": "actions", "importance": 0.4, "key_data": {}, "errors": []}
        
        if isinstance(result, dict):
            if result.get("status") == "error":
                analysis["success"] = False
                analysis["errors"].append(result.get("error", "Unknown error"))
                analysis["importance"] = 0.6
            else:
                analysis["success"] = True
                analysis["summary"] = f"成功读取文件"
                
                # 记录文件内容摘要
                content = result.get("text", "") or result.get("content", "")
                if content:
                    analysis["key_data"]["content_length"] = len(content)
                    analysis["key_data"]["first_line"] = content.split('\n')[0][:100] if content else ""
        
        return analysis
    
    def _analyze_write(self, params: Dict, result: Any) -> Dict:
        """分析文件写入结果"""
        analysis = {"category": "actions", "importance": 0.7, "key_data": {}}
        
        path = params.get("path", "unknown")
        analysis["summary"] = f"创建/修改文件: {path}"
        analysis["success"] = True
        analysis["key_data"]["file_path"] = path
        analysis["key_data"]["content_length"] = len(params.get("content", ""))
        
        return analysis
    
    def _analyze_edit(self, params: Dict, result: Any) -> Dict:
        """分析文件编辑结果"""
        analysis = {"category": "actions", "importance": 0.7, "key_data": {}}
        
        path = params.get("path", "unknown")
        analysis["summary"] = f"编辑文件: {path}"
        analysis["success"] = True
        analysis["key_data"]["file_path"] = path
        analysis["key_data"]["edits_count"] = len(params.get("edits", []))
        
        return analysis
    
    def _analyze_memory_search(self, result: Any) -> Dict:
        """分析记忆搜索结果"""
        analysis = {"category": "actions", "importance": 0.3}
        
        if isinstance(result, dict):
            results_count = len(result.get("results", []))
            analysis["summary"] = f"记忆搜索返回 {results_count} 条结果"
            analysis["success"] = True
            analysis["key_data"]["results_count"] = results_count
        
        return analysis
    
    def _analyze_feishu_action(self, result: Any) -> Dict:
        """分析飞书操作结果"""
        analysis = {"category": "actions", "importance": 0.6}
        
        if isinstance(result, dict):
            if result.get("success") or result.get("code") == 0:
                analysis["success"] = True
                analysis["summary"] = "飞书操作成功"
            else:
                analysis["success"] = False
                analysis["errors"].append(result.get("msg", "Unknown error"))
                analysis["importance"] = 0.7
        
        return analysis
    
    def _analyze_generic(self, result: Any) -> Dict:
        """通用结果分析"""
        analysis = {"category": "actions", "importance": 0.5, "key_data": {}, "errors": []}
        
        if isinstance(result, dict):
            # 检查成功/失败状态
            if "success" in result:
                analysis["success"] = result["success"]
                if not result["success"]:
                    analysis["importance"] = 0.7
            elif "error" in result or "status" in result and result["status"] == "error":
                analysis["success"] = False
                analysis["importance"] = 0.7
            
            # 提取摘要
            for key in ["message", "summary", "text", "content"]:
                if key in result and isinstance(result[key], str):
                    analysis["summary"] = result[key][:200]
                    break
        
        return analysis
    
    def _calculate_importance(self, memory: Dict) -> float:
        """计算记忆的重要性分数 (0-1)"""
        importance = 0.5  # 基础分
        
        # 工具类型权重
        tool_weights = {
            "write": 0.8,
            "edit": 0.8,
            "delete": 0.9,
            "exec": 0.6,
            "web_fetch": 0.6,
            "create": 0.7,
            "message": 0.7
        }
        tool = memory.get("tool", "")
        importance += tool_weights.get(tool, 0.0)
        
        # 内容分析
        params_str = json.dumps(memory.get("params", {}))
        
        # 关键词加权
        important_keywords = [
            "create", "delete", "modify", "important", "critical",
            "error", "fail", "success", "complete", "discover",
            "创建", "删除", "修改", "重要", "错误", "完成", "发现"
        ]
        for keyword in important_keywords:
            if keyword.lower() in params_str.lower():
                importance += 0.1
        
        # 路径分析 - 关键文件
        critical_paths = ["config", "memory", "plan", "strategy", ".md", "README"]
        for path in critical_paths:
            if path in params_str:
                importance += 0.15
        
        return min(importance, 1.0)  # 最高1.0
    
    def _save_memory(self, memory: Dict) -> None:
        """保存记忆到文件"""
        # 按日期组织
        date_str = datetime.now().strftime("%Y-%m-%d")
        daily_file = self.memory_dir / f"memories_{date_str}.jsonl"
        
        # 追加写入
        with open(daily_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(memory, ensure_ascii=False) + '\n')
    
    def _update_memory_md(self, memory: Dict) -> None:
        """更新MEMORY.md文件"""
        memory_md_path = Path.home() / "MEMORY.md"
        
        if not memory_md_path.exists():
            return
        
        # 只更新高重要性的记忆
        if memory.get("importance", 0) < 0.8:
            return
        
        try:
            # 读取现有内容
            with open(memory_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建记忆条目
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            tool = memory.get("tool", "unknown")
            summary = memory.get("summary", "")
            category = memory.get("category", "actions")
            
            memory_entry = f"\n### [{timestamp}] {category.upper()}: {tool}\n\n{summary}\n\n"
            
            # 添加到文件末尾
            with open(memory_md_path, 'a', encoding='utf-8') as f:
                f.write(memory_entry)
            
            logger.debug(f"更新MEMORY.md: {summary[:50]}...")
            
        except Exception as e:
            logger.error(f"更新MEMORY.md失败: {e}")
    
    def _save_session_summary(self) -> None:
        """保存会话摘要"""
        if not self.session_memories:
            return
        
        summary = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "end_time": datetime.now().isoformat(),
            "total_memories": len(self.session_memories),
            "categories": {},
            "tools_used": {},
            "important_findings": []
        }
        
        # 统计分类
        for memory in self.session_memories:
            category = memory.get("category", "actions")
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            
            tool = memory.get("tool", "unknown")
            summary["tools_used"][tool] = summary["tools_used"].get(tool, 0) + 1
            
            # 收集重要发现
            if memory.get("importance", 0) >= 0.8:
                summary["important_findings"].append({
                    "tool": tool,
                    "summary": memory.get("summary", ""),
                    "category": category
                })
        
        # 保存摘要
        summary_file = self.memory_dir / f"session_{self.session_id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存会话摘要: {summary_file}")
    
    def _load_relevant_memories(self, session_info: Dict) -> None:
        """加载相关的历史记忆"""
        # 获取当前工作目录
        working_dir = session_info.get("working_dir", "")
        
        # 查找最近7天的记忆
        recent_memories = []
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for memory_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                # 从文件名提取日期
                date_str = memory_file.stem.replace("memories_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date >= cutoff_date:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                memory = json.loads(line.strip())
                                # 检查是否与当前工作目录相关
                                memory_context = memory.get("context", {})
                                if working_dir and working_dir in str(memory_context):
                                    recent_memories.append(memory)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"读取记忆文件失败: {e}")
        
        # 加载到上下文（可以供AI查询）
        if recent_memories:
            logger.info(f"加载 {len(recent_memories)} 条相关历史记忆")
            session_info["relevant_memories"] = recent_memories[:10]  # 最多10条
    
    def _cleanup_old_memories(self) -> None:
        """清理过期记忆"""
        retention_days = self.config.get("memory_retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        for memory_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                date_str = memory_file.stem.replace("memories_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    memory_file.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.error(f"清理旧记忆失败: {e}")
        
        if deleted_count > 0:
            logger.info(f"清理 {deleted_count} 个过期记忆文件")
    
    def _sanitize_params(self, params: Dict) -> Dict:
        """清理敏感参数"""
        sensitive_keys = ['api_key', 'password', 'token', 'secret', 'key', 'auth']
        sanitized = {}
        
        for key, value in params.items():
            if any(sk in key.lower() for sk in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索记忆（简单的关键词匹配）"""
        results = []
        query_lower = query.lower()
        
        # 搜索最近30天的记忆
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for memory_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                date_str = memory_file.stem.replace("memories_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date >= cutoff_date:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                memory = json.loads(line.strip())
                                memory_text = json.dumps(memory, ensure_ascii=False).lower()
                                
                                if query_lower in memory_text:
                                    results.append(memory)
                                    
                                    if len(results) >= limit:
                                        return results
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"搜索记忆失败: {e}")
        
        return results
    
    def get_session_stats(self) -> Dict:
        """获取当前会话统计"""
        return {
            "session_id": self.session_id,
            "memories_count": len(self.session_memories),
            "start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "duration_minutes": (datetime.now() - self.session_start_time).total_seconds() / 60 if self.session_start_time else 0
        }


# 插件入口点
_plugin_instance = None

def init_plugin(config_path: str = None):
    """初始化插件"""
    global _plugin_instance
    _plugin_instance = AutoMemoryPlugin(config_path)
    return _plugin_instance

def on_session_start(session_info: Dict):
    """会话开始钩子"""
    if _plugin_instance:
        _plugin_instance.on_session_start(session_info)

def on_session_end(session_info: Dict):
    """会话结束钩子"""
    if _plugin_instance:
        _plugin_instance.on_session_end(session_info)

def on_tool_call(tool_name: str, tool_params: Dict, context: Dict):
    """工具调用钩子"""
    if _plugin_instance:
        return _plugin_instance.on_tool_call(tool_name, tool_params, context)
    return None

def on_tool_result(tool_name: str, tool_params: Dict, tool_result: Any, context: Dict):
    """工具结果钩子"""
    if _plugin_instance:
        return _plugin_instance.on_tool_result(tool_name, tool_params, tool_result, context)
    return None

# 如果直接运行，进行测试
if __name__ == "__main__":
    # 测试插件
    plugin = AutoMemoryPlugin()
    
    # 模拟会话开始
    plugin.on_session_start({
        "session_id": "test_session_001",
        "working_dir": "/home/jayson2013"
    })
    
    # 模拟工具调用
    plugin.on_tool_call("write", {
        "path": "/home/jayson2013/test.txt",
        "content": "Test content"
    }, {
        "working_dir": "/home/jayson2013",
        "current_task": "testing"
    })
    
    # 模拟工具结果
    plugin.on_tool_result("write", {
        "path": "/home/jayson2013/test.txt",
        "content": "Test content"
    }, {
        "status": "success"
    }, {
        "working_dir": "/home/jayson2013"
    })
    
    # 获取统计
    stats = plugin.get_session_stats()
    print(f"会话统计: {json.dumps(stats, indent=2)}")
    
    # 模拟会话结束
    plugin.on_session_end({"session_id": "test_session_001"})
    
    print("AutoMemory插件测试完成!")