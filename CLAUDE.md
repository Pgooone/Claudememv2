# Claudememv2 项目指南

本文件为 Claude Code 在处理此项目时提供上下文。

## 项目概述

Claudememv2 是一个为 Claude Code 设计的智能记忆系统插件，支持：
- 将对话保存到可搜索的记忆库
- 使用 Claude API 进行语义搜索
- 按项目组织记忆

## 目录结构

```
Claudememv2/
├── .claude-plugin/          # 插件配置
│   ├── plugin.json          # 插件元数据
│   └── marketplace.json     # 市场配置
├── commands/                # Slash 命令定义
│   ├── setup.md             # /Claudememv2:setup
│   ├── memory.md            # /memory 命令
│   └── uninstall.md         # /Claudememv2:uninstall
├── skills/                  # 自然语言触发
│   └── memory/SKILL.md
├── scripts/                 # Python 核心
│   ├── memory_core.py       # 主入口
│   ├── session_parser.py    # 会话解析器
│   ├── search_engine.py     # 搜索实现
│   └── requirements.txt
├── docs/                    # 文档
│   ├── alternatives.md      # 备选方案
│   ├── v2.2-hook-design.md  # 未来 Hook 设计
│   └── plans/               # 设计文档
└── README.md
```

## 关键文件

- `scripts/memory_core.py` - 主 CLI 入口
- `scripts/session_parser.py` - 解析 Claude Code 会话文件
- `scripts/search_engine.py` - 使用 Claude API 的语义搜索
- `commands/memory.md` - 定义 /memory 命令行为

## 开发说明

- 使用 Claude API 进行语义搜索（可配置模型）
- 从 `~/.claude/projects/` 读取 Claude Code 会话
- 记忆存储在 `~/.claude/Claudememv2-data/`
- SQLite + FTS5 用于全文搜索

## 测试

```bash
# 测试记忆保存
python scripts/memory_core.py save

# 测试搜索
python scripts/memory_core.py search "测试查询"

# 测试状态
python scripts/memory_core.py status
```
