# Claudememv2 摘要生成功能设计

**日期**: 2026-02-04
**版本**: v2.2.3
**状态**: 已实现

## 概述

当前摘要文件只是简单复制对话内容，没有真正的"摘要"功能。本设计添加使用 Claude API 生成结构化摘要的能力。

## 需求

1. 摘要内容格式可配置（安装时选择）
2. 摘要生成时机可配置（安装时选择）
3. 保持与现有功能的兼容性

## 配置选项

### 摘要内容格式

| 选项 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| `structured` | 结构化摘要：会话主题、关键决策、完成任务、问题解决、待办事项 | 信息组织清晰，便于快速浏览 | 格式固定，可能遗漏非结构化信息 |
| `freeform` | 自由格式：Claude 自由生成一段总结性文字 | 灵活，能捕捉对话的整体氛围 | 格式不统一，不便于快速扫描 |
| `mixed` | 混合格式：一段总结性描述 + 关键点列表 | 兼顾概述和细节 | 内容可能较长 |

### 摘要生成时机

| 选项 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| `on_save` | 保存时生成 | 实时生成，内容最新 | 保存操作需等待 API 响应（约 2-5 秒） |
| `async` | 异步后台生成 | 保存操作快速，不阻塞用户 | 实现复杂，摘要可能延迟生成 |
| `on_demand` | 按需生成（搜索时） | 节省 API 调用 | 首次搜索较慢，摘要质量可能不一致 |
| `disabled` | 仅保存原始对话 | 保存最快，无需 API 调用 | 没有摘要，搜索效果可能较差 |

## 配置文件结构

```json
{
  "model": { ... },
  "memory": { ... },
  "summary": {
    "enabled": true,
    "format": "structured",
    "timing": "on_save"
  }
}
```

## Prompt 模板

### 结构化摘要 (structured)

```
基于以下对话内容，生成一个结构化摘要。请严格按照以下格式输出：

## 会话主题
[一句话描述本次会话的主要目标或主题]

## 关键决策和结论
- [决策/结论 1]
- [决策/结论 2]
...

## 完成的任务
- [x] [任务 1]
- [x] [任务 2]
...

## 遇到的问题和解决方案
- **问题**: [问题描述]
  **解决**: [解决方案]
...

## 后续待办
- [ ] [待办 1]
- [ ] [待办 2]
...

如果某个部分没有相关内容，写"无"。

---
对话内容：
{conversation}
```

### 自由格式摘要 (freeform)

```
基于以下对话内容，生成一段简洁的总结（150-300字）。
重点描述：做了什么、为什么这样做、结果如何。

对话内容：
{conversation}
```

### 混合格式摘要 (mixed)

```
基于以下对话内容，生成摘要。格式如下：

## 概述
[2-3句话总结本次会话]

## 关键点
- [要点 1]
- [要点 2]
- [要点 3]
...

对话内容：
{conversation}
```

## 实现方案

### 需要修改的文件

| 文件 | 修改内容 |
|------|----------|
| `commands/setup.md` | 添加摘要格式和生成时机的配置选项 |
| `scripts/session_parser.py` | 添加 `generate_summary()` 方法 |
| `scripts/memory_core.py` | 更新 `cmd_save()` 支持不同生成时机 |

### 核心方法：generate_summary()

```python
def generate_summary(self, messages: list) -> str:
    """使用 Claude API 生成对话摘要"""
    summary_config = self.config.get("summary", {})

    if not summary_config.get("enabled", True):
        return None

    format_type = summary_config.get("format", "structured")

    # 准备对话内容
    conversation = self._format_conversation_for_summary(messages)

    # 选择对应的 prompt 模板
    prompt = self._get_summary_prompt(format_type, conversation)

    # 调用 Claude API
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=self._get_model(),
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
```

### 摘要文件结构

```markdown
---
project: xxx
created: 2026-02-04T...
type: summary
summary_format: structured
---

# 会话摘要

[AI 生成的摘要内容]

---

# 原始对话

[格式化的对话内容]
```

## 注意事项

1. 保持 `maxMessages` 为 `null` 时的兼容性（已修复的 bug）
2. API 调用失败时优雅降级，仍保存原始对话
3. 异步模式需要额外的状态管理

## 安装流程更新

在 `/Claudememv2:setup` 中添加两个新问题：
1. 选择摘要内容格式（显示优缺点）
2. 选择摘要生成时机（显示优缺点）
