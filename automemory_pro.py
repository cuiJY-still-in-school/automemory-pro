#!/usr/bin/env python3
"""
AutoMemory Pro - 增强版自动记忆插件
核心升级：
1. 主动记忆推荐 - 根据当前任务自动推荐相关记忆
2. 任务状态追踪 - 自动追踪TODO完成情况
3. 智能工作流管理
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoMemoryPro")

# 尝试导入父类（如果在独立运行时）
try:
    from automemory import AutoMemoryPlugin
except ImportError:
    # 如果导入失败，创建一个基类占位符
    class AutoMemoryPlugin:
        def __init__(self, config_path=None):
            self.memory_dir = Path.home() / ".openclaw" / "automemory"
            self.session_memories = []
            self.session_id = None
        def on_session_start(self, session_info): pass
        def on_session_end(self, session_info): pass
        def on_tool_call(self, tool_name, tool_params, context): return None
        def on_tool_result(self, tool_name, tool_params, tool_result, context): return None
        def get_session_stats(self): return {}
        def search_memories(self, query, limit=10): return []
        def _save_memory(self, memory): pass
        def _calculate_importance(self, memory): return 0.5
        def _sanitize_params(self, params): return params
        def _generate_id(self, content): return hashlib.md5(content.encode()).hexdigest()[:16]

try:
    from smart_reminder import SmartReminder, Reminder, ReminderType, ReminderPriority
except ImportError:
    # 如果导入失败，创建占位符
    SmartReminder = None
    Reminder = None
    ReminderType = None
    ReminderPriority = None

class TaskTracker:
    """任务追踪器 - 自动追踪任务完成状态"""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.tasks_file = memory_dir / "tasks.json"
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> Dict:
        """加载任务数据"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"tasks": [], "last_updated": datetime.now().isoformat()}
    
    def _save_tasks(self):
        """保存任务数据"""
        self.tasks["last_updated"] = datetime.now().isoformat()
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def extract_tasks_from_content(self, content: str, source: str = "") -> List[Dict]:
        """从内容中提取任务"""
        tasks = []
        
        # 匹配 TODO 模式
        # - [ ] 未完成任务
        # - [x] 已完成任务
        todo_pattern = r'- \[([ x])\] (.+)'
        matches = re.findall(todo_pattern, content)
        
        for status, task_text in matches:
            task = {
                "id": hashlib.md5(f"{source}_{task_text}".encode()).hexdigest()[:12],
                "text": task_text.strip(),
                "status": "completed" if status == "x" else "pending",
                "source": source,
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
                "related_memories": []
            }
            tasks.append(task)
        
        # 匹配动作关键词
        action_patterns = [
            r'(需要|应该|计划|准备|开始)\s*(.+?)(?:\n|$)',
            r'(need to|should|plan to|prepare to)\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for _, action_text in matches:
                if len(action_text) > 10:  # 过滤太短的内容
                    task = {
                        "id": hashlib.md5(f"{source}_{action_text}".encode()).hexdigest()[:12],
                        "text": action_text.strip(),
                        "status": "pending",
                        "source": source,
                        "created_at": datetime.now().isoformat(),
                        "completed_at": None,
                        "extracted_from": "action_keyword",
                        "confidence": 0.7
                    }
                    tasks.append(task)
        
        return tasks
    
    def add_task(self, task_text: str, source: str = "", priority: str = "medium") -> str:
        """添加新任务"""
        task_id = hashlib.md5(f"{source}_{task_text}_{datetime.now()}".encode()).hexdigest()[:12]
        
        task = {
            "id": task_id,
            "text": task_text,
            "status": "pending",
            "source": source,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "related_memories": []
        }
        
        # 检查是否已存在
        existing = [t for t in self.tasks["tasks"] if t["text"] == task_text and t["status"] == "pending"]
        if not existing:
            self.tasks["tasks"].append(task)
            self._save_tasks()
            logger.info(f"添加新任务: {task_text[:50]}...")
        
        return task_id
    
    def mark_completed(self, task_text: str = None, task_id: str = None, memory_id: str = None):
        """标记任务完成"""
        for task in self.tasks["tasks"]:
            if task["status"] == "pending":
                # 通过ID匹配
                if task_id and task["id"] == task_id:
                    task["status"] = "completed"
                    task["completed_at"] = datetime.now().isoformat()
                    if memory_id:
                        task["related_memories"].append(memory_id)
                    logger.info(f"完成任务: {task['text'][:50]}...")
                    break
                # 通过文本匹配
                elif task_text and task_text.lower() in task["text"].lower():
                    task["status"] = "completed"
                    task["completed_at"] = datetime.now().isoformat()
                    if memory_id:
                        task["related_memories"].append(memory_id)
                    logger.info(f"完成任务: {task['text'][:50]}...")
                    break
        
        self._save_tasks()
    
    def check_task_completion(self, memory: Dict) -> List[str]:
        """检查是否有任务被完成"""
        completed_tasks = []
        tool = memory.get("tool", "")
        summary = memory.get("summary", "")
        
        for task in self.tasks["tasks"]:
            if task["status"] == "pending":
                # 检查记忆是否完成任务
                task_text = task["text"].lower()
                
                # 创建文件类任务
                if "创建" in task_text or "create" in task_text:
                    if tool in ["write", "edit"] and task_text in summary.lower():
                        self.mark_completed(task_id=task["id"], memory_id=memory.get("id"))
                        completed_tasks.append(task["text"])
                
                # 执行命令类任务
                elif "执行" in task_text or "run" in task_text or "setup" in task_text:
                    if tool == "exec" and any(kw in summary.lower() for kw in ["成功", "完成", "success"]):
                        # 进一步检查相关性
                        self.mark_completed(task_id=task["id"], memory_id=memory.get("id"))
                        completed_tasks.append(task["text"])
                
                # 检查类任务
                elif "检查" in task_text or "查看" in task_text:
                    if tool in ["read", "exec"] and "成功" in summary:
                        self.mark_completed(task_id=task["id"], memory_id=memory.get("id"))
                        completed_tasks.append(task["text"])
        
        return completed_tasks
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict]:
        """获取未完成任务"""
        pending = [t for t in self.tasks["tasks"] if t["status"] == "pending"]
        
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
        
        return pending[:limit]
    
    def get_task_summary(self) -> Dict:
        """获取任务摘要"""
        total = len(self.tasks["tasks"])
        pending = len([t for t in self.tasks["tasks"] if t["status"] == "pending"])
        completed = len([t for t in self.tasks["tasks"] if t["status"] == "completed"])
        
        # 检查逾期任务（创建超过3天未完成）
        overdue = 0
        for task in self.tasks["tasks"]:
            if task["status"] == "pending":
                created = datetime.fromisoformat(task["created_at"])
                if datetime.now() - created > timedelta(days=3):
                    overdue += 1
        
        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": completed / total if total > 0 else 0
        }


class MemoryRecommender:
    """记忆推荐器 - 根据当前任务推荐相关记忆"""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.keyword_index = self._build_keyword_index()
    
    def _build_keyword_index(self) -> Dict[str, List[str]]:
        """构建关键词索引"""
        index = defaultdict(list)
        
        for memory_file in self.memory_dir.glob("memories_*.jsonl"):
            with open(memory_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        memory = json.loads(line.strip())
                        memory_id = memory.get("id", "")
                        
                        # 提取关键词
                        text = f"{memory.get('tool', '')} {memory.get('summary', '')}"
                        text += f" {json.dumps(memory.get('key_data', {}))}"
                        
                        # 简单分词（可以优化为更好的NLP）
                        keywords = self._extract_keywords(text)
                        
                        for keyword in keywords:
                            index[keyword].append(memory_id)
                    except:
                        pass
        
        return index
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 提取重要词汇
        words = re.findall(r'\b[A-Za-z_]{3,}\b|\b[\u4e00-\u9fa5]{2,}\b', text)
        
        # 过滤停用词
        stopwords = {"the", "and", "for", "with", "from", "this", "that", "成功", "失败"}
        keywords = [w.lower() for w in words if w.lower() not in stopwords and len(w) > 2]
        
        return list(set(keywords))[:10]  # 限制数量
    
    def recommend_for_task(self, task_description: str, current_context: Dict = None, limit: int = 5) -> List[Dict]:
        """为当前任务推荐相关记忆"""
        
        # 提取任务关键词
        task_keywords = self._extract_keywords(task_description)
        
        # 找到相关记忆ID
        related_ids = set()
        for keyword in task_keywords:
            if keyword in self.keyword_index:
                related_ids.update(self.keyword_index[keyword])
        
        # 加载完整记忆
        related_memories = []
        for memory_file in self.memory_dir.glob("memories_*.jsonl"):
            with open(memory_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        memory = json.loads(line.strip())
                        if memory.get("id") in related_ids:
                            # 计算相关性分数
                            relevance = self._calculate_relevance(memory, task_keywords, current_context)
                            memory["relevance_score"] = relevance
                            related_memories.append(memory)
                    except:
                        pass
        
        # 排序并返回
        related_memories.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return related_memories[:limit]
    
    def _calculate_relevance(self, memory: Dict, task_keywords: List[str], context: Dict = None) -> float:
        """计算记忆与当前任务的相关性"""
        score = 0.0
        
        # 关键词匹配
        memory_text = f"{memory.get('tool', '')} {memory.get('summary', '')}"
        memory_keywords = self._extract_keywords(memory_text)
        
        common_keywords = set(task_keywords) & set(memory_keywords)
        score += len(common_keywords) * 0.3
        
        # 时效性加分（越新的记忆越相关）
        try:
            timestamp = datetime.fromisoformat(memory.get("timestamp", ""))
            days_ago = (datetime.now() - timestamp).days
            if days_ago < 1:
                score += 0.5  # 今天的记忆
            elif days_ago < 7:
                score += 0.3  # 本周的记忆
            elif days_ago < 30:
                score += 0.1  # 本月的记忆
        except:
            pass
        
        # 重要性加权
        importance = memory.get("importance", 0.5)
        score += importance * 0.2
        
        # 上下文匹配
        if context:
            working_dir = context.get("working_dir", "")
            if working_dir and working_dir in str(memory.get("context", {})):
                score += 0.3
        
        # 失败记忆降权（除非任务也是解决错误）
        if not memory.get("success", True) and "error" not in " ".join(task_keywords):
            score *= 0.5
        
        return min(score, 2.0)  # 最高2.0
    
    def get_recent_context(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """获取近期上下文"""
        recent = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for memory_file in sorted(self.memory_dir.glob("memories_*.jsonl"), reverse=True):
            with open(memory_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        memory = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(memory.get("timestamp", ""))
                        if timestamp > cutoff:
                            recent.append(memory)
                    except:
                        pass
        
        # 按时间排序
        recent.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return recent[:limit]


class AutoMemoryPro(AutoMemoryPlugin):
    """增强版AutoMemory插件"""
    
    def __init__(self, config_path: str = None):
        # 先初始化父类
        super().__init__(config_path)
        
        # 初始化新功能
        self.task_tracker = TaskTracker(self.memory_dir)
        self.memory_recommender = MemoryRecommender(self.memory_dir)
        
        # 初始化智能提醒系统
        if SmartReminder:
            self.smart_reminder = SmartReminder(str(self.memory_dir))
        else:
            self.smart_reminder = None
        
        logger.info("AutoMemory Pro 初始化完成")
    
    def on_session_start(self, session_info: Dict) -> List[Dict]:
        """会话开始时的处理 - 返回推荐的记忆"""
        super().on_session_start(session_info)
        
        recommendations = []
        
        # 1. 获取当前任务描述
        current_task = session_info.get("current_task", "")
        
        if current_task:
            # 2. 推荐相关记忆
            recommendations = self.memory_recommender.recommend_for_task(
                current_task,
                session_info,
                limit=5
            )
            
            if recommendations:
                logger.info(f"为任务 '{current_task[:50]}...' 推荐 {len(recommendations)} 条记忆")
        
        # 3. 获取待完成任务提醒
        pending_tasks = self.task_tracker.get_pending_tasks(limit=5)
        
        # 4. 检查是否有逾期的任务
        summary = self.task_tracker.get_task_summary()
        if summary["overdue"] > 0:
            logger.warning(f"有 {summary['overdue']} 个任务已逾期！")
        
        # 返回推荐结果
        session_info["recommended_memories"] = recommendations
        session_info["pending_tasks"] = pending_tasks
        session_info["task_summary"] = summary
        
        return recommendations
    
    def on_tool_result(self, tool_name: str, tool_params: Dict, 
                       tool_result: Any, context: Dict) -> Optional[Dict]:
        """工具返回结果时的处理 - 增强版"""
        
        # 调用父类方法保存记忆
        result = super().on_tool_result(tool_name, tool_params, tool_result, context)
        
        # 获取刚保存的记忆（最后一条）
        if self.session_memories:
            latest_memory = self.session_memories[-1]
            
            # 1. 检查是否完成任务
            completed_tasks = self.task_tracker.check_task_completion(latest_memory)
            if completed_tasks:
                logger.info(f"通过此操作完成 {len(completed_tasks)} 个任务: {completed_tasks}")
                latest_memory["completed_tasks"] = completed_tasks
            
            # 2. 从结果中提取新任务
            if isinstance(tool_result, dict):
                text_content = tool_result.get("text", "") or tool_result.get("content", "")
                if text_content:
                    new_tasks = self.task_tracker.extract_tasks_from_content(
                        text_content,
                        source=f"{tool_name}_result"
                    )
                    for task in new_tasks:
                        self.task_tracker.add_task(task["text"], source=task["source"])
        
        return result
    
    def get_work_summary(self) -> Dict:
        """获取工作摘要 - 用于每日总结"""
        # 获取基础统计
        stats = self.get_session_stats()
        task_summary = self.task_tracker.get_task_summary()
        
        # 获取今日高价值记忆
        today_memories = []
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        for m in self.session_memories:
            if m.get("timestamp", "").startswith(today_str):
                today_memories.append(m)
        
        high_value = [m for m in today_memories if m.get("importance", 0) >= 0.8]
        errors = [m for m in today_memories if not m.get("success", True)]
        
        # 生成摘要文本
        summary_text = f"""
📅 {datetime.now().strftime('%Y-%m-%d')} 工作摘要
=====================================

今日完成：
- 记录记忆: {len(today_memories)} 条
- 高价值操作: {len(high_value)} 条
- 遇到问题: {len(errors)} 个

任务状态：
- 总任务: {task_summary['total']}
- 已完成: {task_summary['completed']} ({task_summary['completion_rate']*100:.1f}%)
- 待完成: {task_summary['pending']}
- 已逾期: {task_summary['overdue']}

待办提醒：
"""
        
        # 添加待完成任务
        pending = self.task_tracker.get_pending_tasks(limit=5)
        for i, task in enumerate(pending, 1):
            created = datetime.fromisoformat(task["created_at"])
            days_ago = (datetime.now() - created).days
            overdue_mark = "⚠️ " if days_ago > 3 else ""
            summary_text += f"{i}. {overdue_mark}{task['text'][:50]}... ({days_ago}天前)\n"
        
        if not pending:
            summary_text += "✅ 所有任务已完成！\n"
        
        summary_text += "\n建议：\n"
        if task_summary["overdue"] > 0:
            summary_text += f"⚠️  有{task_summary['overdue']}个任务已逾期，建议优先处理\n"
        if pending:
            summary_text += f"⏳ 还有{len(pending)}个任务待完成，加油！\n"
        
        return {
            "stats": stats,
            "task_summary": task_summary,
            "today_memories": today_memories,
            "high_value_memories": high_value,
            "errors": errors,
            "summary_text": summary_text,
            "pending_tasks": pending
        }
    
    def check_reminders(self, current_tool: str = None) -> Dict[str, List[Reminder]]:
        """检查所有智能提醒 - 整合到工作流中"""
        if not self.smart_reminder:
            return {}
        
        # 统计最近完成的任务
        recent_completed = len([m for m in self.session_memories 
                               if m.get('completed_tasks')])
        
        # 收集最近的错误
        recent_errors = [m for m in self.session_memories 
                        if not m.get('success', True)]
        error_dicts = [{"type": m.get('tool', 'unknown'), "message": m.get('summary', '')}
                      for m in recent_errors]
        
        # 检查所有提醒
        reminders = self.smart_reminder.check_all_reminders(
            recent_completed=recent_completed,
            recent_errors=error_dicts,
            current_tool=current_tool,
            context={"session_id": self.session_id}
        )
        
        return reminders
    
    def get_reminder_summary(self) -> str:
        """获取提醒摘要文本"""
        if not self.smart_reminder:
            return "智能提醒系统未安装"
        
        reminders = self.check_reminders()
        return self.smart_reminder.get_reminder_summary(reminders)
    
    def add_routine_reminder(self, title: str, time: str, description: str = "",
                           days: List[str] = None) -> str:
        """添加定期提醒"""
        if not self.smart_reminder:
            return ""
        return self.smart_reminder.add_routine_task(
            title=title,
            time=time,
            description=description,
            days=days
        )
    
    def add_context_tip(self, trigger: str, tip: str, tool: str = None,
                       severity: str = "info") -> None:
        """添加上下文提示"""
        if self.smart_reminder:
            self.smart_reminder.add_context_tip(
                trigger=trigger,
                tip=tip,
                tool=tool,
                severity=severity
            )
    
    def search_and_recommend(self, query: str, context: Dict = None, limit: int = 5) -> Dict:
        """搜索并推荐记忆"""
        # 直接搜索
        search_results = self.search_memories(query, limit=limit)
        
        # 推荐相关记忆
        recommendations = self.memory_recommender.recommend_for_task(
            query, context, limit=limit
        )
        
        # 合并去重
        seen_ids = set()
        combined = []
        
        for m in recommendations + search_results:
            mid = m.get("id")
            if mid and mid not in seen_ids:
                seen_ids.add(mid)
                combined.append(m)
        
        return {
            "search_results": search_results,
            "recommendations": recommendations,
            "combined": combined[:limit],
            "total_found": len(combined)
        }


# 测试代码
if __name__ == "__main__":
    # 导入父类
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from automemory import AutoMemoryPlugin
    
    print("🚀 AutoMemory Pro 测试")
    print("=" * 60)
    
    # 初始化
    plugin = AutoMemoryPro()
    
    # 模拟会话开始
    print("\n1️⃣  会话开始 - 任务：'继续monetization项目'")
    session_info = {
        "session_id": "test_pro_001",
        "working_dir": "/home/jayson2013",
        "current_task": "继续monetization项目，推进Fiverr设置"
    }
    
    recommendations = plugin.on_session_start(session_info)
    print(f"   💡 自动推荐 {len(recommendations)} 条相关记忆")
    for i, m in enumerate(recommendations[:3], 1):
        print(f"   {i}. [{m.get('relevance_score', 0):.2f}] {m.get('tool')}: {m.get('summary', '')[:40]}...")
    
    # 检查任务状态
    print(f"\n2️⃣  待完成任务：{len(session_info.get('pending_tasks', []))} 个")
    for task in session_info.get('pending_tasks', [])[:3]:
        print(f"   ⏳ {task['text'][:50]}...")
    
    # 执行任务并追踪
    print("\n3️⃣  执行任务：创建Fiverr账号")
    plugin.on_tool_call("exec", {
        "command": "echo 'Fiverr account created'"
    }, {
        "working_dir": "/home/jayson2013",
        "current_task": "Setup Fiverr"
    })
    
    plugin.on_tool_result("exec", {
        "command": "setup fiverr"
    }, {
        "status": "success",
        "message": "Fiverr account created successfully"
    }, {
        "working_dir": "/home/jayson2013"
    })
    
    # 获取工作摘要
    print("\n4️⃣  生成工作摘要")
    summary = plugin.get_work_summary()
    print(summary["summary_text"])
    
    # 结束会话
    plugin.on_session_end({"session_id": "test_pro_001"})
    
    print("\n✅ AutoMemory Pro 测试完成！")
    print("核心升级：")
    print("  ✓ 主动记忆推荐 - 自动找到相关记忆")
    print("  ✓ 任务状态追踪 - 自动追踪TODO完成情况")
    print("  ✓ 工作摘要生成 - 每日自动总结")