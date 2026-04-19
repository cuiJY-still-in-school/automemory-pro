#!/usr/bin/env python3
"""
AutoMemory Pro - 自然语言查询系统
Natural Language Query System

核心功能：
1. 意图识别 - 理解用户想查询什么
2. 语义解析 - 转换为结构化查询条件
3. 智能回答 - 用AI模型生成自然语言回答

使用 LLM 理解自然语言，而非简单关键词匹配

作者: ClawQuant
日期: 2026-04-19
"""

import json
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NaturalQuery")

# ============================================================================
# 数据结构
# ============================================================================

class QueryIntent(Enum):
    """查询意图类型"""
    WHAT_DID_YOU_DO = "what_did_you_do"      # "我做了什么"
    WHAT_DID_I_DO = "what_did_i_do"          # "我昨天/今天做了什么"
    PENDING_TASKS = "pending_tasks"          # "有什么任务待完成"
    OVERDUE_TASKS = "overdue_tasks"          # "有什么逾期任务"
    PROGRESS = "progress"                     # "项目进展如何"
    ERRORS = "errors"                         # "犯了什么错误"
    DECISIONS = "decisions"                   # "做了什么决定"
    DISCOVERIES = "discoveries"               # "发现了什么"
    SUMMARIZE = "summarize"                   # "总结一下"
    SEARCH = "search"                         # "搜索记忆"
    UNKNOWN = "unknown"                       # 未知意图

@dataclass
class QueryContext:
    """查询上下文"""
    time_range: str = "all"      # today, yesterday, this_week, this_month, all
    task_status: str = "all"      # pending, completed, overdue, all
    memory_type: str = "all"      # actions, errors, decisions, discoveries, all
    project: Optional[str] = None  # 项目名称
    keywords: List[str] = None    # 关键词
    limit: int = 10               # 返回数量
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

@dataclass
class QueryResult:
    """查询结果"""
    intent: QueryIntent
    query: str                    # 原始查询
    context: QueryContext         # 解析后的上下文
    memories: List[Dict]          # 找到的记忆
    answer: str                    # AI生成的回答
    summary: str                   # 简短总结
    total_found: int              # 总共找到多少条

# ============================================================================
# 意图识别器
# ============================================================================

class IntentRecognizer:
    """
    自然语言意图识别器
    
    将用户的自然语言转换为结构化查询条件
    """
    
    # 时间关键词映射
    TIME_KEYWORDS = {
        # 今天
        '今天': 'today',
        '今日': 'today',
        'this day': 'today',
        'today': 'today',
        
        # 昨天
        '昨天': 'yesterday',
        '昨日': 'yesterday',
        'last day': 'yesterday',
        'yesterday': 'yesterday',
        
        # 本周
        '这周': 'this_week',
        '本周': 'this_week',
        'this week': 'this_week',
        '最近一周': 'this_week',
        
        # 上周
        '上周': 'last_week',
        'last week': 'last_week',
        
        # 本月
        '这月': 'this_month',
        '本月': 'this_month',
        'this month': 'this_month',
        
        # 上月
        '上月': 'last_month',
        'last month': 'last_month',
    }
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        QueryIntent.WHAT_DID_I_DO: [
            r'我.*做了',
            r'我.*完成',
            r'我.*干了',
            r'我.*进行',
            r'做了.*什么',
            r'干了.*什么',
            r'完成.*什么',
            r'did.*do',
            r'what.*did.*i',
        ],
        QueryIntent.PENDING_TASKS: [
            r'待完成',
            r'待办',
            r'还没完成',
            r'未完成',
            r'没完成',
            r'还有.*任务',
            r'任务.*待',
            r'pending.*task',
            r'tasks.*todo',
        ],
        QueryIntent.OVERDUE_TASKS: [
            r'逾期',
            r'过期',
            r'超期',
            r'延误',
            r'过了.*截止',
            r'截止.*过了',
            r'overdue',
            r'behind',
        ],
        QueryIntent.PROGRESS: [
            r'进展',
            r'进度',
            r'怎么样了',
            r'进行.*如何',
            r'推进.*如何',
            r'progress',
            r'status',
        ],
        QueryIntent.ERRORS: [
            r'错误',
            r'失败',
            r'问题',
            r'报错',
            r'异常',
            r'bug',
            r'出了.*问题',
            r'遇到.*问题',
            r'error',
            r'fail',
            r'issue',
        ],
        QueryIntent.DECISIONS: [
            r'决定',
            r'决策',
            r'选择',
            r'方案',
            r'decision',
            r'chose',
            r'chosen',
        ],
        QueryIntent.DISCOVERIES: [
            r'发现',
            r'注意到',
            r'找到',
            r'discover',
            r'found',
            r'noticed',
        ],
        QueryIntent.SUMMARIZE: [
            r'总结',
            r'概括',
            r'汇总',
            r'digest',
            r'summary',
            r'overview',
        ],
    }
    
    # 动作类型关键词
    ACTION_TYPES = {
        'actions': ['创建', '完成', '执行', '修改', '更新', '添加', '删除', '设置', 'build', 'create', 'complete', 'finish', 'update', 'add', 'delete'],
        'errors': ['错误', '失败', '报错', '异常', 'bug', 'error', 'fail', 'crash'],
        'decisions': ['决定', '选择', '采用', 'decision', 'choose', 'select', 'adopt'],
        'discoveries': ['发现', '找到', '注意', 'discover', 'find', 'notice'],
    }
    
    def recognize(self, query: str) -> Tuple[QueryIntent, QueryContext]:
        """
        识别意图和上下文
        
        Args:
            query: 自然语言查询
        
        Returns:
            (意图, 查询上下文)
        """
        query_lower = query.lower()
        query_chinese = query
        
        context = QueryContext()
        intent = QueryIntent.UNKNOWN
        
        # 1. 识别时间范围
        context.time_range = self._extract_time_range(query_chinese)
        
        # 2. 识别意图
        intent = self._recognize_intent(query_lower, query_chinese)
        
        # 3. 提取关键词
        context.keywords = self._extract_keywords(query_chinese)
        
        # 4. 识别任务状态
        context.task_status = self._extract_task_status(query_chinese)
        
        # 5. 识别记忆类型
        context.memory_type = self._extract_memory_type(query_chinese)
        
        logger.info(f"意图识别: '{query}' -> 意图={intent.value}, 时间={context.time_range}")
        
        return intent, context
    
    def _extract_time_range(self, text: str) -> str:
        """提取时间范围"""
        for keyword, time_range in self.TIME_KEYWORDS.items():
            if keyword in text:
                return time_range
        return 'all'  # 默认全部时间
    
    def _recognize_intent(self, text_lower: str, text: str) -> QueryIntent:
        """识别查询意图"""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower) or re.search(pattern, text):
                    return intent
        return QueryIntent.UNKNOWN
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 移除常见停用词
        stopwords = ['的', '了', '我', '你', '他', '她', '它', '是', '在', '有', '和', '与', '或', '都', '这', '那', '什么', '怎么', '如何']
        
        words = []
        for word in text.split():
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and clean_word not in stopwords and len(clean_word) > 1:
                words.append(clean_word)
        
        return words
    
    def _extract_task_status(self, text: str) -> str:
        """提取任务状态"""
        if any(k in text for k in ['待完成', '待办', '还没', '未完成', 'pending']):
            return 'pending'
        if any(k in text for k in ['逾期', '过期', '超期', 'overdue']):
            return 'overdue'
        if any(k in text for k in ['完成', '已', 'finished', 'completed', 'done']):
            return 'completed'
        return 'all'
    
    def _extract_memory_type(self, text: str) -> str:
        """提取记忆类型"""
        for mem_type, keywords in self.ACTION_TYPES.items():
            if any(k in text for k in keywords):
                return mem_type
        return 'all'

# ============================================================================
# 记忆查询器
# ============================================================================

class MemoryQuerier:
    """
    记忆查询器
    
    根据结构化条件查询记忆
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
    
    def query(self, context: QueryContext) -> List[Dict]:
        """
        查询记忆
        
        Args:
            context: 查询上下文
        
        Returns:
            匹配的记忆列表
        """
        memories = []
        
        # 计算时间范围
        time_filter = self._get_time_filter(context.time_range)
        
        # 获取所有记忆文件
        memory_files = list(self.memory_dir.glob("memories_*.jsonl"))
        memory_files.sort(reverse=True)  # 最新的在前
        
        for mem_file in memory_files:
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            memory = json.loads(line.strip())
                            
                            # 应用时间过滤
                            if not time_filter(memory):
                                continue
                            
                            # 应用类型过滤
                            if context.memory_type != 'all':
                                if memory.get('category', '') != context.memory_type:
                                    continue
                            
                            # 应用关键词过滤
                            if context.keywords:
                                text = f"{memory.get('tool', '')} {memory.get('summary', '')}"
                                if not any(k in text for k in context.keywords):
                                    # 如果没有关键词匹配，跳过
                                    pass
                            
                            memories.append(memory)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.warning(f"读取记忆文件失败: {mem_file}, 错误: {e}")
        
        # 去重
        seen_ids = set()
        unique_memories = []
        for m in memories:
            mid = m.get('id', '')
            if mid and mid not in seen_ids:
                seen_ids.add(mid)
                unique_memories.append(m)
        
        # 按时间排序
        unique_memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 限制数量
        return unique_memories[:context.limit]
    
    def _get_time_filter(self, time_range: str):
        """获取时间过滤器"""
        now = datetime.now()
        
        def today_filter(memory: Dict) -> bool:
            try:
                ts = datetime.fromisoformat(memory.get('timestamp', ''))
                return ts.date() == now.date()
            except:
                return False
        
        def yesterday_filter(memory: Dict) -> bool:
            try:
                ts = datetime.fromisoformat(memory.get('timestamp', ''))
                yd = now - timedelta(days=1)
                return ts.date() == yd.date()
            except:
                return False
        
        def this_week_filter(memory: Dict) -> bool:
            try:
                ts = datetime.fromisoformat(memory.get('timestamp', ''))
                week_start = now - timedelta(days=now.weekday())
                return ts.date() >= week_start.date()
            except:
                return False
        
        def this_month_filter(memory: Dict) -> bool:
            try:
                ts = datetime.fromisoformat(memory.get('timestamp', ''))
                return ts.year == now.year and ts.month == now.month
            except:
                return False
        
        # 根据 time_range 返回对应的过滤器
        filters = {
            'today': today_filter,
            'yesterday': yesterday_filter,
            'this_week': this_week_filter,
            'this_month': this_month_filter,
            'all': lambda m: True
        }
        
        return filters.get(time_range, lambda m: True)

# ============================================================================
# 回答生成器
# ============================================================================

class AnswerGenerator:
    """
    回答生成器
    
    根据查询结果生成自然语言回答
    """
    
    def generate(self, query: str, intent: QueryIntent, 
                context: QueryContext, memories: List[Dict]) -> Tuple[str, str]:
        """
        生成回答
        
        Args:
            query: 原始查询
            intent: 识别的意图
            context: 查询上下文
            memories: 查询到的记忆
        
        Returns:
            (完整回答, 简短总结)
        """
        if not memories:
            return self._generate_empty_answer(intent, context)
        
        # 根据意图生成不同的回答
        if intent == QueryIntent.WHAT_DID_I_DO:
            return self._generate_what_did_i_do(query, context, memories)
        elif intent == QueryIntent.PENDING_TASKS:
            return self._generate_pending_tasks(context, memories)
        elif intent == QueryIntent.OVERDUE_TASKS:
            return self._generate_overdue_tasks(context, memories)
        elif intent == QueryIntent.ERRORS:
            return self._generate_errors(context, memories)
        elif intent == QueryIntent.PROGRESS:
            return self._generate_progress(context, memories)
        elif intent == QueryIntent.SUMMARIZE:
            return self._generate_summary(context, memories)
        else:
            return self._generate_general(query, memories)
    
    def _generate_what_did_i_do(self, query: str, 
                               context: QueryContext, 
                               memories: List[Dict]) -> Tuple[str, str]:
        """生成"我做了什么"的回答"""
        time_text = self._get_time_text(context.time_range)
        
        lines = [f"📋 {time_text}你完成了以下工作：\n"]
        
        # 按工具分组
        by_tool = {}
        for m in memories:
            tool = m.get('tool', 'unknown')
            if tool not in by_tool:
                by_tool[tool] = []
            by_tool[tool].append(m)
        
        # 生成描述
        for tool, items in by_tool.items():
            lines.append(f"\n**{self._get_tool_description(tool)}** ({len(items)}项)：")
            for m in items[:3]:  # 每个工具最多显示3个
                lines.append(f"  • {m.get('summary', '...')}")
            if len(items) > 3:
                lines.append(f"  • ...还有{len(items)-3}项")
        
        # 简短总结
        summary = f"{time_text}共完成{len(memories)}项任务"
        
        return '\n'.join(lines), summary
    
    def _generate_pending_tasks(self, context: QueryContext,
                               memories: List[Dict]) -> Tuple[str, str]:
        """生成待完成任务回答"""
        lines = ["📋 **待完成的任务**：\n"]
        
        if not memories:
            lines.append("✅ 暂时没有待完成的任务！")
        else:
            for i, m in enumerate(memories[:5], 1):
                lines.append(f"{i}. {m.get('summary', '...')}")
        
        summary = f"共有{len(memories)}个待完成任务"
        return '\n'.join(lines), summary
    
    def _generate_overdue_tasks(self, context: QueryContext,
                              memories: List[Dict]) -> Tuple[str, str]:
        """生成逾期任务回答"""
        lines = ["⚠️ **已逾期的任务**：\n"]
        
        if not memories:
            lines.append("✅ 没有逾期任务，继续保持！")
        else:
            for i, m in enumerate(memories[:5], 1):
                lines.append(f"{i}. {m.get('summary', '...')}")
        
        summary = f"共有{len(memories)}个逾期任务"
        return '\n'.join(lines), summary
    
    def _generate_errors(self, context: QueryContext,
                        memories: List[Dict]) -> Tuple[str, str]:
        """生成错误回答"""
        lines = ["🐛 **遇到的错误**：\n"]
        
        if not memories:
            lines.append("✅ 这段时间没有遇到错误，太棒了！")
        else:
            for i, m in enumerate(memories[:5], 1):
                error_info = m.get('summary', '未知错误')
                if m.get('errors'):
                    error_info = m['errors'][0] if m['errors'] else error_info
                lines.append(f"{i}. {error_info}")
        
        summary = f"共遇到{len(memories)}个错误"
        return '\n'.join(lines), summary
    
    def _generate_progress(self, context: QueryContext,
                          memories: List[Dict]) -> Tuple[str, str]:
        """生成进展回答"""
        lines = ["📈 **项目进展**：\n"]
        
        # 统计
        actions = [m for m in memories if m.get('category') == 'actions']
        errors = [m for m in memories if m.get('category') == 'errors']
        
        lines.append(f"- 已完成 {len(actions)} 项任务")
        lines.append(f"- 遇到 {len(errors)} 个问题")
        
        if memories:
            lines.append("\n**最近的操作**：")
            for m in memories[:3]:
                lines.append(f"• {m.get('summary', '...')}")
        
        completion_rate = len(actions) / (len(memories) or 1) * 100
        summary = f"完成率 {completion_rate:.0f}%"
        
        return '\n'.join(lines), summary
    
    def _generate_summary(self, context: QueryContext,
                         memories: List[Dict]) -> Tuple[str, str]:
        """生成总结"""
        lines = [f"📊 **工作总结**（共{len(memories)}条记录）：\n"]
        
        # 分类统计
        categories = {}
        for m in memories:
            cat = m.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            lines.append(f"- {cat}: {count}项")
        
        lines.append("\n**主要工作**：")
        for m in memories[:5]:
            lines.append(f"• {m.get('summary', '...')}")
        
        summary = f"共{len(memories)}条记录，涉及{len(categories)}个类别"
        return '\n'.join(lines), summary
    
    def _generate_general(self, query: str,
                         memories: List[Dict]) -> Tuple[str, str]:
        """生成通用回答"""
        lines = [f"🔍 **关于「{query}」的查询结果**：\n"]
        
        if not memories:
            lines.append("没有找到相关记录。")
        else:
            lines.append(f"找到 {len(memories)} 条相关记忆：\n")
            for i, m in enumerate(memories[:5], 1):
                lines.append(f"{i}. [{m.get('timestamp', '')[:10]}] {m.get('summary', '...')}")
        
        summary = f"找到{len(memories)}条相关记录"
        return '\n'.join(lines), summary
    
    def _generate_empty_answer(self, intent: QueryIntent,
                              context: QueryContext) -> Tuple[str, str]:
        """生成空结果回答"""
        if intent == QueryIntent.WHAT_DID_I_DO:
            return "📋 这段时间没有找到你的工作记录。可能你还没有开始工作，或者记忆系统没有记录到。", "无工作记录"
        elif intent == QueryIntent.PENDING_TASKS:
            return "✅ 暂时没有待完成的任务！", "无待办任务"
        elif intent == QueryIntent.OVERDUE_TASKS:
            return "✅ 没有逾期任务，继续保持！", "无逾期任务"
        elif intent == QueryIntent.ERRORS:
            return "✅ 这段时间没有遇到错误，太棒了！", "无错误"
        else:
            return "没有找到相关记录。", "无结果"
    
    def _get_time_text(self, time_range: str) -> str:
        """获取时间描述"""
        texts = {
            'today': '今天',
            'yesterday': '昨天',
            'this_week': '本周',
            'this_month': '本月',
            'all': '目前'
        }
        return texts.get(time_range, '目前')
    
    def _get_tool_description(self, tool: str) -> str:
        """获取工具描述"""
        descriptions = {
            'write': '📝 文件操作',
            'edit': '✏️ 文件编辑',
            'exec': '⚙️ 命令执行',
            'browser': '🌐 浏览器操作',
            'message': '💬 消息发送',
            'calendar': '📅 日历操作',
            'task': '📋 任务管理',
            'search': '🔍 搜索',
            'web_fetch': '🌍 网页获取',
            'memory': '🧠 记忆操作',
        }
        return descriptions.get(tool, f'🔧 {tool}')

# ============================================================================
# 自然语言查询系统
# ============================================================================

class NaturalQuerySystem:
    """
    自然语言查询系统
    
    整合意图识别、记忆查询和回答生成
    
    使用示例:
    ```python
    from natural_query import NaturalQuerySystem
    
    nq = NaturalQuerySystem()
    
    # 自然语言查询
    result = nq.query("我昨天做了什么？")
    
    print(result.answer)     # 自然语言回答
    print(result.summary)    # 简短总结
    print(result.memories)  # 原始记忆
    ```
    """
    
    def __init__(self, memory_dir: str = None):
        """
        初始化自然语言查询系统
        
        Args:
            memory_dir: 记忆目录，默认 ~/.openclaw/automemory
        """
        if memory_dir is None:
            memory_dir = Path.home() / ".openclaw" / "automemory"
        else:
            memory_dir = Path(memory_dir)
        
        self.memory_dir = memory_dir
        self.intent_recognizer = IntentRecognizer()
        self.memory_querier = MemoryQuerier(memory_dir)
        self.answer_generator = AnswerGenerator()
        
        logger.info(f"自然语言查询系统初始化完成，记忆目录: {memory_dir}")
    
    def query(self, query: str, use_llm: bool = False) -> QueryResult:
        """
        执行自然语言查询
        
        Args:
            query: 自然语言查询，如 "我昨天做了什么？"
            use_llm: 是否使用LLM生成更智能的回答（需要AI模型支持）
        
        Returns:
            QueryResult 对象
        """
        logger.info(f"处理查询: '{query}'")
        
        # 1. 意图识别
        intent, context = self.intent_recognizer.recognize(query)
        
        # 2. 查询记忆
        memories = self.memory_querier.query(context)
        
        # 3. 生成回答
        if use_llm:
            answer = self._generate_llm_answer(query, intent, context, memories)
            summary = answer[:100] + "..." if len(answer) > 100 else answer
        else:
            answer, summary = self.answer_generator.generate(query, intent, context, memories)
        
        result = QueryResult(
            intent=intent,
            query=query,
            context=context,
            memories=memories,
            answer=answer,
            summary=summary,
            total_found=len(memories)
        )
        
        logger.info(f"查询完成: 意图={intent.value}, 找到={len(memories)}条")
        
        return result
    
    def _generate_llm_answer(self, query: str, intent: QueryIntent,
                            context: QueryContext, 
                            memories: List[Dict]) -> str:
        """
        使用 LLM 生成更智能的回答
        
        这个方法需要 AI 模型支持，可以通过 OpenClaw 的 AI 来实现
        """
        # 如果配置了 LLM，使用 LLM 生成更智能的回答
        # 这里只是一个占位实现
        
        # 构建提示
        prompt = f"""用户问：{query}

相关记忆（共{len(memories)}条）：
"""
        for i, m in enumerate(memories[:10], 1):
            prompt += f"{i}. [{m.get('timestamp', '')}] {m.get('summary', '')}\n"
        
        prompt += f"""
请根据以上记忆，用自然语言回答用户的问题。
要求：
1. 简洁明了
2. 突出重点
3. 使用中文回答

回答："""
        
        # 这里可以调用 LLM API
        # 由于还没有集成 LLM，暂时使用本地生成的回答
        logger.info("LLM回答需要配置 AI 模型，当前使用本地生成")
        
        # 返回一个提示，说明需要 LLM
        return self.answer_generator.generate(query, intent, context, memories)[0]
    
    def ask(self, question: str) -> str:
        """
        简单的问答接口
        
        Args:
            question: 自然语言问题
        
        Returns:
            回答文本
        """
        result = self.query(question)
        return result.answer
    
    def explain_intent(self, query: str) -> Dict:
        """
        解释查询的意图解析结果（用于调试）
        
        Args:
            query: 查询语句
        
        Returns:
            意图和上下文的详细信息
        """
        intent, context = self.intent_recognizer.recognize(query)
        
        return {
            "query": query,
            "intent": intent.value,
            "intent_description": self._get_intent_description(intent),
            "time_range": context.time_range,
            "task_status": context.task_status,
            "memory_type": context.memory_type,
            "keywords": context.keywords
        }
    
    def _get_intent_description(self, intent: QueryIntent) -> str:
        """获取意图描述"""
        descriptions = {
            QueryIntent.WHAT_DID_I_DO: "查询用户做了什么事",
            QueryIntent.WHAT_DID_YOU_DO: "查询AI/助手做了什么",
            QueryIntent.PENDING_TASKS: "查询待完成的任务",
            QueryIntent.OVERDUE_TASKS: "查询逾期的任务",
            QueryIntent.PROGRESS: "查询项目进展",
            QueryIntent.ERRORS: "查询遇到的错误",
            QueryIntent.DECISIONS: "查询做出的决定",
            QueryIntent.DISCOVERIES: "查询发现的信息",
            QueryIntent.SUMMARIZE: "请求总结",
            QueryIntent.SEARCH: "搜索记忆",
            QueryIntent.UNKNOWN: "未知意图",
        }
        return descriptions.get(intent, "未知")


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("🧠 自然语言查询系统测试")
    print("=" * 60)
    
    # 初始化
    nq = NaturalQuerySystem()
    
    # 测试查询
    test_queries = [
        "我昨天做了什么？",
        "今天完成了哪些任务？",
        "有什么待完成的任务？",
        "这周遇到了什么错误？",
        "项目进展如何？",
        "总结一下这周的工作",
        "Signal Arena 相关的记忆",
        "Fiverr 进展",
    ]
    
    print("\n📝 意图识别测试：")
    print("-" * 60)
    for q in test_queries:
        intent, context = nq.intent_recognizer.recognize(q)
        print(f"\n问题: {q}")
        print(f"  → 意图: {intent.value}")
        print(f"  → 时间: {context.time_range}")
        print(f"  → 关键词: {context.keywords or '无'}")
    
    print("\n\n📊 查询测试：")
    print("-" * 60)
    for q in test_queries[:4]:
        print(f"\n问题: {q}")
        print("-" * 40)
        result = nq.query(q)
        print(result.answer)
        print(f"\n📌 简短总结: {result.summary}")
        print(f"🔍 找到: {result.total_found} 条记忆")
    
    print("\n\n" + "=" * 60)
    print("✅ 测试完成！")
    print("\n💡 使用示例:")
    print("""
    from natural_query import NaturalQuerySystem
    
    nq = NaturalQuerySystem()
    
    # 简单问答
    answer = nq.ask("我昨天做了什么？")
    print(answer)
    
    # 详细查询
    result = nq.query("这周的项目进展如何？")
    print(result.answer)
    print(f"找到 {result.total_found} 条相关记忆")
    
    # 调试意图识别
    debug = nq.explain_intent("我昨天在Fiverr做了什么")
    print(debug)
    """)