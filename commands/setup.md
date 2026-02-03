---
description: 配置 Claudememv2 记忆系统
---

# Claudememv2 安装配置

此命令为 Claude Code 环境配置 Claudememv2 记忆系统。

## 前置条件

- 已安装 Python 3.8+
- Claude Code 已配置 API 访问

## 配置流程

当用户运行 `/Claudememv2:setup` 时，按以下步骤执行：

### 步骤 1：检测环境

1. 检查 Python 安装：
   - Windows: `where python` 或 `where python3`
   - macOS/Linux: `which python3`

2. 检查 Claude Code 配置：
   - 读取 `~/.claude/settings.json` 获取 API 配置

### 步骤 2：配置模型

询问用户选择用于语义搜索的模型：

```
请选择用于语义搜索的模型：

1. 继承 Claude Code 配置（推荐）
   - 自动使用当前 Claude Code 模型设置

2. claude-3-haiku（快速、低成本）

3. claude-3-5-sonnet（平衡）

4. claude-3-opus（最强能力）

5. 自定义模型 ID
   - 输入任意 Anthropic 模型 ID
```

### 步骤 3：配置内容范围

询问用户选择内容保存偏好：

```
选择保存到记忆的内容范围：

1. 完整（推荐）
   - 用户 + 助手 + 工具调用 + 思考过程

2. 标准
   - 用户 + 助手 + 工具调用（无思考过程）

3. 精简
   - 仅用户和助手消息
```

### 步骤 4：配置消息数量限制

询问用户选择消息数量限制：

```
选择每次保存的最大消息数：

1. 全部消息（无限制）
2. 最近 50 条消息
3. 最近 25 条消息（推荐）
4. 最近 15 条消息
5. 自定义数量: ____
```

### 步骤 5：配置搜索范围

询问用户选择搜索范围：

```
选择搜索记忆时的范围：

1. 仅摘要文件（推荐，更快）
   - 搜索精简的对话摘要

2. 仅完整文件
   - 搜索包含工具输入/输出的完整记录

3. 两者都搜索
   - 最全面但较慢
```

### 步骤 6：创建配置文件

在 `~/.claude/plugins/Claudememv2/config.json` 创建配置文件：

```json
{
  "model": {
    "source": "inherit",
    "customModelId": null,
    "fallback": "claude-3-haiku-20240307"
  },
  "memory": {
    "dataDir": "~/.claude/Claudememv2-data",
    "contentScope": "standard",
    "includeThinking": false,
    "includeToolCalls": true,
    "maxMessages": 25,
    "cleanupDays": 90,
    "saveFull": true,
    "searchScope": "summary"
  }
}
```

### 步骤 7：创建数据目录

创建记忆数据目录结构：

**Windows:**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\Claudememv2-data\memory"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\Claudememv2-data\logs"
```

**macOS/Linux:**
```bash
mkdir -p ~/.claude/Claudememv2-data/memory
mkdir -p ~/.claude/Claudememv2-data/logs
```

### 步骤 8：安装 Python 依赖

```bash
pip install -r <plugin-path>/scripts/requirements.txt
```

### 步骤 9：验证安装

运行快速测试：
```bash
python <plugin-path>/scripts/memory_core.py status
```

## 成功消息

```
✓ Claudememv2 配置完成！

配置信息：
  - 模型：[选择的模型]
  - 内容范围：[选择的范围]
  - 最大消息数：[选择的数量]
  - 搜索范围：[选择的范围]
  - 数据目录：~/.claude/Claudememv2-data/

现在可以使用：
  /Claudememv2:memory save     - 保存当前对话
  /Claudememv2:memory search   - 搜索记忆
  /Claudememv2:memory status   - 查看记忆状态

或使用自然语言：
  "保存对话" / "save conversation"
  "搜索记忆" / "search memory"
```
