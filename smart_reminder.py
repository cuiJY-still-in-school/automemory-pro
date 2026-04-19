#!/usr/bin/env python3
"""
AutoMemory Pro - 智能提醒系统
Smart Reminder System

核心功能：
1. 逾期任务提醒 - 有任务过期了？
2. 定期任务提醒 - 每天/每周固定时间该做什么
3. 上下文提醒 - 根据当前操作自动提示相关注意事项
4. 成就提醒 - 完成任务后给予正向激励
5. 模式提醒 - 发现常见错误模式时提醒

作者: ClawQuant
日期: 2026-04-19
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartReminder")

# ============================================================================
# 数据结构
# ============================================================================

class ReminderType(Enum):
    """提醒类型"""
    OVERDUE = "overdue"              # 逾期任务
    ROUTINE = "routine"              # 定期任务
    CONTEXT = "context"               # 上下文提醒
    ACHIEVEMENT = "achievement"      # 成就提醒
    PATTERN = "pattern"              # 模式提醒
    SUGGESTION = "suggestion"        # 建议提醒

class ReminderPriority(Enum):
    """优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Reminder:
    """提醒数据模型"""
    id: str
    type: ReminderType
    priority: ReminderPriority
    title: str
    message: str
    created_at: str
    action_url: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'Reminder':
        data['type'] = ReminderType(data['type'])
        data['priority'] = ReminderPriority(data['priority'])
        return Reminder(**data)

@dataclass
class Task:
    """任务数据模型"""
    id: str
    title: str
    description: str
    status: str  # pending, completed, overdue
    due_date: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    tags: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        return Task(**data)

# ============================================================================
# 智能提醒系统核心
# ============================================================================

class SmartReminder:
    """
    智能提醒系统
    
    使用示例:
    ```python
    from smart_reminder import SmartReminder
    
    reminder = SmartReminder()
    
    # 检查所有提醒
    reminders = reminder.check_all_reminders()
    for r in reminders:
        print(f"[{r.priority.value.upper()}] {r.title}")
        print(f"   {r.message}")
    
    # 添加定期任务
    reminder.add_routine_task(
        title="每天检查Signal Arena",
        time="09:00",
        days=["Mon", "Tue", "Wed", "Thu", "Fri"]
    )
    
    # 上下文提醒
    reminder.add_context_tip(
        trigger="exec",
        tip="执行命令前注意检查路径和权限"
    )
    ```
    """
    
    def __init__(self, memory_dir: str = None):
        """
        初始化智能提醒系统
        
        Args:
            memory_dir: 记忆目录路径，默认 ~/.openclaw/automemory
        """
        if memory_dir is None:
            memory_dir = Path.home() / ".openclaw" / "automemory"
        else:
            memory_dir = Path(memory_dir)
        
        self.memory_dir = memory_dir
        self.reminder_dir = memory_dir / "reminders"
        self.reminder_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.routine_file = self.reminder_dir / "routine_tasks.json"
        self.context_tips_file = self.reminder_dir / "context_tips.json"
        self.achievements_file = self.reminder_dir / "achievements.json"
        self.patterns_file = self.reminder_dir / "patterns.json"
        self.history_file = self.reminder_dir / "reminder_history.json"
        
        # 初始化数据文件
        self._init_data_files()
        
        logger.info(f"智能提醒系统初始化完成，数据目录: {self.reminder_dir}")
    
    def _init_data_files(self):
        """初始化数据文件"""
        # 定期任务
        if not self.routine_file.exists():
            self._save_json(self.routine_file, {"routine_tasks": []})
        
        # 上下文提示
        if not self.context_tips_file.exists():
            self._save_json(self.context_tips_file, {
                "context_tips": [
                    {
                        "trigger": "exec",
                        "tool": "command",
                        "tip": "执行命令前注意检查路径和权限，特别是 rm、chmod 等危险操作",
                        "severity": "warning"
                    },
                    {
                        "trigger": "exec",
                        "tool": "pip",
                        "tip": "建议使用 uv 代替 pip，uv 更快更安全",
                        "severity": "info"
                    },
                    {
                        "trigger": "write",
                        "tip": "写入文件前确认路径正确，避免覆盖重要文件",
                        "severity": "warning"
                    },
                    {
                        "trigger": "browser",
                        "tip": "浏览器操作会留下痕迹，注意隐私保护",
                        "severity": "info"
                    }
                ]
            })
        
        # 成就系统
        if not self.achievements_file.exists():
            self._save_json(self.achievements_file, {
                "achievements": [],
                "stats": {
                    "total_completed": 0,
                    "streak_days": 0,
                    "last_active": None,
                    "max_streak": 0
                }
            })
        
        # 错误模式
        if not self.patterns_file.exists():
            self._save_json(self.patterns_file, {
                "patterns": [],
                "common_errors": []
            })
        
        # 历史记录
        if not self.history_file.exists():
            self._save_json(self.history_file, {"history": []})
    
    def _save_json(self, filepath: Path, data: Dict):
        """保存JSON数据"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_json(self, filepath: Path) -> Dict:
        """加载JSON数据"""
        if not filepath.exists():
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # =========================================================================
    # 逾期任务提醒
    # =========================================================================
    
    def check_overdue_tasks(self) -> List[Reminder]:
        """
        检查逾期任务
        
        Returns:
            逾期任务提醒列表
        """
        reminders = []
        
        # 从记忆目录加载任务
        tasks = self._load_tasks_from_memory()
        
        now = datetime.now()
        
        for task in tasks:
            if task.get('status') == 'pending' and task.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(task['due_date'])
                    if due_date < now:
                        # 计算逾期天数
                        overdue_days = (now - due_date).days
                        
                        # 根据逾期天数确定优先级
                        if overdue_days >= 7:
                            priority = ReminderPriority.URGENT
                        elif overdue_days >= 3:
                            priority = ReminderPriority.HIGH
                        else:
                            priority = ReminderPriority.MEDIUM
                        
                        reminders.append(Reminder(
                            id=f"overdue_{task['id']}",
                            type=ReminderType.OVERDUE,
                            priority=priority,
                            title=f"任务已逾期 {overdue_days} 天",
                            message=f"「{task.get('title', '未知任务')}」已逾期 {overdue_days} 天了，建议尽快处理。",
                            created_at=now.isoformat(),
                            metadata={
                                "task_id": task['id'],
                                "overdue_days": overdue_days,
                                "original_due": task['due_date']
                            }
                        ))
                except (ValueError, TypeError):
                    continue
        
        # 按优先级排序
        priority_order = {
            ReminderPriority.URGENT: 0,
            ReminderPriority.HIGH: 1,
            ReminderPriority.MEDIUM: 2,
            ReminderPriority.LOW: 3
        }
        reminders.sort(key=lambda x: priority_order[x.priority])
        
        return reminders
    
    def _load_tasks_from_memory(self) -> List[Dict]:
        """从记忆文件加载任务"""
        tasks = []
        
        # 加载 tasks.json
        tasks_file = self.memory_dir / "tasks.json"
        if tasks_file.exists():
            data = self._load_json(tasks_file)
            tasks.extend(data.get('tasks', []))
        
        # 从每日记忆文件中提取任务
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        memory = json.loads(line.strip())
                        # 从记忆中提取TODO
                        if 'tasks' in memory:
                            tasks.extend(memory['tasks'])
                    except:
                        continue
        
        return tasks
    
    # =========================================================================
    # 定期任务提醒
    # =========================================================================
    
    def check_routine_tasks(self) -> List[Reminder]:
        """
        检查定期任务
        
        Returns:
            需要执行的定期任务提醒
        """
        reminders = []
        now = datetime.now()
        
        data = self._load_json(self.routine_file)
        routine_tasks = data.get('routine_tasks', [])
        
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a")
        current_weekday = now.weekday()  # 0=Monday
        
        for task in routine_tasks:
            if not task.get('enabled', True):
                continue
            
            # 检查时间
            if task.get('time') != current_time:
                continue
            
            # 检查日期
            days = task.get('days', [])
            if days:
                # 支持中文或英文
                day_map = {
                    'Mon': 0, 'Monday': 0, '周一': 0, '星期一': 0,
                    'Tue': 1, 'Tuesday': 1, '周二': 1, '星期二': 1,
                    'Wed': 2, 'Wednesday': 2, '周三': 2, '星期二': 2,
                    'Thu': 3, 'Thursday': 3, '周四': 3, '星期四': 3,
                    'Fri': 4, 'Friday': 4, '周五': 4, '星期五': 4,
                    'Sat': 5, 'Saturday': 5, '周六': 5, '星期六': 5,
                    'Sun': 6, 'Sunday': 6, '周日': 6, '星期日': 6,
                }
                
                valid_days = []
                for d in days:
                    d_normalized = day_map.get(d, d)
                    if isinstance(d_normalized, int):
                        valid_days.append(d_normalized)
                
                if current_weekday not in valid_days:
                    continue
            
            # 检查是否已提醒过
            last_reminded = task.get('last_reminded')
            if last_reminded:
                last_date = datetime.fromisoformat(last_reminded[:10])
                if last_date.date() == now.date():
                    continue  # 今天已提醒
            
            reminders.append(Reminder(
                id=f"routine_{task['id']}",
                type=ReminderType.ROUTINE,
                priority=ReminderPriority.MEDIUM,
                title=f"📅 {task.get('title', '定期任务')}",
                message=task.get('description', f"该执行「{task.get('title')}」了"),
                created_at=now.isoformat(),
                metadata={
                    "task_id": task['id'],
                    "routine_type": task.get('type', 'daily')
                }
            ))
        
        return reminders
    
    def add_routine_task(
        self,
        title: str,
        time: str,
        description: str = "",
        days: List[str] = None,
        task_type: str = "daily"
    ) -> str:
        """
        添加定期任务
        
        Args:
            title: 任务标题
            time: 执行时间 (HH:MM)
            description: 任务描述
            days: 执行日期列表 ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            task_type: 任务类型 (daily, weekly, custom)
        
        Returns:
            任务ID
        """
        if days is None:
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        
        task_id = f"routine_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        task = {
            "id": task_id,
            "title": title,
            "time": time,
            "description": description,
            "days": days,
            "type": task_type,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_reminded": None
        }
        
        data = self._load_json(self.routine_file)
        data['routine_tasks'].append(task)
        self._save_json(self.routine_file, data)
        
        logger.info(f"添加定期任务: {title} @ {time}")
        return task_id
    
    def complete_routine_task(self, task_id: str):
        """标记定期任务为已完成"""
        data = self._load_json(self.routine_file)
        
        for task in data['routine_tasks']:
            if task['id'] == task_id:
                task['last_reminded'] = datetime.now().isoformat()
                break
        
        self._save_json(self.routine_file, data)
        logger.info(f"定期任务完成: {task_id}")
    
    # =========================================================================
    # 上下文提醒
    # =========================================================================
    
    def check_context_tips(self, tool_name: str = None, context: Dict = None) -> List[Reminder]:
        """
        检查上下文相关的提示
        
        Args:
            tool_name: 当前执行的工具名称
            context: 上下文信息
        
        Returns:
            上下文提醒列表
        """
        if tool_name is None:
            return []
        
        reminders = []
        now = datetime.now()
        
        data = self._load_json(self.context_tips_file)
        tips = data.get('context_tips', [])
        
        for tip in tips:
            # 检查触发条件
            if tip.get('tool') and tip['tool'] != tool_name:
                continue
            
            # 检查是否已显示过（短时间内）
            tip_id = f"context_{tool_name}_{tip.get('trigger', 'general')}"
            if self._was_recently_shown(tip_id):
                continue
            
            # severity 映射到 ReminderPriority
            severity_map = {
                'info': ReminderPriority.LOW,
                'warning': ReminderPriority.MEDIUM,
                'error': ReminderPriority.HIGH,
                'urgent': ReminderPriority.URGENT
            }
            severity = severity_map.get(tip.get('severity', 'info'), ReminderPriority.LOW)
            
            reminders.append(Reminder(
                id=tip_id,
                type=ReminderType.CONTEXT,
                priority=severity,
                title=f"💡 {tip.get('title', '提示')}",
                message=tip.get('tip', ''),
                created_at=now.isoformat(),
                metadata={"tool": tool_name}
            ))
        
        return reminders[:3]  # 最多返回3条
    
    def _was_recently_shown(self, tip_id: str, minutes: int = 30) -> bool:
        """检查提示是否在最近N分钟内显示过"""
        history_data = self._load_json(self.history_file)
        
        cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        
        for item in history_data.get('history', []):
            if item.get('id') == tip_id and item.get('shown_at', '') > cutoff:
                return True
        
        return False
    
    def add_context_tip(
        self,
        trigger: str,
        tip: str,
        tool: str = None,
        severity: str = "info",
        title: str = None
    ):
        """
        添加上下文提示
        
        Args:
            trigger: 触发关键词
            tip: 提示内容
            tool: 触发工具 (exec, write, browser等)
            severity: 严重程度 (info, warning, error)
            title: 提示标题
        """
        tip_entry = {
            "id": f"tip_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "trigger": trigger,
            "tip": tip,
            "tool": tool,
            "severity": severity,
            "title": title or trigger.capitalize(),
            "created_at": datetime.now().isoformat()
        }
        
        data = self._load_json(self.context_tips_file)
        data['context_tips'].append(tip_entry)
        self._save_json(self.context_tips_file, data)
        
        logger.info(f"添加上下文提示: {tip[:50]}...")
    
    # =========================================================================
    # 成就提醒
    # =========================================================================
    
    def check_achievements(self, recent_completed: int = 0) -> List[Reminder]:
        """
        检查成就解锁情况
        
        Args:
            recent_completed: 最近完成的任务数
        
        Returns:
            新成就提醒
        """
        reminders = []
        now = datetime.now()
        
        data = self._load_json(self.achievements_file)
        achievements = data.get('achievements', [])
        stats = data.get('stats', {})
        earned_ids = {a['id'] for a in achievements}
        
        # 成就定义
        achievement_defs = [
            {
                "id": "first_task",
                "name": "🎯 初试牛刀",
                "desc": "完成第一个任务",
                "condition": lambda s: s.get('total_completed', 0) >= 1
            },
            {
                "id": "five_tasks",
                "name": "🔥 五福临门",
                "desc": "累计完成5个任务",
                "condition": lambda s: s.get('total_completed', 0) >= 5
            },
            {
                "id": "ten_tasks",
                "name": "⭐ 十全十美",
                "desc": "累计完成10个任务",
                "condition": lambda s: s.get('total_completed', 0) >= 10
            },
            {
                "id": "streak_3",
                "name": "📅 三日连击",
                "desc": "连续3天活跃",
                "condition": lambda s: s.get('streak_days', 0) >= 3
            },
            {
                "id": "streak_7",
                "name": "🧠 周周不休",
                "desc": "连续7天活跃",
                "condition": lambda s: s.get('streak_days', 0) >= 7
            },
            {
                "id": "streak_30",
                "name": "💎 月度达人",
                "desc": "连续30天活跃",
                "condition": lambda s: s.get('streak_days', 0) >= 30
            },
            {
                "id": "efficient_5",
                "name": "⚡ 效率达人",
                "desc": "一天内完成5个任务",
                "condition": lambda s: recent_completed >= 5
            },
            {
                "id": "productive_day",
                "name": "🚀 高效一天",
                "desc": "一天内完成10个任务",
                "condition": lambda s: recent_completed >= 10
            }
        ]
        
        # 检查新成就
        for defn in achievement_defs:
            if defn['id'] not in earned_ids and defn['condition'](stats):
                reminder = Reminder(
                    id=f"achievement_{defn['id']}",
                    type=ReminderType.ACHIEVEMENT,
                    priority=ReminderPriority.LOW,
                    title=f"🏆 新成就解锁: {defn['name']}",
                    message=f"恭喜！{defn['desc']}",
                    created_at=now.isoformat(),
                    metadata={"achievement_id": defn['id']}
                )
                reminders.append(reminder)
                
                # 保存成就
                achievements.append({
                    "id": defn['id'],
                    "name": defn['name'],
                    "earned_at": now.isoformat()
                })
        
        # 更新统计数据
        stats['total_completed'] = stats.get('total_completed', 0) + recent_completed
        
        # 更新连续活跃天数
        last_active = stats.get('last_active')
        if last_active:
            last_date = datetime.fromisoformat(last_active[:10])
            if (now - last_date).days == 1:
                stats['streak_days'] = stats.get('streak_days', 0) + 1
            elif (now - last_date).days > 1:
                stats['streak_days'] = 1
        else:
            stats['streak_days'] = 1
        
        if stats.get('streak_days', 0) > stats.get('max_streak', 0):
            stats['max_streak'] = stats['streak_days']
        
        stats['last_active'] = now.isoformat()
        
        data['achievements'] = achievements
        data['stats'] = stats
        self._save_json(self.achievements_file, data)
        
        return reminders
    
    def get_achievement_stats(self) -> Dict:
        """获取成就统计数据"""
        data = self._load_json(self.achievements_file)
        return {
            "total_achievements": len(data.get('achievements', [])),
            "achievements": data.get('achievements', []),
            "stats": data.get('stats', {})
        }
    
    # =========================================================================
    # 模式提醒
    # =========================================================================
    
    def check_error_patterns(self, recent_errors: List[Dict] = None) -> List[Reminder]:
        """
        检查错误模式
        
        Args:
            recent_errors: 最近犯的错误列表
        
        Returns:
            模式提醒
        """
        if recent_errors is None:
            recent_errors = []
        
        reminders = []
        now = datetime.now()
        
        # 加载已知模式
        data = self._load_json(self.patterns_file)
        patterns = data.get('patterns', [])
        
        # 分析最近错误
        error_types = {}
        for error in recent_errors:
            error_type = error.get('type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # 检查常见错误
        common_errors = data.get('common_errors', [])
        
        for error_type, count in error_types.items():
            if count >= 3:
                # 同样的错误犯了3次以上
                reminder = Reminder(
                    id=f"pattern_{error_type}",
                    type=ReminderType.PATTERN,
                    priority=ReminderPriority.HIGH,
                    title=f"⚠️ 发现错误模式: {error_type}",
                    message=f"你最近犯了 {count} 次同样的错误（{error_type}）。"
                            f"建议检查根本原因，避免再次出错。",
                    created_at=now.isoformat(),
                    metadata={"error_type": error_type, "count": count}
                )
                reminders.append(reminder)
                
                # 添加到已知模式
                if error_type not in common_errors:
                    common_errors.append(error_type)
        
        # 保存更新
        data['common_errors'] = common_errors
        self._save_json(self.patterns_file, data)
        
        return reminders
    
    def add_pattern(self, pattern: str, description: str = ""):
        """添加已知错误模式"""
        data = self._load_json(self.patterns_file)
        
        pattern_entry = {
            "id": f"pattern_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "pattern": pattern,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        data['patterns'].append(pattern_entry)
        self._save_json(self.patterns_file, data)
        
        logger.info(f"添加错误模式: {pattern}")
    
    # =========================================================================
    # 综合检查
    # =========================================================================
    
    def check_all_reminders(
        self,
        recent_completed: int = 0,
        recent_errors: List[Dict] = None,
        current_tool: str = None,
        context: Dict = None
    ) -> Dict[str, List[Reminder]]:
        """
        检查所有类型的提醒
        
        Args:
            recent_completed: 最近完成的任务数
            recent_errors: 最近犯的错误
            current_tool: 当前执行的工具
            context: 上下文信息
        
        Returns:
            按类型分类的提醒字典
        """
        all_reminders = {
            "overdue": self.check_overdue_tasks(),
            "routine": self.check_routine_tasks(),
            "context": self.check_context_tips(current_tool, context),
            "achievement": self.check_achievements(recent_completed),
            "pattern": self.check_error_patterns(recent_errors)
        }
        
        # 记录历史
        self._save_reminder_history(all_reminders)
        
        return all_reminders
    
    def _save_reminder_history(self, reminders: Dict[str, List[Reminder]]):
        """保存提醒历史"""
        data = self._load_json(self.history_file)
        
        for reminder_list in reminders.values():
            for reminder in reminder_list:
                data['history'].append({
                    "id": reminder.id,
                    "type": reminder.type.value,
                    "shown_at": datetime.now().isoformat()
                })
        
        # 只保留最近1000条
        data['history'] = data['history'][-1000:]
        
        self._save_json(self.history_file, data)
    
    def get_reminder_summary(self, reminders: Dict[str, List[Reminder]]) -> str:
        """
        生成提醒摘要文本
        
        Args:
            reminders: check_all_reminders 返回的结果
        
        Returns:
            格式化的提醒摘要
        """
        lines = []
        lines.append("=" * 50)
        lines.append("🔔 智能提醒摘要")
        lines.append("=" * 50)
        
        total = sum(len(v) for v in reminders.values())
        
        if total == 0:
            lines.append("")
            lines.append("✅ 暂无提醒，一切顺利！")
        else:
            lines.append(f"📊 共 {total} 条提醒")
            lines.append("")
            
            if reminders.get('overdue'):
                lines.append(f"⚠️  逾期任务: {len(reminders['overdue'])} 条")
                for r in reminders['overdue'][:3]:
                    lines.append(f"   • {r.title}")
                    lines.append(f"     {r.message}")
                lines.append("")
            
            if reminders.get('routine'):
                lines.append(f"📅 定期任务: {len(reminders['routine'])} 条")
                for r in reminders['routine'][:3]:
                    lines.append(f"   • {r.title}")
                    lines.append(f"     {r.message}")
                lines.append("")
            
            if reminders.get('context'):
                lines.append(f"💡 智能提示: {len(reminders['context'])} 条")
                for r in reminders['context'][:2]:
                    lines.append(f"   • {r.message}")
                lines.append("")
            
            if reminders.get('achievement'):
                lines.append(f"🏆 新成就: {len(reminders['achievement'])} 个")
                for r in reminders['achievement']:
                    lines.append(f"   🎉 {r.title}")
                lines.append("")
            
            if reminders.get('pattern'):
                lines.append(f"⚠️  错误模式: {len(reminders['pattern'])} 个")
                for r in reminders['pattern']:
                    lines.append(f"   • {r.title}")
                lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("🧠 智能提醒系统测试")
    print("=" * 50)
    
    # 初始化
    reminder = SmartReminder()
    
    # 1. 测试逾期任务检查
    print("\n1️⃣ 检查逾期任务...")
    overdue = reminder.check_overdue_tasks()
    print(f"   找到 {len(overdue)} 条逾期任务")
    
    # 2. 测试定期任务检查
    print("\n2️⃣ 检查定期任务...")
    routine = reminder.check_routine_tasks()
    print(f"   找到 {len(routine)} 条定期任务待执行")
    
    # 3. 测试上下文提示
    print("\n3️⃣ 检查上下文提示...")
    context = reminder.check_context_tips("exec")
    print(f"   找到 {len(context)} 条上下文提示")
    
    # 4. 测试成就检查
    print("\n4️⃣ 检查成就...")
    achievements = reminder.check_achievements(recent_completed=0)
    print(f"   找到 {len(achievements)} 个新成就")
    
    # 5. 添加示例定期任务
    print("\n5️⃣ 添加示例定期任务...")
    task_id = reminder.add_routine_task(
        title="每日工作检查",
        time="09:00",
        description="检查Signal Arena账户状态",
        days=["Mon", "Tue", "Wed", "Thu", "Fri"]
    )
    print(f"   ✅ 已添加定期任务: {task_id}")
    
    # 6. 综合检查
    print("\n6️⃣ 综合提醒检查...")
    all_reminders = reminder.check_all_reminders(
        recent_completed=0,
        current_tool="write"
    )
    summary = reminder.get_reminder_summary(all_reminders)
    print(summary)
    
    # 7. 显示成就统计
    print("\n7️⃣ 成就统计...")
    stats = reminder.get_achievement_stats()
    print(f"   总成就数: {stats['total_achievements']}")
    print(f"   完成任务: {stats['stats'].get('total_completed', 0)}")
    print(f"   连续活跃: {stats['stats'].get('streak_days', 0)} 天")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("\n💡 使用示例:")
    print("""
    from smart_reminder import SmartReminder
    
    reminder = SmartReminder()
    
    # 检查所有提醒
    reminders = reminder.check_all_reminders(
        recent_completed=3,
        current_tool="exec"
    )
    
    # 打印摘要
    print(reminder.get_reminder_summary(reminders))
    
    # 添加定期任务
    reminder.add_routine_task(
        title="每天检查Signal Arena",
        time="09:00",
        days=["Mon", "Tue", "Wed", "Thu", "Fri"]
    )
    
    # 添加上下文提示
    reminder.add_context_tip(
        trigger="exec",
        tip="执行命令前注意检查路径和权限"
    )
    """)