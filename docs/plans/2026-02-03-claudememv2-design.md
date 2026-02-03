# Claudememv2 设计文档

**日期**: 2026-02-03
**版本**: v2.1.0
**状态**: 已批准

## 概述

Claudememv2 是一个为 Claude Code 设计的智能记忆系统，融合了会话自动保存和语义搜索功能。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code 环境                          │
├─────────────────────────────────────────────────────────────┤
│  用户输入                                                    │
│    ↓                                                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Slash 命令      │ OR │ 自然语言触发     │                │
│  │ /memory save    │    │ "保存对话"       │                │
│  └────────┬────────┘    └────────┬────────┘                │
│           └──────────┬───────────┘                          │
│                      ↓                                      │
│  ┌─────────────────────────────────────────┐               │
│  │         Claudememv2 核心引擎             │               │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │               │
│  │  │ 保存    │  │ 搜索    │  │ 索引    │  │               │
│  │  │ 模块    │  │ 模块    │  │ 模块    │  │               │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  │               │
│  └───────┼────────────┼────────────┼───────┘               │
│          ↓            ↓            ↓                        │
│  ┌─────────────────────────────────────────┐               │
│  │           存储层                         │               │
│  │  memory/<project>/*.md  +  memory.sqlite │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## 核心特性

1. **手动命令触发**（v2.1），后续支持 Hook 自动触发（v2.2）
2. **Claude API 语义搜索**（用户可选模型）
3. **混合命令接口**（Slash + 自然语言）
4. **读取 Claude Code 会话文件**
5. **按项目/主题组织存储**
6. **可配置内容范围**（含/不含思考过程、工具调用）
7. **可配置消息数量**（含全部保存选项）
8. **插件方式安装，完整卸载支持**

## 命令接口

| 命令 | 功能 |
|------|------|
| `/memory save` | 保存当前会话 |
| `/memory search <query>` | 搜索记忆 |
| `/memory index` | 索引所有记忆 |
| `/memory status` | 查看状态 |
| `/memory cleanup` | 清理旧记忆 |
| `/memory config` | 修改配置 |

## 自然语言触发

- 保存：保存对话、记住这次会话、save conversation
- 搜索：搜索记忆、查找记忆、search memory
- 索引：索引记忆、更新记忆库、index memory
- 状态：记忆状态、查看记忆、memory status

## 配置选项

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
    "cleanupDays": 90
  }
}
```

## 文件结构

```
~/.claude/Claudememv2-data/
├── memory/
│   ├── <project>/
│   │   ├── 2026-02-03-api-design.md
│   │   └── ...
│   └── ...
├── memory.sqlite
└── logs/
    ├── memory.log
    └── error.log
```

## 安装与卸载

### 安装
```bash
/plugin marketplace add <username>/Claudememv2
/plugin install Claudememv2
/Claudememv2:setup
```

### 卸载
```bash
/plugin uninstall Claudememv2
# 或使用 /Claudememv2:uninstall
```

## 相关文档

- [备选方案](./alternatives.md)
- [v2.2 Hook 设计](./v2.2-hook-design.md)
