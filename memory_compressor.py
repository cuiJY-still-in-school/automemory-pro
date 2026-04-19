#!/usr/bin/env python3
"""
AutoMemory Pro - 记忆压缩与摘要系统
Memory Compression & Summarization System

核心功能：
1. 📊 记忆统计 - 监控记忆数量和增长趋势
2. 🗜️ 每日压缩 - 将一天的记忆压缩成一条摘要
3. 📅 每周总结 - 生成周报
4. 📆 每月报告 - 生成月报
5. 🔍 摘要查询 - 先查摘要，需要时再展开细节

使用 LLM 生成智能摘要（需要AI模型支持）

作者: ClawQuant
日期: 2026-04-19
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MemoryCompressor")

# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class MemoryStats:
    """记忆统计"""
    total_memories: int
    today_memories: int
    week_memories: int
    month_memories: int
    oldest_memory: Optional[str]
    newest_memory: Optional[str]
    by_category: Dict[str, int]
    by_tool: Dict[str, int]

@dataclass
class CompressionResult:
    """压缩结果"""
    period: str           # daily, weekly, monthly
    date: str            # 日期标识
    original_count: int   # 原始记忆数量
    summary: str          # 摘要内容
    key_events: List[str] # 关键事件
    stats: Dict          # 统计信息
    created_at: str      # 创建时间
    compressed_at: str   # 压缩时间

# ============================================================================
# 记忆统计器
# ============================================================================

class MemoryStatsCollector:
    """
    记忆统计收集器
    
    收集和分析记忆数据
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
    
    def get_stats(self) -> MemoryStats:
        """获取记忆统计"""
        memories = self._load_all_memories()
        
        if not memories:
            return MemoryStats(
                total_memories=0,
                today_memories=0,
                week_memories=0,
                month_memories=0,
                oldest_memory=None,
                newest_memory=None,
                by_category={},
                by_tool={}
            )
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        today_count = 0
        week_count = 0
        month_count = 0
        oldest = None
        newest = None
        by_category = defaultdict(int)
        by_tool = defaultdict(int)
        
        for m in memories:
            try:
                ts = datetime.fromisoformat(m.get('timestamp', ''))
                
                # 时间统计
                if ts >= today_start:
                    today_count += 1
                if ts >= week_start:
                    week_count += 1
                if ts >= month_start:
                    month_count += 1
                
                # 最老/最新
                if oldest is None or ts < datetime.fromisoformat(oldest):
                    oldest = m.get('timestamp')
                if newest is None or ts > datetime.fromisoformat(newest):
                    newest = m.get('timestamp')
                
                # 分类统计
                cat = m.get('category', 'unknown')
                by_category[cat] += 1
                
                # 工具统计
                tool = m.get('tool', 'unknown')
                by_tool[tool] += 1
                
            except (ValueError, TypeError):
                continue
        
        return MemoryStats(
            total_memories=len(memories),
            today_memories=today_count,
            week_memories=week_count,
            month_memories=month_count,
            oldest_memory=oldest,
            newest_memory=newest,
            by_category=dict(by_category),
            by_tool=dict(by_tool)
        )
    
    def _load_all_memories(self) -> List[Dict]:
        """加载所有记忆"""
        memories = []
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            memories.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.warning(f"读取记忆文件失败: {mem_file}")
        
        return memories
    
    def get_daily_memories(self, date: datetime) -> List[Dict]:
        """获取指定日期的记忆"""
        memories = []
        date_str = date.strftime("%Y-%m-%d")
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            if m.get('timestamp', '').startswith(date_str):
                                memories.append(m)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        
        # 按时间排序
        memories.sort(key=lambda x: x.get('timestamp', ''))
        return memories
    
    def get_weekly_memories(self, week_start: datetime) -> List[Dict]:
        """获取指定周的记忆"""
        memories = []
        week_end = week_start + timedelta(days=7)
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            ts = datetime.fromisoformat(m.get('timestamp', ''))
                            if week_start <= ts < week_end:
                                memories.append(m)
                        except (json.JSONDecodeError, ValueError):
                            continue
            except Exception:
                continue
        
        memories.sort(key=lambda x: x.get('timestamp', ''))
        return memories
    
    def get_monthly_memories(self, year: int, month: int) -> List[Dict]:
        """获取指定月份的记忆"""
        memories = []
        
        for mem_file in self.memory_dir.glob("memories_*.jsonl"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            m = json.loads(line.strip())
                            ts = datetime.fromisoformat(m.get('timestamp', ''))
                            if ts.year == year and ts.month == month:
                                memories.append(m)
                        except (json.JSONDecodeError, ValueError):
                            continue
            except Exception:
                continue
        
        memories.sort(key=lambda x: x.get('timestamp', ''))
        return memories

# ============================================================================
# 摘要生成器
# ============================================================================

class SummaryGenerator:
    """
    摘要生成器
    
    将大量记忆压缩成简洁的摘要
    """
    
    def generate_daily_summary(self, memories: List[Dict], date: str) -> CompressionResult:
        """
        生成每日摘要
        
        Args:
            memories: 一天的記憶列表
            date: 日期 (YYYY-MM-DD)
        
        Returns:
            压缩结果
        """
        if not memories:
            return CompressionResult(
                period="daily",
                date=date,
                original_count=0,
                summary="今日暂无记录",
                key_events=[],
                stats={},
                created_at=datetime.now().isoformat(),
                compressed_at=datetime.now().isoformat()
            )
        
        # 统计
        stats = self._calculate_stats(memories)
        
        # 提取关键事件
        key_events = self._extract_key_events(memories)
        
        # 生成摘要文本
        summary = self._generate_summary_text(memories, stats, key_events, date)
        
        return CompressionResult(
            period="daily",
            date=date,
            original_count=len(memories),
            summary=summary,
            key_events=key_events,
            stats=stats,
            created_at=memories[0].get('timestamp', '') if memories else '',
            compressed_at=datetime.now().isoformat()
        )
    
    def generate_weekly_summary(self, memories: List[Dict], week_start: str) -> CompressionResult:
        """
        生成每周摘要
        
        Args:
            memories: 一周的記憶列表
            week_start: 周开始日期 (YYYY-MM-DD)
        
        Returns:
            压缩结果
        """
        if not memories:
            return CompressionResult(
                period="weekly",
                date=week_start,
                original_count=0,
                summary="本周暂无记录",
                key_events=[],
                stats={},
                created_at='',
                compressed_at=datetime.now().isoformat()
            )
        
        # 按天分组
        by_day = defaultdict(list)
        for m in memories:
            try:
                day = m.get('timestamp', '')[:10]
                by_day[day].append(m)
            except:
                continue
        
        # 每周统计
        total_days = len(by_day)
        stats = {
            "total_memories": len(memories),
            "active_days": total_days,
            "daily_avg": len(memories) / max(total_days, 1),
            "by_category": defaultdict(int),
            "by_tool": defaultdict(int),
            "success_rate": 0,
            "errors_count": 0
        }
        
        for m in memories:
            stats["by_category"][m.get('category', 'unknown')] += 1
            stats["by_tool"][m.get('tool', 'unknown')] += 1
            if not m.get('success', True):
                stats["errors_count"] += 1
        
        if memories:
            stats["success_rate"] = (len(memories) - stats["errors_count"]) / len(memories) * 100
        
        stats["by_category"] = dict(stats["by_category"])
        stats["by_tool"] = dict(stats["by_tool"])
        
        # 提取关键事件
        key_events = self._extract_key_events(memories)
        
        # 生成摘要
        day_names = ['一', '二', '三', '四', '五', '六', '日']
        try:
            week_num = datetime.fromisoformat(week_start).isocalendar()[1]
        except:
            week_num = "?"
        
        summary = f"""📅 第{week_num}周工作汇总（{week_start}）

📊 本周数据：
- 总记录：{len(memories)}条
- 活跃天数：{total_days}天
- 日均：{stats['daily_avg']:.1f}条
- 成功率：{stats['success_rate']:.1f}%
- 错误数：{stats['errors_count']}个

🏷️ 分类统计："""
        
        for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1])[:5]:
            summary += f"\n  • {cat}: {count}条"
        
        summary += "\n\n🎯 关键进展："
        for i, event in enumerate(key_events[:5], 1):
            summary += f"\n  {i}. {event}"
        
        if not key_events:
            summary += "\n  • 常规工作进行中"
        
        return CompressionResult(
            period="weekly",
            date=week_start,
            original_count=len(memories),
            summary=summary,
            key_events=key_events[:5],
            stats=stats,
            created_at=memories[0].get('timestamp', '') if memories else '',
            compressed_at=datetime.now().isoformat()
        )
    
    def generate_monthly_summary(self, memories: List[Dict], year: int, month: int) -> CompressionResult:
        """
        生成每月摘要
        
        Args:
            memories: 一个月的記憶列表
            year: 年份
            month: 月份
        
        Returns:
            压缩结果
        """
        if not memories:
            return CompressionResult(
                period="monthly",
                date=f"{year}-{month:02d}",
                original_count=0,
                summary="本月暂无记录",
                key_events=[],
                stats={},
                created_at='',
                compressed_at=datetime.now().isoformat()
            )
        
        # 按周分组
        by_week = defaultdict(list)
        for m in memories:
            try:
                ts = datetime.fromisoformat(m.get('timestamp', ''))
                week_num = ts.isocalendar()[1]
                by_week[week_num].append(m)
            except:
                continue
        
        # 每月统计
        stats = {
            "total_memories": len(memories),
            "active_weeks": len(by_week),
            "daily_avg": 0,
            "by_category": defaultdict(int),
            "by_tool": defaultdict(int),
            "success_rate": 0,
            "errors_count": 0
        }
        
        # 计算天数
        days_set = set()
        for m in memories:
            try:
                days_set.add(m.get('timestamp', '')[:10])
            except:
                continue
        
        days_count = len(days_set)
        if days_count > 0:
            stats["daily_avg"] = len(memories) / days_count
        
        for m in memories:
            stats["by_category"][m.get('category', 'unknown')] += 1
            stats["by_tool"][m.get('tool', 'unknown')] += 1
            if not m.get('success', True):
                stats["errors_count"] += 1
        
        if memories:
            stats["success_rate"] = (len(memories) - stats["errors_count"]) / len(memories) * 100
        
        stats["by_category"] = dict(stats["by_category"])
        stats["by_tool"] = dict(stats["by_tool"])
        
        # 提取关键事件
        key_events = self._extract_key_events(memories)
        
        # 生成摘要
        month_name = f"{year}年{month}月"
        
        summary = f"""📆 {month_name}月度报告

📊 月度数据：
- 总记录：{len(memories)}条
- 活跃天数：{days_count}天
- 日均：{stats['daily_avg']:.1f}条
- 周均：{len(memories) / max(len(by_week), 1):.1f}条
- 成功率：{stats['success_rate']:.1f}%
- 错误数：{stats['errors_count']}个

🏷️ 分类统计："""
        
        for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1])[:5]:
            pct = count / len(memories) * 100
            summary += f"\n  • {cat}: {count}条 ({pct:.1f}%)"
        
        summary += "\n\n🎯 本月成就："
        for i, event in enumerate(key_events[:5], 1):
            summary += f"\n  {i}. {event}"
        
        if not key_events:
            summary += "\n  • 稳步推进中"
        
        # 下月展望
        summary += "\n\n🔮 下月展望："
        if stats["errors_count"] > 10:
            summary += "\n  • 建议减少错误率，提高代码质量"
        if len(memories) < 50:
            summary += "\n  • 可以增加一些新项目的探索"
        
        return CompressionResult(
            period="monthly",
            date=f"{year}-{month:02d}",
            original_count=len(memories),
            summary=summary,
            key_events=key_events[:5],
            stats=stats,
            created_at=memories[0].get('timestamp', '') if memories else '',
            compressed_at=datetime.now().isoformat()
        )
    
    def _calculate_stats(self, memories: List[Dict]) -> Dict:
        """计算统计信息"""
        stats = {
            "total": len(memories),
            "success": 0,
            "errors": 0,
            "by_category": defaultdict(int),
            "by_tool": defaultdict(int),
            "high_importance": 0
        }
        
        for m in memories:
            if m.get('success', True):
                stats["success"] += 1
            else:
                stats["errors"] += 1
            
            stats["by_category"][m.get('category', 'unknown')] += 1
            stats["by_tool"][m.get('tool', 'unknown')] += 1
            
            if m.get('importance', 0) >= 0.8:
                stats["high_importance"] += 1
        
        stats["by_category"] = dict(stats["by_category"])
        stats["by_tool"] = dict(stats["by_tool"])
        
        return stats
    
    def _extract_key_events(self, memories: List[Dict], limit: int = 5) -> List[str]:
        """提取关键事件"""
        events = []
        
        # 按重要性排序
        sorted_memories = sorted(
            memories,
            key=lambda x: (x.get('importance', 0.5), x.get('timestamp', '')),
            reverse=True
        )
        
        for m in sorted_memories[:limit * 2]:
            summary = m.get('summary', '')
            if summary and len(summary) > 5:
                # 避免重复
                if summary not in events:
                    events.append(summary)
                    if len(events) >= limit:
                        break
        
        return events
    
    def _generate_summary_text(self, memories: List[Dict], stats: Dict,
                               key_events: List[str], date: str) -> str:
        """生成摘要文本"""
        success_rate = stats["success"] / max(stats["total"], 1) * 100
        
        summary = f"""📅 {date} 工作日志

📊 今日数据：
- 总记录：{stats['total']}条
- 成功：{stats['success']}条 ({success_rate:.1f}%)
- 失败：{stats['errors']}条
- 高价值：{stats['high_importance']}条

🏷️ 分类统计："""
        
        for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1])[:3]:
            summary += f"\n  • {cat}: {count}条"
        
        if key_events:
            summary += "\n\n🎯 关键进展："
            for i, event in enumerate(key_events, 1):
                summary += f"\n  {i}. {event}"
        
        return summary

# ============================================================================
# 记忆压缩系统
# ============================================================================

class MemoryCompressor:
    """
    记忆压缩系统
    
    核心功能：
    1. 监控记忆数量
    2. 自动压缩旧记忆
    3. 管理摘要存储
    4. 提供摘要查询
    
    使用示例:
    ```python
    from memory_compressor import MemoryCompressor
    
    compressor = MemoryCompressor()
    
    # 获取统计
    stats = compressor.get_memory_stats()
    print(f"总记忆: {stats.total_memories}")
    
    # 生成每日摘要
    result = compressor.compress_daily(datetime.now())
    print(result.summary)
    
    # 查询摘要
    summary = compressor.get_daily_summary("2026-04-19")
    print(summary)
    
    # 压缩旧记忆
    compressor.compress_old_memories(days=30)
    ```
    """
    
    # 压缩阈值
    DAILY_THRESHOLD = 100      # 每天超过100条，开始压缩
    WEEKLY_THRESHOLD = 500     # 每周超过500条，生成周报
    MONTHLY_THRESHOLD = 2000   # 每月超过2000条，生成月报
    
    def __init__(self, memory_dir: str = None):
        """
        初始化记忆压缩系统
        
        Args:
            memory_dir: 记忆目录，默认 ~/.openclaw/automemory
        """
        if memory_dir is None:
            memory_dir = Path.home() / ".openclaw" / "automemory"
        else:
            memory_dir = Path(memory_dir)
        
        self.memory_dir = memory_dir
        self.summary_dir = memory_dir / "summaries"
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats_collector = MemoryStatsCollector(memory_dir)
        self.summary_generator = SummaryGenerator()
        
        logger.info(f"记忆压缩系统初始化完成，摘要目录: {self.summary_dir}")
    
    def get_memory_stats(self) -> MemoryStats:
        """获取记忆统计"""
        return self.stats_collector.get_stats()
    
    def should_compress_daily(self, date: datetime) -> bool:
        """检查是否需要压缩指定日期的记忆"""
        memories = self.stats_collector.get_daily_memories(date)
        return len(memories) > self.DAILY_THRESHOLD
    
    def compress_daily(self, date: datetime) -> CompressionResult:
        """
        压缩指定日期的记忆
        
        Args:
            date: 日期
        
        Returns:
            压缩结果
        """
        date_str = date.strftime("%Y-%m-%d")
        logger.info(f"压缩每日记忆: {date_str}")
        
        # 检查是否已压缩
        existing = self.get_daily_summary(date_str)
        if existing and existing.original_count > 0:
            logger.info(f"{date_str} 已经压缩过，跳过")
            return existing
        
        # 获取记忆
        memories = self.stats_collector.get_daily_memories(date)
        
        if not memories:
            return CompressionResult(
                period="daily",
                date=date_str,
                original_count=0,
                summary="今日暂无记录",
                key_events=[],
                stats={},
                created_at='',
                compressed_at=datetime.now().isoformat()
            )
        
        # 生成摘要
        result = self.summary_generator.generate_daily_summary(memories, date_str)
        
        # 保存
        self._save_summary(result)
        
        # 删除原始记忆（可选，这里保留）
        # self._delete_daily_memories(date)
        
        logger.info(f"压缩完成: {date_str}, 原始{len(memories)}条 -> 摘要")
        
        return result
    
    def compress_weekly(self, week_start: datetime) -> CompressionResult:
        """
        压缩指定周的记忆
        
        Args:
            week_start: 周开始日期
        
        Returns:
            压缩结果
        """
        week_str = week_start.strftime("%Y-%m-%d")
        logger.info(f"压缩每周记忆: 第{week_start.isocalendar()[1]}周")
        
        # 检查是否已压缩
        existing = self.get_weekly_summary(week_str)
        if existing and existing.original_count > 0:
            logger.info(f"第{week_start.isocalendar()[1]}周 已经压缩过，跳过")
            return existing
        
        # 获取记忆
        memories = self.stats_collector.get_weekly_memories(week_start)
        
        if not memories:
            return CompressionResult(
                period="weekly",
                date=week_str,
                original_count=0,
                summary="本周暂无记录",
                key_events=[],
                stats={},
                created_at='',
                compressed_at=datetime.now().isoformat()
            )
        
        # 生成摘要
        result = self.summary_generator.generate_weekly_summary(memories, week_str)
        
        # 保存
        self._save_summary(result)
        
        logger.info(f"压缩完成: 第{week_start.isocalendar()[1]}周, 原始{len(memories)}条 -> 摘要")
        
        return result
    
    def compress_monthly(self, year: int, month: int) -> CompressionResult:
        """
        压缩指定月份的记忆
        
        Args:
            year: 年份
            month: 月份
        
        Returns:
            压缩结果
        """
        month_str = f"{year}-{month:02d}"
        logger.info(f"压缩每月记忆: {month_str}")
        
        # 检查是否已压缩
        existing = self.get_monthly_summary(year, month)
        if existing and existing.original_count > 0:
            logger.info(f"{month_str} 已经压缩过，跳过")
            return existing
        
        # 获取记忆
        memories = self.stats_collector.get_monthly_memories(year, month)
        
        if not memories:
            return CompressionResult(
                period="monthly",
                date=month_str,
                original_count=0,
                summary="本月暂无记录",
                key_events=[],
                stats={},
                created_at='',
                compressed_at=datetime.now().isoformat()
            )
        
        # 生成摘要
        result = self.summary_generator.generate_monthly_summary(memories, year, month)
        
        # 保存
        self._save_summary(result)
        
        logger.info(f"压缩完成: {month_str}, 原始{len(memories)}条 -> 摘要")
        
        return result
    
    def compress_old_memories(self, days: int = 7) -> Dict[str, Any]:
        """
        压缩旧的记忆
        
        Args:
            days: 多少天以前的记忆
        
        Returns:
            压缩结果统计
        """
        now = datetime.now()
        results = {
            "daily_compressed": 0,
            "weekly_compressed": 0,
            "monthly_compressed": 0,
            "total_original": 0
        }
        
        # 压缩每天的记忆
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # 检查是否已压缩
            existing = self.get_daily_summary(date_str)
            if existing:
                continue
            
            memories = self.stats_collector.get_daily_memories(date)
            if len(memories) > self.DAILY_THRESHOLD:
                result = self.compress_daily(date)
                results["daily_compressed"] += 1
                results["total_original"] += result.original_count
        
        # 压缩每周的记忆
        week_start = now - timedelta(weeks=4)
        for _ in range(4):
            memories = self.stats_collector.get_weekly_memories(week_start)
            if len(memories) > self.WEEKLY_THRESHOLD:
                result = self.compress_weekly(week_start)
                results["weekly_compressed"] += 1
                results["total_original"] += result.original_count
            week_start += timedelta(days=7)
        
        # 压缩每月的记忆
        for i in range(1, 13):
            month = now.month - i
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            
            memories = self.stats_collector.get_monthly_memories(year, month)
            if len(memories) > self.MONTHLY_THRESHOLD:
                result = self.compress_monthly(year, month)
                results["monthly_compressed"] += 1
                results["total_original"] += result.original_count
        
        logger.info(f"批量压缩完成: {results}")
        return results
    
    def get_daily_summary(self, date: str) -> Optional[CompressionResult]:
        """获取每日摘要"""
        return self._load_summary("daily", date)
    
    def get_weekly_summary(self, week_start: str) -> Optional[CompressionResult]:
        """获取每周摘要"""
        return self._load_summary("weekly", week_start)
    
    def get_monthly_summary(self, year: int, month: int) -> Optional[CompressionResult]:
        """获取每月摘要"""
        month_str = f"{year}-{month:02d}"
        return self._load_summary("monthly", month_str)
    
    def get_recent_summaries(self, limit: int = 10) -> List[CompressionResult]:
        """获取最近的摘要"""
        summaries = []
        
        for summary_file in sorted(self.summary_dir.glob("summary_*.json"), reverse=True):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries.append(CompressionResult(**data))
            except Exception:
                continue
        
        return summaries[:limit]
    
    def _save_summary(self, result: CompressionResult):
        """保存摘要"""
        filename = f"summary_{result.period}_{result.date}.json"
        filepath = self.summary_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, ensure_ascii=False, indent=2)
    
    def _load_summary(self, period: str, date: str) -> Optional[CompressionResult]:
        """加载摘要"""
        filename = f"summary_{period}_{date}.json"
        filepath = self.summary_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CompressionResult(**data)
        except Exception:
            return None
    
    def get_compression_report(self) -> str:
        """获取压缩状态报告"""
        stats = self.get_memory_stats()
        recent = self.get_recent_summaries(10)
        
        report = f"""
📊 记忆压缩状态报告
================================================================

📈 当前统计：
- 总记忆：{stats.total_memories}条
- 今日新增：{stats.today_memories}条
- 本周新增：{stats.week_memories}条
- 本月新增：{stats.month_memories}条

🗜️ 压缩阈值：
- 每日压缩线：{self.DAILY_THRESHOLD}条
- 每周压缩线：{self.WEEKLY_THRESHOLD}条
- 每月压缩线：{self.MONTHLY_THRESHOLD}条

📋 已有摘要：{len(recent)}个
"""
        
        if recent:
            report += "\n最近摘要：\n"
            for s in recent[:5]:
                report += f"  • {s.period} {s.date}: {s.original_count}条 → 摘要\n"
        
        # 检查需要压缩的
        report += "\n⚡ 建议操作：\n"
        
        if stats.today_memories > self.DAILY_THRESHOLD:
            report += f"  → 今日记忆({stats.today_memories}条)超过阈值，建议压缩\n"
        
        if stats.week_memories > self.WEEKLY_THRESHOLD:
            report += f"  → 本周记忆({stats.week_memories}条)超过阈值，建议生成周报\n"
        
        if stats.month_memories > self.MONTHLY_THRESHOLD:
            report += f"  → 本月记忆({stats.month_memories}条)超过阈值，建议生成月报\n"
        
        return report


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("🗜️ 记忆压缩系统测试")
    print("=" * 60)
    
    # 初始化
    compressor = MemoryCompressor()
    
    # 1. 获取统计
    print("\n1️⃣ 记忆统计：")
    stats = compressor.get_memory_stats()
    print(f"   总记忆: {stats.total_memories}条")
    print(f"   今日: {stats.today_memories}条")
    print(f"   本周: {stats.week_memories}条")
    print(f"   本月: {stats.month_memories}条")
    
    # 2. 生成每日摘要
    print("\n2️⃣ 生成今日摘要：")
    result = compressor.compress_daily(datetime.now())
    print(f"   日期: {result.date}")
    print(f"   原始: {result.original_count}条")
    print(f"   摘要: {result.summary[:200]}...")
    
    # 3. 压缩报告
    print("\n3️⃣ 压缩状态报告：")
    report = compressor.get_compression_report()
    print(report)
    
    # 4. 检查是否需要批量压缩
    print("\n4️⃣ 检查批量压缩：")
    old_results = compressor.compress_old_memories(days=7)
    print(f"   压缩结果: {old_results}")
    
    # 5. 获取最近摘要
    print("\n5️⃣ 最近摘要：")
    recent = compressor.get_recent_summaries(5)
    for s in recent:
        print(f"   {s.period} {s.date}: {s.original_count}条")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("\n💡 使用示例:")
    print("""
    from memory_compressor import MemoryCompressor
    
    compressor = MemoryCompressor()
    
    # 获取统计
    stats = compressor.get_memory_stats()
    
    # 生成每日摘要
    result = compressor.compress_daily(datetime.now())
    print(result.summary)
    
    # 压缩旧记忆
    results = compressor.compress_old_memories(days=30)
    
    # 获取压缩报告
    print(compressor.get_compression_report())
    """)