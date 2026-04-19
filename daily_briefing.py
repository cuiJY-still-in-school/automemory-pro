#!/usr/bin/env python3
"""
AutoMemory Pro - 每日简报生成器
Daily Briefing Generator

每天开始工作时，AI 自动生成简报，快速进入状态

作者: ClawQuant
日期: 2026-04-19
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DailyBriefing")

# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class TodoItem:
    """待办事项"""
    id: str
    text: str
    priority: str  # high, medium, low
    due_date: Optional[str] = None
    project: Optional[str] = None
    status: str = "pending"  # pending, completed, overdue
    created_at: str = ""
    
@dataclass
class BriefingSection:
    """简报章节"""
    title: str
    icon: str
    content: List[str]
    priority: int = 0  # 显示顺序

@dataclass
class DailyBriefing:
    """每日简报"""
    date: str
    sections: List[BriefingSection]
    generated_at: str
    stats: Dict

# ============================================================================
# 每日简报生成器
# ============================================================================

class DailyBriefingGenerator:
    """
    每日简报生成器
    
    每天开始工作时生成简报，帮助 AI 快速进入状态
    
    使用示例:
    ```python
    from daily_briefing import DailyBriefingGenerator
    
    generator = DailyBriefingGenerator()
    briefing = generator.generate()
    
    print(briefing.text)
    ```
    """
    
    def __init__(self, memory_dir: str = None):
        """
        初始化简报生成器
        
        Args:
            memory_dir: 记忆目录
        """
        if memory_dir is None:
            memory_dir = Path.home() / ".openclaw" / "automemory"
        else:
            memory_dir = Path(memory_dir)
        
        self.memory_dir = memory_dir
        self.tasks_file = memory_dir / "tasks.json"
        self.reminder_dir = memory_dir / "reminders"
        
        logger.info("每日简报生成器初始化完成")
    
    def generate(self, date: datetime = None) -> DailyBriefing:
        """
        生成每日简报
        
        Args:
            date: 日期，默认今天
        
        Returns:
            DailyBriefing 对象
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        logger.info(f"生成简报: {date_str}")
        
        sections = []
        stats = {}
        
        # 1. 获取时间相关的元信息
        greeting = self._get_greeting()
        weekday = date.strftime("%A")
        weekday_cn = self._get_weekday_cn(date)
        
        sections.append(BriefingSection(
            title=f"{greeting}！今天{weekday_cn}",
            icon="👋",
            content=[],
            priority=0
        ))
        
        # 2. 今日待办
        todo_section = self._get_todo_section()
        if todo_section:
            sections.append(todo_section)
        
        # 3. 昨日进展
        yesterday_section = self._get_yesterday_section(date)
        if yesterday_section:
            sections.append(yesterday_section)
        
        # 4. 逾期提醒
        overdue_section = self._get_overdue_section()
        if overdue_section:
            sections.append(overdue_section)
        
        # 5. 注意事项
        caution_section = self._get_caution_section()
        if caution_section:
            sections.append(caution_section)
        
        # 6. 建议
        suggestion_section = self._get_suggestion_section()
        if suggestion_section:
            sections.append(suggestion_section)
        
        # 7. 快速统计
        stats_section = self._get_stats_section(date)
        if stats_section:
            sections.append(stats_section)
        
        briefing = DailyBriefing(
            date=date_str,
            sections=sections,
            generated_at=datetime.now().isoformat(),
            stats=stats
        )
        
        return briefing
    
    def _get_greeting(self) -> str:
        """获取问候语"""
        hour = datetime.now().hour
        
        if 5 <= hour < 9:
            return "早上好"
        elif 9 <= hour < 12:
            return "上午好"
        elif 12 <= hour < 14:
            return "中午好"
        elif 14 <= hour < 18:
            return "下午好"
        elif 18 <= hour < 22:
            return "晚上好"
        else:
            return "夜深了"
    
    def _get_weekday_cn(self, date: datetime) -> str:
        """获取中文星期"""
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[date.weekday()]
    
    def _get_todo_section(self) -> Optional[BriefingSection]:
        """获取今日待办"""
        todos = self._get_pending_todos()
        
        if not todos:
            return None
        
        content = []
        
        # 按优先级分组
        high_priority = [t for t in todos if t.priority == "high"]
        medium_priority = [t for t in todos if t.priority == "medium"]
        low_priority = [t for t in todos if t.priority == "low"]
        
        for i, todo in enumerate(high_priority[:3], 1):
            project_tag = f"[{todo.project}] " if todo.project else ""
            content.append(f"{i}. 🔴 {project_tag}{todo.text}")
        
        for i, todo in enumerate(medium_priority[:3], len(high_priority)+1):
            project_tag = f"[{todo.project}] " if todo.project else ""
            content.append(f"{i}. 🟡 {project_tag}{todo.text}")
        
        for i, todo in enumerate(low_priority[:2], len(high_priority)+len(medium_priority)+1):
            project_tag = f"[{todo.project}] " if todo.project else ""
            content.append(f"{i}. 🟢 {project_tag}{todo.text}")
        
        total = len(todos)
        if total > 8:
            content.append(f"...还有 {total - 8} 项")
        
        return BriefingSection(
            title="🎯 今日待办",
            icon="📋",
            content=content,
            priority=1
        )
    
    def _get_yesterday_section(self, date: datetime) -> Optional[BriefingSection]:
        """获取昨日进展"""
        yesterday = date - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        
        # 从记忆中提取昨日完成的任务
        completed = self._get_completed_yesterday(yesterday_str)
        
        if not completed:
            return None
        
        content = []
        
        # 按项目分组显示
        by_project = {}
        for item in completed[:10]:
            project = item.get("project", "其他")
            if project not in by_project:
                by_project[project] = []
            by_project[project].append(item.get("text", item.get("summary", "")))
        
        for project, items in by_project.items():
            content.append(f"**{project}**：")
            for item in items[:3]:
                if len(item) > 50:
                    item = item[:50] + "..."
                content.append(f"  • {item}")
            if len(items) > 3:
                content.append(f"  • ...还有{len(items)-3}项")
        
        return BriefingSection(
            title="📊 昨日进展",
            icon="✅",
            content=content,
            priority=2
        )
    
    def _get_overdue_section(self) -> Optional[BriefingSection]:
        """获取逾期提醒"""
        overdue = self._get_overdue_todos()
        
        if not overdue:
            return None
        
        content = []
        
        for i, todo in enumerate(overdue[:5], 1):
            days_overdue = todo.get("days_overdue", 1)
            project_tag = f"[{todo.get('project', '')}] " if todo.get('project') else ""
            content.append(f"{i}. ⚠️ {project_tag}{todo['text']} (逾期{days_overdue}天)")
        
        if len(overdue) > 5:
            content.append(f"...还有 {len(overdue) - 5} 项逾期任务")
        
        return BriefingSection(
            title="⚠️ 逾期提醒",
            icon="🚨",
            content=content,
            priority=0  # 高优先级
        )
    
    def _get_caution_section(self) -> Optional[BriefingSection]:
        """获取注意事项"""
        cautions = []
        
        # 从错误记忆中提取常见问题
        error_patterns = self._get_error_patterns()
        for pattern in error_patterns[:3]:
            cautions.append(f"• {pattern}")
        
        # 从记忆中提取未解决的问题
        unresolved = self._get_unresolved_issues()
        for issue in unresolved[:2]:
            cautions.append(f"• {issue}")
        
        if not cautions:
            return None
        
        return BriefingSection(
            title="⚠️ 注意事项",
            icon="💡",
            content=cautions,
            priority=3
        )
    
    def _get_suggestion_section(self) -> Optional[BriefingSection]:
        """获取建议"""
        suggestions = []
        
        # 基于时间建议
        hour = datetime.now().hour
        
        if 6 <= hour < 9:
            suggestions.append("☕ 建议先查看今日任务，制定工作计划")
        elif 9 <= hour < 12:
            suggestions.append("🧠 上午适合处理复杂任务")
        elif 14 <= hour < 17:
            suggestions.append("📧 下午适合沟通和协调")
        elif 17 <= hour < 19:
            suggestions.append("📋 建议整理今日工作，准备收工")
        
        # 基于待办建议
        pending_count = len(self._get_pending_todos())
        if pending_count > 10:
            suggestions.append(f"📌 待办较多({pending_count}项)，建议分批处理")
        
        # 基于进度建议
        progress = self._get_milestone_progress()
        if progress:
            suggestions.append(f"📈 {progress}")
        
        if not suggestions:
            return None
        
        return BriefingSection(
            title="💡 建议",
            icon="🚀",
            content=suggestions,
            priority=4
        )
    
    def _get_stats_section(self, date: datetime) -> Optional[BriefingSection]:
        """获取快速统计"""
        content = []
        
        # 本周完成数
        week_completed = self._get_week_completed_count(date)
        if week_completed > 0:
            content.append(f"本周完成：{week_completed} 项")
        
        # 本月活跃天数
        month_active = self._get_month_active_days(date)
        content.append(f"本月活跃：{month_active} 天")
        
        # 记忆总数
        total_memories = self._get_total_memories()
        content.append(f"记忆总数：{total_memories} 条")
        
        return BriefingSection(
            title="📈 统计",
            icon="📊",
            content=content,
            priority=5
        )
    
    # =========================================================================
    # 数据获取方法
    # =========================================================================
    
    def _get_pending_todos(self) -> List[TodoItem]:
        """获取待办事项"""
        todos = []
        
        # 从 tasks.json 加载
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task in data.get('tasks', []):
                        if task.get('status') == 'pending':
                            todos.append(TodoItem(
                                id=task.get('id', ''),
                                text=task.get('text', ''),
                                priority=task.get('priority', 'medium'),
                                due_date=task.get('due_date'),
                                project=task.get('project'),
                                status=task.get('status', 'pending'),
                                created_at=task.get('created_at', '')
                            ))
            except Exception:
                pass
        
        return todos
    
    def _get_overdue_todos(self) -> List[Dict]:
        """获取逾期任务"""
        overdue = []
        now = datetime.now()
        
        todos = self._get_pending_todos()
        
        for todo in todos:
            if todo.due_date:
                try:
                    due = datetime.fromisoformat(todo.due_date)
                    if due < now:
                        days_overdue = (now - due).days
                        overdue.append({
                            **vars(todo),
                            "days_overdue": days_overdue
                        })
                except:
                    pass
        
        # 按逾期天数排序
        overdue.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
        
        return overdue
    
    def _get_completed_yesterday(self, date_str: str) -> List[Dict]:
        """获取昨日完成的任务"""
        completed = []
        
        # 从记忆中查找
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            # 检查是否是昨日的记忆且标记为完成
                            if date_str in m.get('timestamp', ''):
                                if m.get('completed_tasks') or 'success' in str(m.get('summary', '')).lower():
                                    completed.append({
                                        "text": m.get('summary', ''),
                                        "project": m.get('context', {}).get('project', '工作'),
                                        "tool": m.get('tool', '')
                                    })
                        except:
                            continue
            except:
                continue
        
        return completed
    
    def _get_error_patterns(self) -> List[str]:
        """获取错误模式"""
        patterns = []
        
        # 从 reminder patterns 文件加载
        patterns_file = self.reminder_dir / "patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pattern in data.get('common_errors', [])[:3]:
                        patterns.append(f"常见错误：{pattern}")
            except:
                pass
        
        return patterns
    
    def _get_unresolved_issues(self) -> List[str]:
        """获取未解决的问题"""
        issues = []
        
        # 从记忆中查找错误记录
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            # 查找错误但未解决
                            if not m.get('success', True) and not m.get('resolved', False):
                                error = m.get('summary', m.get('errors', ['未知错误']))
                                if isinstance(error, list):
                                    error = error[0] if error else '未知错误'
                                if error and len(error) < 100:
                                    issues.append(f"待解决：{error}")
                        except:
                            continue
            except:
                continue
        
        # 去重，只保留最新的3个
        seen = set()
        unique_issues = []
        for issue in issues:
            if issue not in seen:
                seen.add(issue)
                unique_issues.append(issue)
        
        return unique_issues[:3]
    
    def _get_week_completed_count(self, date: datetime) -> int:
        """获取本周完成数"""
        count = 0
        week_start = date - timedelta(days=date.weekday())
        week_str = week_start.strftime("%Y-%m-%d")
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            if week_str <= m.get('timestamp', '')[:10] <= date.strftime("%Y-%m-%d"):
                                if m.get('completed_tasks') or m.get('category') == 'actions':
                                    count += 1
                        except:
                            continue
            except:
                continue
        
        return count
    
    def _get_month_active_days(self, date: datetime) -> int:
        """获取本月活跃天数"""
        days = set()
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            ts = m.get('timestamp', '')
                            if ts:
                                day = ts[:10]
                                # 检查是否在本月
                                if day.startswith(date.strftime("%Y-%m")):
                                    days.add(day)
                        except:
                            continue
            except:
                continue
        
        return len(days)
    
    def _get_total_memories(self) -> int:
        """获取总记忆数"""
        count = 0
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    count += sum(1 for _ in f)
            except:
                continue
        
        return count
    
    def _get_milestone_progress(self) -> Optional[str]:
        """获取里程碑进度"""
        # 这需要项目配置，简化版返回 None
        return None
    
    # =========================================================================
    # 格式化输出
    # =========================================================================
    
    def format_briefing(self, briefing: DailyBriefing) -> str:
        """格式化简报为文本"""
        lines = []
        
        lines.append("=" * 60)
        lines.append(f"📋 每日简报 - {briefing.date}")
        lines.append("=" * 60)
        lines.append("")
        
        # 按优先级排序显示
        sections = sorted(briefing.sections, key=lambda x: x.priority)
        
        for section in sections:
            if not section.content:
                continue
            
            lines.append(f"{section.icon} {section.title}")
            lines.append("-" * 40)
            
            for line in section.content:
                lines.append(f"  {line}")
            
            lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"🕐 生成时间: {briefing.generated_at[:19]}")
        lines.append("")
        
        return "\n".join(lines)
    
    def format_short_briefing(self, briefing: DailyBriefing) -> str:
        """格式化简报为简短版本"""
        lines = []
        
        lines.append(f"📋 每日简报 {briefing.date}")
        lines.append("")
        
        # 只显示最重要的几个部分
        sections = sorted(briefing.sections, key=lambda x: x.priority)[:4]
        
        for section in sections:
            if not section.content:
                continue
            
            lines.append(f"{section.icon} {section.title}")
            for line in section.content[:5]:
                lines.append(f"  {line}")
            lines.append("")
        
        return "\n".join(lines)


# ============================================================================
# 简报查看命令
# ============================================================================

class BriefingViewer:
    """
    简报查看器
    
    方便查看历史简报
    """
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            memory_dir = Path.home() / ".openclaw" / "automemory"
        self.briefing_dir = memory_dir / "briefings"
        self.briefing_dir.mkdir(parents=True, exist_ok=True)
    
    def save_briefing(self, briefing: DailyBriefing, formatted_text: str = None):
        """保存简报"""
        filename = f"briefing_{briefing.date}.txt"
        filepath = self.briefing_dir / filename
        
        if formatted_text is None:
            from daily_briefing import DailyBriefingGenerator
            gen = DailyBriefingGenerator()
            formatted_text = gen.format_briefing(briefing)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        logger.info(f"简报已保存: {filepath}")
    
    def load_briefing(self, date: str) -> Optional[str]:
        """加载指定日期的简报"""
        filename = f"briefing_{date}.txt"
        filepath = self.briefing_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_briefings(self) -> List[str]:
        """列出所有简报"""
        return [f.stem.replace("briefing_", "") 
                for f in sorted(self.briefing_dir.glob("briefing_*.txt"), reverse=True)]


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("📋 每日简报生成器测试")
    print("=" * 60)
    
    # 初始化
    generator = DailyBriefingGenerator()
    
    # 生成今日简报
    print("\n🆕 生成今日简报...")
    briefing = generator.generate()
    
    # 格式化输出
    print(generator.format_briefing(briefing))
    
    # 简短版本
    print("\n📝 简短版本:")
    print(generator.format_short_briefing(briefing))
    
    # 保存简报
    print("\n💾 保存简报...")
    viewer = BriefingViewer()
    viewer.save_briefing(briefing)
    
    # 列出历史简报
    print("\n📂 历史简报:")
    briefings = viewer.list_briefings()
    for b in briefings[:5]:
        print(f"  • {b}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("\n💡 使用示例:")
    print("""
    from daily_briefing import DailyBriefingGenerator
    
    generator = DailyBriefingGenerator()
    
    # 生成今日简报
    briefing = generator.generate()
    
    # 打印完整简报
    print(generator.format_briefing(briefing))
    
    # 或打印简短版本
    print(generator.format_short_briefing(briefing))
    """)