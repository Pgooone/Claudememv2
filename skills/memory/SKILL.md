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

## 操作

### 保存触发时

执行记忆保存流程：

1. 获取当前工作目录
2. 从目录提取项目名称
3. 定位 Claude Code 会话文件
4. 根据配置解析和过滤消息
5. 通过 Claude API 生成 slug
6. 保存到 `~/.claude/Claudememv2-data/memory/<project>/YYYY-MM-DD-slug.md`
7. 更新索引

**响应：**
```
✓ 会话已保存到记忆
  文件：<file_path>
  消息数：<count>
  项目：<project>
```

### 搜索触发时

从用户消息提取查询并搜索：

1. 从消息解析查询（例如："搜索记忆：API设计" → 查询 = "API设计"）
2. 使用查询调用搜索引擎
3. 返回格式化结果

**响应：**
```
🔍 搜索结果（查询："<query>"）

1. [<score>] <file>:<lines>
   "<excerpt>..."

2. ...
```

### 索引触发时

执行索引更新：

1. 扫描记忆目录
2. 索引新增/修改的文件
3. 报告结果

**响应：**
```
📚 记忆索引已更新
  扫描文件：<count>
  新增索引：<new>
  总分块数：<chunks>
```

### 状态触发时

显示记忆系统状态：

**响应：**
```
📊 Claudememv2 记忆库状态
  项目数：<projects>
  文件数：<files>
  总大小：<size>
  最近更新：<date>
  模型：<model>
```

## 配置

此技能从 `~/.claude/plugins/Claudememv2/config.json` 读取配置。

## 错误处理

如果任何操作失败，根据触发语言（从触发词检测）提供相应语言的错误消息。
