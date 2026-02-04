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

首先读取 `~/.claude/settings.json` 中的模型配置，获取用户已配置的模型列表：
- `env.ANTHROPIC_DEFAULT_HAIKU_MODEL` - Haiku 模型
- `env.ANTHROPIC_DEFAULT_SONNET_MODEL` - Sonnet 模型
- `env.ANTHROPIC_DEFAULT_OPUS_MODEL` - Opus 模型
- `env.ANTHROPIC_MODEL` - 当前默认模型

然后询问用户选择用于语义搜索的模型（选项从用户配置中动态读取）：

```
请选择用于语义搜索的模型：

1. 继承当前模型（推荐）
   - 使用 ANTHROPIC_MODEL: [从配置读取的值]

2. Haiku（快速、低成本）
   - 使用 [从 ANTHROPIC_DEFAULT_HAIKU_MODEL 读取的值]

3. Sonnet（平衡）
   - 使用 [从 ANTHROPIC_DEFAULT_SONNET_MODEL 读取的值]

4. Opus（最强能力）
   - 使用 [从 ANTHROPIC_DEFAULT_OPUS_MODEL 读取的值]

5. 自定义模型 ID
   - 输入任意模型 ID
```

**注意**：如果用户配置中没有某个模型，则该选项不显示或使用默认值。

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

### 步骤 6：配置摘要内容格式

询问用户选择摘要内容格式：

```
选择摘要文件的内容格式：

1. 结构化摘要（推荐）
   - 包含：会话主题、关键决策、完成任务、问题解决、待办事项
   - 优点：信息组织清晰，便于快速浏览
   - 缺点：格式固定，可能遗漏非结构化信息

2. 自由格式摘要
   - Claude 自由生成一段总结性文字
   - 优点：灵活，能捕捉对话的整体氛围
   - 缺点：格式不统一，不便于快速扫描

3. 混合格式
   - 一段总结性描述 + 关键点列表
   - 优点：兼顾概述和细节
   - 缺点：内容可能较长
```

### 步骤 7：配置摘要生成时机

询问用户选择摘要生成时机：

```
选择摘要生成的时机：

1. 保存时生成（推荐）
   - 执行 /memory save 时调用 API 生成摘要
   - 优点：实时生成，内容最新
   - 缺点：保存操作需等待 API 响应（约 2-5 秒）

2. 异步后台生成
   - 先保存原始对话，后台异步调用 API 生成摘要
   - 优点：保存操作快速，不阻塞用户
   - 缺点：实现复杂，摘要可能延迟生成

3. 按需生成
   - 保存时只存原始对话，搜索时才生成摘要
   - 优点：节省 API 调用，只为需要的内容生成摘要
   - 缺点：首次搜索较慢，摘要质量可能不一致

4. 仅保存原始对话
   - 不生成摘要，只保存格式化的对话内容
   - 优点：保存最快，无需 API 调用
   - 缺点：没有摘要，搜索效果可能较差
```

### 步骤 8：创建配置文件

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
  },
  "summary": {
    "enabled": true,
    "format": "structured",
    "timing": "on_save"
  }
}
```

### 步骤 9：创建数据目录

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

### 步骤 10：安装 Python 依赖

```bash
pip install -r <plugin-path>/scripts/requirements.txt
```

### 步骤 11：验证安装

运行快速测试：
```bash
python <plugin-path>/scripts/memory_core.py status
```

## 成功消息

```
[OK] Claudememv2 配置完成！

配置信息：
  - 模型：[选择的模型]
  - 内容范围：[选择的范围]
  - 最大消息数：[选择的数量]
  - 搜索范围：[选择的范围]
  - 摘要格式：[选择的格式]
  - 摘要时机：[选择的时机]
  - 数据目录：~/.claude/Claudememv2-data/

现在可以使用：
  /Claudememv2:memory save     - 保存当前对话
  /Claudememv2:memory search   - 搜索记忆
  /Claudememv2:memory status   - 查看记忆状态

或使用自然语言：
  "保存对话" / "save conversation"
  "搜索记忆" / "search memory"
```
