---
name: memory
description: Claude Code 智能记忆系统 - 保存和搜索对话
triggers:
  - 保存对话
  - 记住这次会话
  - 保存到记忆
  - save conversation
  - remember this
  - save this chat
  - 搜索记忆
  - 查找记忆
  - 在记忆中搜索
  - search memory
  - find in memory
  - 索引记忆
  - 更新记忆库
  - 重建索引
  - index memory
  - 记忆状态
  - 查看记忆
  - memory status
---

# 记忆技能

此技能提供对 Claudememv2 记忆系统的自然语言访问。

## 重要：执行方式

**必须通过 Python 脚本执行所有操作，不要自行实现逻辑。**

### 脚本位置

首先使用 Glob 工具查找脚本路径：
- Windows: `C:\Users\*\.claude\plugins\cache\Claudememv2\Claudememv2\*\scripts\memory_core.py`
- Unix: `~/.claude/plugins/cache/Claudememv2/Claudememv2/*/scripts/memory_core.py`

或者直接使用以下路径模式（选择最新版本）：
```
# Windows
%USERPROFILE%\.claude\plugins\cache\Claudememv2\Claudememv2\<version>\scripts\memory_core.py

# Unix
~/.claude/plugins/cache/Claudememv2/Claudememv2/<version>/scripts/memory_core.py
```

### 执行命令

找到脚本路径后，使用 Bash 工具执行：

```bash
# 保存
python "<script_path>" save

# 搜索
python "<script_path>" search "<query>"

# 索引
python "<script_path>" index

# 状态
python "<script_path>" status

# 清理
python "<script_path>" cleanup
```

## 触发词检测

当用户消息匹配以下任何模式时，激活此技能：

### 保存触发词
- 中文："保存对话"、"记住这次会话"、"保存到记忆"、"保存这次对话"
- 英文："save conversation"、"remember this"、"save this chat"、"save to memory"

### 搜索触发词
- 中文："搜索记忆"、"查找记忆"、"在记忆中搜索"、"搜索：XXX"
- 英文："search memory"、"find in memory"、"search for XXX in memory"

### 索引触发词
- 中文："索引记忆"、"更新记忆库"、"重建索引"
- 英文："index memory"、"update memory index"、"rebuild index"

### 状态触发词
- 中文："记忆状态"、"查看记忆"、"记忆库状态"
- 英文："memory status"、"show memory"、"memory info"

## 操作流程

### 保存触发时

1. 使用 Glob 工具查找 `memory_core.py` 脚本路径
2. 使用 Bash 工具执行：`python "<script_path>" save`
3. 将脚本输出展示给用户

**预期输出：**
```
[OK] Session saved to memory
  File: <file_path>
  Messages: <count>
  Project: <project>
```

### 搜索触发时

1. 从用户消息提取查询（例如："搜索记忆：API设计" → 查询 = "API设计"）
2. 使用 Glob 工具查找脚本路径
3. 使用 Bash 工具执行：`python "<script_path>" search "<query>"`
4. 将脚本输出展示给用户

### 索引触发时

1. 使用 Glob 工具查找脚本路径
2. 使用 Bash 工具执行：`python "<script_path>" index`
3. 将脚本输出展示给用户

### 状态触发时

1. 使用 Glob 工具查找脚本路径
2. 使用 Bash 工具执行：`python "<script_path>" status`
3. 将脚本输出展示给用户

## 配置

此技能从 `~/.claude/plugins/Claudememv2/config.json` 读取配置。

## 错误处理

如果脚本执行失败，将错误信息展示给用户。根据触发语言（从触发词检测）提供相应语言的错误消息。
