/**
 * AutoMemory Pro - OpenClaw 集成插件
 * 
 * 功能：
 * 1. 自动保存每轮对话到记忆文件
 * 2. 记录所有工具调用
 * 
 * 作者: ClawQuant
 * 日期: 2026-04-19
 */

const fs = require('fs');
const path = require('path');

const plugin = {
  id: 'automemory',
  name: 'AutoMemory',
  version: '1.0.0',
  
  // 路径配置
  homeDir: process.env.HOME || '/home/jayson2013',
  memoryDir: null,
  memoriesFile: null,
  stats: null,
  
  register(api) {
    console.log('[AutoMemory] 插件注册中...');
    
    // 初始化路径
    this.memoryDir = path.join(this.homeDir, '.openclaw', 'automemory');
    this.memoriesFile = path.join(this.memoryDir, 'memories.jsonl');
    
    // 确保目录存在
    if (!fs.existsSync(this.memoryDir)) {
      fs.mkdirSync(this.memoryDir, { recursive: true });
    }
    
    // 初始化文件
    if (!fs.existsSync(this.memoriesFile)) {
      fs.writeFileSync(this.memoriesFile, '');
    }
    
    // 加载统计
    this.loadStats();
    
    // 注册工具
    this.registerTools(api);
    
    // 注册钩子
    this.registerHooks(api);
    
    console.log('[AutoMemory] 插件注册完成! 🧠');
  },
  
  loadStats() {
    this.stats = {
      totalMemories: 0,
      todayMemories: 0,
      toolsUsed: {}
    };
    
    try {
      if (fs.existsSync(this.memoriesFile)) {
        const content = fs.readFileSync(this.memoriesFile, 'utf-8');
        this.stats.totalMemories = content.trim() ? content.trim().split('\n').length : 0;
        
        const today = new Date().toISOString().slice(0, 10);
        this.stats.todayMemories = content.trim().split('\n').filter(line => {
          try {
            const m = JSON.parse(line);
            return m.timestamp && m.timestamp.startsWith(today);
          } catch { return false; }
        }).length;
      }
    } catch (e) {
      console.log('[AutoMemory] 加载统计失败:', e.message);
    }
  },
  
  addMemory(data) {
    try {
      const memory = {
        id: `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        tool: data.tool || 'message',
        action: data.action || 'send',
        summary: data.summary || '',
        success: data.success !== false,
        error: data.error || null
      };
      
      fs.appendFileSync(this.memoriesFile, JSON.stringify(memory) + '\n');
      
      this.stats.totalMemories++;
      this.stats.todayMemories++;
      
      if (memory.tool) {
        this.stats.toolsUsed[memory.tool] = (this.stats.toolsUsed[memory.tool] || 0) + 1;
      }
      
      return memory;
    } catch (e) {
      console.log('[AutoMemory] 添加记忆失败:', e.message);
      return null;
    }
  },
  
  registerTools(api) {
    // 统计工具
    api.registerTool('automemory_stats', {
      description: '获取AutoMemory统计信息'
    }, async () => {
      return {
        success: true,
        totalMemories: this.stats.totalMemories,
        todayMemories: this.stats.todayMemories,
        toolsUsed: this.stats.toolsUsed
      };
    });
    
    // 简报工具
    api.registerTool('automemory_briefing', {
      description: '生成今日简报'
    }, async () => {
      const today = new Date().toISOString().slice(0, 10);
      const todayMemories = [];
      
      try {
        const content = fs.readFileSync(this.memoriesFile, 'utf-8');
        const lines = content.trim().split('\n');
        for (const line of lines) {
          try {
            const m = JSON.parse(line);
            if (m.timestamp && m.timestamp.startsWith(today)) {
              todayMemories.push(m);
            }
          } catch {}
        }
      } catch {}
      
      const success = todayMemories.filter(m => m.success).length;
      const total = todayMemories.length;
      const rate = total > 0 ? Math.round(success / total * 100) : 100;
      
      return {
        success: true,
        date: today,
        totalActions: total,
        successRate: `${rate}%`,
        errors: total - success
      };
    });
  },
  
  registerHooks(api) {
    // 工具调用后 - 自动记录
    api.on('after_tool_call', (event, ctx, result, error) => {
      this.addMemory({
        tool: event.toolName,
        action: 'execute',
        summary: `执行 ${event.toolName}`,
        success: !error,
        error: error ? error.message : null
      });
    });
  }
};

module.exports = plugin;
