#!/bin/bash
# AutoMemory Pro - 一键安装脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/cuiJY-still-in-school/automemory-pro/main/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}========================================${NC}"; }

INSTALL_DIR="${HOME}/.openclaw/plugins/automemory"
REPO_URL="https://github.com/cuiJY-still-in-school/automemory-pro.git"

clear
print_header
echo -e "${BLUE}  🧠 AutoMemory Pro 一键安装${NC}"
echo -e "${BLUE}  让AI真正拥有记忆的OpenClaw插件${NC}"
print_header
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    print_error "未找到 Python3，请先安装"
    exit 1
fi
print_success "Python版本: $(python3 --version | cut -d' ' -f2)"

# 检查目录
mkdir -p "${HOME}/.openclaw/plugins"

print_success "环境检查通过！"
echo ""

# 开始安装
print_info "从 GitHub 克隆..."
echo ""

# 备份旧安装
if [ -d "$INSTALL_DIR" ]; then
    print_warning "检测到已有安装，备份中..."
    mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
fi

# 克隆
git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"

if [ $? -ne 0 ]; then
    print_error "克隆失败，请检查网络连接"
    exit 1
fi

print_success "克隆完成！"
echo ""

# 创建配置文件
print_info "创建配置文件..."
CONFIG_DIR="${HOME}/.openclaw/automemory"
mkdir -p "$CONFIG_DIR"

CONFIG_FILE="$CONFIG_DIR/config.json"
cat > "$CONFIG_FILE" << 'EOFCONFIG'
{
  "enabled": true,
  "auto_save": true,
  "importance_threshold": 0.5,
  "memory_retention_days": 30
}
EOFCONFIG
print_success "配置文件已创建"

# 创建快捷命令
print_info "创建快捷命令..."
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/automemory" << 'EOFBIN'
#!/bin/bash
PLUGIN_DIR="${HOME}/.openclaw/plugins/automemory"

case "$1" in
    test)
        python3 "$PLUGIN_DIR/test_plugin.py"
        ;;
    demo)
        python3 "$PLUGIN_DIR/demo_pro.py"
        ;;
    briefing)
        python3 "$PLUGIN_DIR/daily_briefing.py"
        ;;
    dashboard|dash|board)
        python3 "$PLUGIN_DIR/dashboard.py"
        ;;
    note)
        shift
        python3 "$PLUGIN_DIR/note.py" "$@"
        ;;
    history|hist)
        python3 "$PLUGIN_DIR/history.py" "$2" "$3"
        ;;
    search|find)
        shift
        python3 "$PLUGIN_DIR/search.py" "$@"
        ;;
    achievements|achieve)
        python3 "$PLUGIN_DIR/achievements.py"
        ;;
    status|stat)
        python3 "$PLUGIN_DIR/dashboard.py"
        ;;
    update)
        cd "$PLUGIN_DIR" && git pull origin main
        ;;
    *)
        python3 "$PLUGIN_DIR/dashboard.py"
        ;;
esac
EOFBIN

chmod +x "$BIN_DIR/automemory"
print_success "快捷命令已创建: automemory"

# 测试
print_info "测试安装..."
cd "$INSTALL_DIR"
python3 -c "import sys; sys.path.insert(0, '.'); from automemory_pro import AutoMemoryPro; print('✅ 导入成功')" || {
    print_warning "测试导入失败，但安装已完成"
}

echo ""
print_header
echo -e "${GREEN}  🎉 AutoMemory Pro 安装完成！${NC}"
print_header
echo ""
print_info "安装路径: $INSTALL_DIR"
print_info "记忆目录: ${HOME}/.openclaw/automemory"
echo ""
echo "🚀 快捷命令:"
echo "  automacity          - 仪表盘"
echo "  automacity briefing  - 每日简报"
echo "  automacity note     - 快速笔记"
echo "  automacity history  - 会话历史"
echo "  automacity search   - 智能搜索"
echo "  automacity achieve  - 成就系统"
echo ""
print_success "安装成功！🧠"