#!/bin/bash
# AutoMemory Pro - 一键安装脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}========================================${NC}"; }

# 安装目录
INSTALL_DIR="${HOME}/.openclaw/plugins/automemory"
REPO_URL="https://github.com/cuiJY-still-in-school/automemory-pro.git"

clear
print_header
echo -e "${BLUE}  🧠 AutoMemory Pro 一键安装${NC}"
echo -e "${BLUE}  让AI真正拥有记忆的OpenClaw插件${NC}"
print_header
echo ""

# 检查依赖
print_info "检查系统环境..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    print_error "未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python版本: $PYTHON_VERSION"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    print_warning "未找到 pip3，尝试安装..."
    python3 -m ensurepip --upgrade || {
        print_error "安装 pip 失败，请手动安装"
        exit 1
    }
fi

# 检查OpenClaw目录
if [ ! -d "${HOME}/.openclaw" ]; then
    print_info "创建 OpenClaw 配置目录..."
    mkdir -p "${HOME}/.openclaw/plugins"
fi

print_success "环境检查通过！"
echo ""

# 选择安装方式
print_info "选择安装方式:"
echo "  1) 从 GitHub 克隆 (推荐，可自动更新)"
echo "  2) 直接下载最新版本"
echo "  3) 从本地目录安装"
echo ""
read -p "请输入选项 (1-3): " choice

case $choice in
    1)
        print_info "从 GitHub 克隆..."
        
        # 如果已存在，先备份
        if [ -d "$INSTALL_DIR" ]; then
            print_warning "检测到已有安装，备份中..."
            mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
        fi
        
        # 克隆仓库
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" || {
            print_error "克隆失败，检查网络连接"
            exit 1
        }
        
        print_success "克隆完成！"
        ;;
        
    2)
        print_info "下载最新版本..."
        
        # 创建临时目录
        TEMP_DIR=$(mktemp -d)
        cd "$TEMP_DIR"
        
        # 下载最新 release
        LATEST_URL="https://github.com/cuiJY-still-in-school/automemory-pro/archive/refs/tags/v1.0.0.tar.gz"
        curl -fsSL "$LATEST_URL" -o automemory-pro.tar.gz || {
            # 尝试从 main 分支下载
            LATEST_URL="https://github.com/cuiJY-still-in-school/automemory-pro/archive/main.tar.gz"
            curl -fsSL "$LATEST_URL" -o automemory-pro.tar.gz || {
                print_error "下载失败，尝试使用 git clone"
                git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" || exit 1
                print_success "克隆完成！"
                return
            }
        }
        
        # 解压
        tar -xzf automemory-pro.tar.gz
        
        # 移动文件
        if [ -d "$INSTALL_DIR" ]; then
            print_warning "检测到已有安装，备份中..."
            mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
        fi
        
        mv automemory-pro-1.0.0 "$INSTALL_DIR"
        
        # 清理
        cd -
        rm -rf "$TEMP_DIR"
        
        print_success "下载完成！"
        ;;
        
    3)
        print_info "本地安装..."
        
        # 如果当前目录就是项目目录
        if [ -f "automemory_pro.py" ]; then
            SOURCE_DIR="$(pwd)"
        else
            read -p "请输入本地项目路径: " SOURCE_DIR
        fi
        
        if [ ! -f "$SOURCE_DIR/automemory_pro.py" ]; then
            print_error "未找到 automemory_pro.py，请确认路径"
            exit 1
        fi
        
        # 备份并安装
        if [ -d "$INSTALL_DIR" ]; then
            print_warning "检测到已有安装，备份中..."
            mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
        fi
        
        cp -r "$SOURCE_DIR" "$INSTALL_DIR"
        
        print_success "本地安装完成！"
        ;;
        
    *)
        print_error "无效选项"
        exit 1
        ;;
esac

echo ""

# 安装依赖
print_info "安装依赖..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    pip3 install -q -r "$INSTALL_DIR/requirements.txt" || {
        print_warning "部分依赖安装失败，但核心功能可用"
    }
fi
print_success "依赖安装完成！"

# 创建配置文件
print_info "创建配置文件..."
CONFIG_FILE="${HOME}/.openclaw/automemory.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "enabled": true,
  "auto_save": true,
  "importance_threshold": 0.5,
  "max_memories_per_session": 50,
  "memory_retention_days": 30,
  "task_tracking": {
    "enabled": true,
    "auto_extract": true,
    "auto_complete_detection": true,
    "overdue_days": 3
  },
  "recommendation": {
    "enabled": true,
    "max_recommendations": 5,
    "recency_weight": 0.5,
    "importance_weight": 0.2,
    "context_weight": 0.3
  }
}
EOF
    print_success "配置文件创建: $CONFIG_FILE"
else
    print_warning "配置文件已存在，保留原配置"
fi

# 创建启动脚本
print_info "创建快捷命令..."
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/automemory" << EOF
#!/bin/bash
# AutoMemory Pro 快捷命令

PLUGIN_DIR="${INSTALL_DIR}"

case "\$1" in
    test)
        python3 "\$PLUGIN_DIR/test_plugin.py"
        ;;
    demo)
        python3 "\$PLUGIN_DIR/demo_pro.py"
        ;;
    visualize)
        python3 "\$PLUGIN_DIR/visualize.py"
        ;;
    status)
        echo "🧠 AutoMemory Pro 状态"
        echo "======================="
        echo "安装路径: \$PLUGIN_DIR"
        echo "记忆目录: \${HOME}/.openclaw/automemory"
        
        if [ -d "\${HOME}/.openclaw/automemory" ]; then
            MEM_COUNT=\$(find "\${HOME}/.openclaw/automemory" -name "memories_*.jsonl" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print \$1}')
            echo "记忆数量: \${MEM_COUNT:-0} 条"
        fi
        ;;
    update)
        echo "正在更新..."
        cd "\$PLUGIN_DIR" && git pull origin main
        echo "更新完成！"
        ;;
    *)
        echo "AutoMemory Pro 快捷命令"
        echo ""
        echo "Usage: automemory [command]"
        echo ""
        echo "Commands:"
        echo "  test       运行测试"
        echo "  demo       运行演示"
        echo "  visualize  显示统计"
        echo "  status     查看状态"
        echo "  update     更新到最新版"
        echo ""
        echo "Examples:"
        echo "  automemory test      # 测试安装"
        echo "  automemory demo      # 查看演示"
        echo "  automemory status    # 查看当前状态"
        ;;
esac
EOF

chmod +x "$BIN_DIR/automemory"

# 检查 PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    print_warning "添加 $BIN_DIR 到 PATH"
    
    # 添加到 .bashrc
    if [ -f "${HOME}/.bashrc" ]; then
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "${HOME}/.bashrc"
    fi
    
    # 添加到 .zshrc
    if [ -f "${HOME}/.zshrc" ]; then
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "${HOME}/.zshrc"
    fi
    
    print_info "请运行: source ~/.bashrc (或 ~/.zshrc) 使命令生效"
fi

print_success "快捷命令创建: automemory"

# 创建 OpenClaw Skill 链接
print_info "创建 OpenClaw Skill..."
SKILL_DIR="${HOME}/.openclaw/skills/automemory"
mkdir -p "$SKILL_DIR"

# 复制 Skill 入口文件
cp "$INSTALL_DIR"/*.py "$SKILL_DIR/" 2>/dev/null || true

# 创建插件链接
PLUGIN_DEST="${HOME}/.openclaw/plugins/automemory"
if [ ! -L "$PLUGIN_DEST" ] && [ ! -d "$PLUGIN_DEST" ]; then
    ln -s "$INSTALL_DIR" "$PLUGIN_DEST"
    print_success "创建插件链接: $PLUGIN_DEST"
fi

print_success "OpenClaw Skill 已配置: $SKILL_DIR"

# 测试安装
echo ""
print_info "测试安装..."
cd "$INSTALL_DIR"
python3 -c "from automemory_pro import AutoMemoryPro; print('✅ 导入成功')" || {
    print_error "安装测试失败"
    exit 1
}
print_success "安装测试通过！"

# 完成
echo ""
print_header
echo -e "${GREEN}  🎉 AutoMemory Pro 安装完成！${NC}"
print_header
echo ""

print_info "安装路径: $INSTALL_DIR"
print_info "记忆目录: ${HOME}/.openclaw/automemory"
print_info "快捷命令: automemory"
echo ""

echo "🚀 快速开始:"
echo "  1. 测试:     automemory test"
echo "  2. 演示:     automemory demo"
echo "  3. 状态:     automemory status"
echo "  4. 可视化:   automemory visualize"
echo ""

echo "💡 使用示例:"
echo "  from automemory_pro import AutoMemoryPro"
echo "  plugin = AutoMemoryPro()"
echo "  recommendations = plugin.on_session_start({"
echo "      'current_task': '你的工作描述'"
echo "  })"
echo ""

echo "📖 文档:"
echo "  详细文档: $INSTALL_DIR/README.md"
echo "  快速上手: $INSTALL_DIR/QUICKSTART.md"
echo "  GitHub:   https://github.com/cuiJY-still-in-school/automemory-pro"
echo ""

print_success "安装成功！让AI拥有记忆！🧠"
echo ""