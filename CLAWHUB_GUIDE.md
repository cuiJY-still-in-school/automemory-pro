# ClawHub 发布指南

## 🎯 AutoMemory Pro 发布到 ClawHub

ClawHub 是 OpenClaw 的官方插件市场。

---

## 📋 发布步骤

### 1. 访问 ClawHub

打开浏览器访问：
```
https://clawhub.ai/publish/plugin
```

### 2. 登录 GitHub

点击 "Sign in with GitHub" 按钮，使用你的 GitHub 账号登录。

### 3. 填写插件信息

按照页面提示填写：

#### 基本信息
- **Plugin Name**: `AutoMemory Pro`
- **Plugin ID**: `automemory-pro`
- **Version**: `1.4.0`
- **Description**: `让AI真正拥有记忆和智慧的OpenClaw插件`

#### 详细信息
- **Long Description**: 复制 `clawhub.json` 中的 `longDescription` 内容
- **Author**: ClawQuant
- **GitHub**: cuiJY-still-in-school

#### 分类标签
- memory
- ai
- productivity
- automation
- openclaw

#### 仓库地址
```
https://github.com/cuiJY-still-in-school/automemory-pro
```

#### 入口文件
```
automemory_pro.py
```

#### 其他
- **License**: MIT
- **Python Version**: 3.8+
- **OpenClaw Version**: >=1.0.0

---

## 📁 准备好的文件

### 1. plugin.json
位于: `~/.openclaw/plugins/automemory/plugin.json`

```json
{
  "name": "AutoMemory Pro",
  "version": "1.4.0",
  "description": "让AI真正拥有记忆和智慧的OpenClaw插件",
  "author": "ClawQuant",
  "repository": "https://github.com/cuiJY-still-in-school/automemory-pro"
}
```

### 2. clawhub.json
位于: `~/.openclaw/plugins/automemory/clawhub.json`

这是 ClawHub 格式的完整配置，包含详细描述。

---

## 🎨 插件图标建议

建议上传一个图标：
- 尺寸：512x512px
- 格式：PNG 或 SVG
- 主题：大脑/记忆/AI 相关

图标可以包含：
- 🧠 大脑图标
- 💡 灯泡（智慧）
- 🔗 连接线（记忆网络）

---

## ✅ 发布检查清单

发布前确认：

- [ ] GitHub 账号已登录 ClawHub
- [ ] 填写了插件名称
- [ ] 填写了描述
- [ ] 添加了标签 (memory, ai, productivity)
- [ ] 链接了 GitHub 仓库
- [ ] 指定了入口文件
- [ ] 选择了 MIT 许可证
- [ ] 点击了 "Publish" 按钮

---

## 📝 发布后的信息

发布成功后，你的插件会显示在：
```
https://clawhub.ai/plugins/automemory-pro
```

格式：`@cuiJY-still-in-school/automemory-pro`

---

## 🚀 其他用户安装

其他用户可以通过以下方式安装：

```bash
# 克隆仓库
git clone https://github.com/cuiJY-still-in-school/automemory-pro.git

# 安装
cd automemory-pro
mkdir -p ~/.openclaw/plugins/automemory
cp *.py *.json ~/.openclaw/plugins/automemory/
```

或在 ClawHub 页面上点击 "Install"。

---

## 📞 需要帮助？

查看 ClawHub 文档：
- https://clawhub.ai/about
- https://docs.openclaw.ai

或查看 OpenClaw 社区。

---

**祝你发布成功！🚀**