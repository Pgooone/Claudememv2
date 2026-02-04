# Claudememv2

为 Claude Code 设计的智能记忆系统 - 保存对话、AI 摘要生成、语义搜索、跨会话知识检索。

[English](#english) | 中文

---

## 功能特性

- **AI 摘要生成**：使用 Claude API 自动生成结构化对话摘要
- **保存对话**：手动将 Claude Code 会话保存到可搜索的记忆库
- **语义搜索**：使用 Claude API 进行智能语义匹配搜索
- **项目组织**：记忆按项目自动分类存储
- **可配置内容**：选择保存内容（消息、工具调用、思考过程）
- **自然语言**：支持命令和自然语言触发

## 安装

### 从 GitHub 市场安装

```bash
# 添加市场源
/plugin marketplace add Pgooone/Claudememv2

# 安装插件
/plugin install Claudememv2

# 运行配置
/Claudememv2:setup
```

### 本地安装

```bash
# 克隆仓库
git clone https://github.com/Pgooone/Claudememv2.git

# 本地安装
/plugin install --local /path/to/Claudememv2

# 运行配置
/Claudememv2:setup
```

## 使用方法

### Slash 命令

| 命令 | 说明 |
|------|------|
| `/Claudememv2:memory save` | 保存当前对话到记忆 |
| `/Claudememv2:memory search <查询>` | 搜索记忆 |
| `/Claudememv2:memory index` | 索引所有记忆文件 |
| `/Claudememv2:memory status` | 查看记忆系统状态 |
| `/Claudememv2:memory cleanup` | 清理旧记忆 |
| `/Claudememv2:memory config` | 查看或修改配置 |

### 自然语言触发

你也可以使用自然语言：

- **保存**："保存对话"、"记住这次会话"、"save conversation"
- **搜索**："搜索记忆：API设计"、"查找记忆"
- **索引**："索引记忆"、"更新记忆库"
- **状态**："记忆状态"、"查看记忆"

## 配置

配置文件位于 `~/.claude/plugins/Claudememv2/config.json`：

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

### 模型选项

安装时从 Claude Code 配置中动态读取可用模型：
1. **继承当前模型**（推荐）- 使用 `ANTHROPIC_MODEL` 配置的模型
2. **Haiku** - 使用 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 配置的模型（快速、低成本）
3. **Sonnet** - 使用 `ANTHROPIC_DEFAULT_SONNET_MODEL` 配置的模型（平衡）
4. **Opus** - 使用 `ANTHROPIC_DEFAULT_OPUS_MODEL` 配置的模型（最强能力）
5. **自定义** - 输入任意 Anthropic 模型 ID

### 内容范围选项

- **full（完整）** - 用户 + 助手 + 工具调用 + 思考过程
- **standard（标准）** - 用户 + 助手 + 工具调用（无思考过程）
- **minimal（精简）** - 仅用户和助手消息

### 搜索范围选项

- **summary（摘要）** - 仅搜索摘要文件（默认，更快）
- **full（完整）** - 仅搜索完整文件（含工具输入/输出）
- **both（两者）** - 搜索摘要和完整文件

### AI 摘要格式选项

- **structured（结构化）** - 会话主题、关键决策、完成任务、问题解决、待办事项
- **freeform（自由格式）** - Claude 自由生成一段总结性文字
- **mixed（混合格式）** - 概述 + 关键点列表

### AI 摘要生成时机

- **on_save（保存时）** - 执行保存命令时生成摘要（推荐）
- **async（异步）** - 后台异步生成摘要
- **on_demand（按需）** - 搜索时才生成摘要
- **disabled（禁用）** - 不生成 AI 摘要

## 数据存储

记忆存储在 `~/.claude/Claudememv2-data/`：

```
~/.claude/Claudememv2-data/
├── memory/
│   ├── 项目A/
│   │   ├── 2026-02-03-api-design.md      # AI 摘要文件
│   │   ├── 2026-02-03-bug-fix.md
│   │   └── full/                          # 完整对话目录
│   │       ├── 2026-02-03-api-design.md  # 含工具输入/输出
│   │       └── 2026-02-03-bug-fix.md
│   └── 项目B/
│       └── ...
├── memory.sqlite
└── logs/
```

### 摘要文件示例

```markdown
---
project: my-project
created: 2026-02-04T12:00:00
summary_format: structured
has_ai_summary: true
---

# 会话记录: 2026-02-04 12:00:00

## 元数据
- **项目**: my-project
- **消息数**: 25

## 会话主题
实现用户认证功能

## 关键决策和结论
- 使用 JWT 进行身份验证
- 密码使用 bcrypt 加密

## 完成的任务
- [x] 创建用户模型
- [x] 实现登录接口

## 遇到的问题和解决方案
- **问题**: Token 过期处理
  **解决**: 添加刷新 Token 机制

## 后续待办
- [ ] 添加密码重置功能
```

## 卸载

### 使用插件命令卸载（推荐）

```bash
/plugin uninstall Claudememv2
```

### 手动卸载

详见 [UNINSTALL.md](UNINSTALL.md)。

## 系统要求

- Claude Code
- Python 3.8+
- Anthropic API 访问权限（用于语义搜索）

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)

## 贡献

欢迎贡献！请随时提交 Issue 和 Pull Request。

---

<a name="english"></a>
# English

Intelligent memory system for Claude Code - save conversations, AI summary generation, semantic search, and cross-session knowledge retrieval.

## Features

- **AI Summary Generation**: Automatically generate structured conversation summaries using Claude API
- **Save Conversations**: Manually save Claude Code sessions to searchable memory
- **Semantic Search**: Find relevant memories using Claude API for intelligent matching
- **Project Organization**: Memories automatically organized by project
- **Configurable Content**: Choose what to save (messages, tool calls, thinking process)
- **Natural Language**: Use commands or natural language triggers

## Installation

### From GitHub Marketplace

```bash
# Add marketplace source
/plugin marketplace add Pgooone/Claudememv2

# Install plugin
/plugin install Claudememv2

# Run setup
/Claudememv2:setup
```

### Local Installation

```bash
# Clone repository
git clone https://github.com/Pgooone/Claudememv2.git

# Install locally
/plugin install --local /path/to/Claudememv2

# Run setup
/Claudememv2:setup
```

## Usage

### Slash Commands

| Command | Description |
|---------|-------------|
| `/Claudememv2:memory save` | Save current conversation to memory |
| `/Claudememv2:memory search <query>` | Search memories |
| `/Claudememv2:memory index` | Index all memory files |
| `/Claudememv2:memory status` | View memory system status |
| `/Claudememv2:memory cleanup` | Clean up old memories |
| `/Claudememv2:memory config` | View or modify configuration |

### Natural Language

You can also use natural language:

- **Save**: "保存对话", "save conversation", "remember this"
- **Search**: "搜索记忆：API设计", "search memory for API"
- **Index**: "索引记忆", "update memory index"
- **Status**: "记忆状态", "memory status"

## Configuration

Configuration is stored at `~/.claude/plugins/Claudememv2/config.json`:

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

### Model Options

Models are dynamically read from your Claude Code configuration during setup:
1. **Inherit current model** (Recommended) - Uses model from `ANTHROPIC_MODEL`
2. **Haiku** - Uses model from `ANTHROPIC_DEFAULT_HAIKU_MODEL` (fast, low cost)
3. **Sonnet** - Uses model from `ANTHROPIC_DEFAULT_SONNET_MODEL` (balanced)
4. **Opus** - Uses model from `ANTHROPIC_DEFAULT_OPUS_MODEL` (most capable)
5. **Custom** - Enter any Anthropic model ID

### Content Scope Options

- **full** - user + assistant + tool calls + thinking process
- **standard** - user + assistant + tool calls (no thinking)
- **minimal** - user + assistant messages only

### Search Scope Options

- **summary** - Search summary files only (default, faster)
- **full** - Search full files only (with tool I/O)
- **both** - Search both summary and full files

### AI Summary Format Options

- **structured** - Session topic, key decisions, completed tasks, problem solutions, todos
- **freeform** - Claude generates a free-form summary paragraph
- **mixed** - Overview + key points list

### AI Summary Timing Options

- **on_save** - Generate summary when saving (recommended)
- **async** - Generate summary asynchronously in background
- **on_demand** - Generate summary only when searching
- **disabled** - Do not generate AI summary

## Data Storage

Memories are stored at `~/.claude/Claudememv2-data/`:

```
~/.claude/Claudememv2-data/
├── memory/
│   ├── project-a/
│   │   ├── 2026-02-03-api-design.md      # AI Summary file
│   │   ├── 2026-02-03-bug-fix.md
│   │   └── full/                          # Full conversation directory
│   │       ├── 2026-02-03-api-design.md  # With tool I/O
│   │       └── 2026-02-03-bug-fix.md
│   └── project-b/
│       └── ...
├── memory.sqlite
└── logs/
```

### Summary File Example

```markdown
---
project: my-project
created: 2026-02-04T12:00:00
summary_format: structured
has_ai_summary: true
---

# Session: 2026-02-04 12:00:00

## Metadata
- **Project**: my-project
- **Messages**: 25

## Session Topic
Implement user authentication feature

## Key Decisions and Conclusions
- Use JWT for authentication
- Encrypt passwords with bcrypt

## Completed Tasks
- [x] Create user model
- [x] Implement login endpoint

## Problems and Solutions
- **Problem**: Token expiration handling
  **Solution**: Add refresh token mechanism

## Todos
- [ ] Add password reset feature
```

## Uninstallation

### Using Plugin Command (Recommended)

```bash
/plugin uninstall Claudememv2
```

### Manual Uninstallation

See [UNINSTALL.md](UNINSTALL.md) for detailed instructions.

## Requirements

- Claude Code
- Python 3.8+
- Anthropic API access (for semantic search)

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
