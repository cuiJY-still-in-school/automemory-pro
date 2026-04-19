#!/usr/bin/env python3
"""
AutoMemory Pro - API服务
Simple API - 提供HTTP API访问记忆

用法:
    api start [--port 8080]     # 启动API服务
    api stop                     # 停止服务
    api status                   # 查看状态

作者: ClawQuant
日期: 2026-04-19
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 静默日志
import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

PLUGIN_DIR = Path(__file__).parent
MEMORY_DIR = Path.home() / ".openclaw" / "automemory"
API_CONFIG = MEMORY_DIR / "api_config.json"
sys.path.insert(0, str(PLUGIN_DIR))


def load_config() -> dict:
    """加载配置"""
    if API_CONFIG.exists():
        try:
            with open(API_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"port": 8080, "enabled": False}


def save_config(config: dict):
    """保存配置"""
    with open(API_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f)


def get_memories(limit: int = 100) -> list:
    """获取记忆"""
    memories = []
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl"), reverse=True):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        memories.append(json.loads(line.strip()))
                        if len(memories) >= limit:
                            break
                    except:
                        continue
        except:
            continue
        if len(memories) >= limit:
            break
    
    return memories


def get_stats() -> dict:
    """获取统计"""
    stats = {
        "total": 0,
        "today": 0,
        "by_tool": {},
        "success_rate": 0
    }
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    success = 0
    total = 0
    
    for mem_file in sorted(MEMORY_DIR.glob("memories_*.jsonl")):
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        m = json.loads(line.strip())
                        stats["total"] += 1
                        total += 1
                        
                        if m.get('timestamp', '').startswith(today_str):
                            stats["today"] += 1
                        
                        tool = m.get('tool', 'unknown')
                        stats["by_tool"][tool] = stats["by_tool"].get(tool, 0) + 1
                        
                        if m.get('success', True):
                            success += 1
                    
                    except:
                        continue
        except:
            continue
    
    if total > 0:
        stats["success_rate"] = success / total * 100
    
    return stats


class APIHandler(BaseHTTPRequestHandler):
    """API处理器"""
    
    def log_message(self, format, *args):
        """静默日志"""
        pass
    
    def send_json(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/stats':
            # 统计
            self.send_json(get_stats())
        
        elif path == '/api/memories':
            # 记忆列表
            params = parse_qs(parsed.query)
            limit = int(params.get('limit', [100])[0])
            self.send_json(get_memories(limit))
        
        elif path == '/api/health':
            # 健康检查
            self.send_json({"status": "ok", "timestamp": datetime.now().isoformat()})
        
        elif path == '/':
            # 欢迎页面
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>AutoMemory API</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🧠 AutoMemory API</h1>
    <p>API服务已启动！</p>
    <h2>可用端点:</h2>
    <ul>
        <li><code>/api/stats</code> - 统计信息</li>
        <li><code>/api/memories</code> - 记忆列表</li>
        <li><code>/api/health</code> - 健康检查</li>
    </ul>
    <h2>示例:</h2>
    <pre>curl http://localhost:8080/api/stats</pre>
    <pre>curl http://localhost:8080/api/memories?limit=10</pre>
</body>
</html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        
        else:
            self.send_json({"error": "Not found"}, 404)


def start_server(port: int = 8080):
    """启动服务器"""
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🚀 API服务已启动: http://0.0.0.0:{port}")
    print(f"   统计: http://localhost:{port}/api/stats")
    print(f"   记忆: http://localhost:{port}/api/memories")
    print()
    print("按 Ctrl+C 停止服务")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  服务已停止")
        server.shutdown()


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] == "-h" or args[0] == "--help":
        print("""
🌐 AutoMemory API服务

用法:
    api start [--port 8080]    启动API服务
    api stop                    停止服务
    api status                  查看状态

API端点:
    GET /api/stats              统计信息
    GET /api/memories?limit=N  记忆列表
    GET /api/health             健康检查

示例:
    api start --port 8080
    curl http://localhost:8080/api/stats
""")
        return
    
    config = load_config()
    
    if args[0] == "start":
        port = config.get("port", 8080)
        if "--port" in args:
            idx = args.index("--port")
            port = int(args[idx + 1]) if idx + 1 < len(args) else 8080
        
        config["enabled"] = True
        config["port"] = port
        save_config(config)
        
        start_server(port)
    
    elif args[0] == "status":
        if config.get("enabled"):
            print(f"✅ API服务已配置")
            print(f"   端口: {config.get('port', 8080)}")
        else:
            print("❌ API服务未启用")
    
    elif args[0] == "stop":
        config["enabled"] = False
        save_config(config)
        print("✅ API服务已停止")


if __name__ == "__main__":
    main()
