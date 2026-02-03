# Claudememv2

为 Claude Code 设计的智能记忆系统 - 保存对话、语义搜索、跨会话知识检索。

[English](#english) | 中文

---

## 功能特性

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
  }
}
```

### 模型选项

安装时可选择：
1. **继承 Claude Code 配置**（推荐）- 使用当前 Claude Code 模型设置
2. **claude-3-haiku** - 快速、低成本
3. **claude-3-5-sonnet** - 平衡
4. **claude-3-opus** - 最强能力
5. **自定义** - 任意 Anthropic 模型 ID

### 内容范围选项

- **full（完整）** - 用户 + 助手 + 工具调用 + 思考过程
- **standard（标准）** - 用户 + 助手 + 工具调用（无思考过程）
- **minimal（精简）** - 仅用户和助手消息

### 搜索范围选项

- **summary（摘要）** - 仅搜索摘要文件（默认，更快）
- **full（完整）** - 仅搜索完整文件（含工具输入/输出）
- **both（两者）** - 搜索摘要和完整文件

## 数据存储

记忆存储在 `~/.claude/Claudememv2-data/`：

```
~/.claude/Claudememv2-data/
├── memory/
│   ├── 项目A/
│   │   ├── 2026-02-03-api-design.md      # 摘要文件
│   │   ├── 2026-02-03-bug-fix.md
│   │   └── full/                          # 完整文件目录
│   │       ├── 2026-02-03-api-design.md  # 含工具输入/输出
│   │       └── 2026-02-03-bug-fix.md
│   └── 项目B/
│       └── ...
├── memory.sqlite
└── logs/
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

Intelligent memory system for Claude Code - save conversations, semantic search, and cross-session knowledge retrieval.

## Features

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
  }
}
```

### Model Options

During setup, you can choose:
1. **Inherit from Claude Code** (Recommended) - Uses your current Claude Code model
2. **claude-3-haiku** - Fast, low cost
3. **claude-3-5-sonnet** - Balanced
4. **claude-3-opus** - Most capable
5. **Custom** - Any Anthropic model ID

### Content Scope Options

- **full** - user + assistant + tool calls + thinking process
- **standard** - user + assistant + tool calls (no thinking)
- **minimal** - user + assistant messages only

### Search Scope Options

- **summary** - Search summary files only (default, faster)
- **full** - Search full files only (with tool I/O)
- **both** - Search both summary and full files

## Data Storage

Memories are stored at `~/.claude/Claudememv2-data/`:

```
~/.claude/Claudememv2-data/
├── memory/
│   ├── project-a/
│   │   ├── 2026-02-03-api-design.md      # Summary file
│   │   ├── 2026-02-03-bug-fix.md
│   │   └── full/                          # Full files directory
│   │       ├── 2026-02-03-api-design.md  # With tool I/O
│   │       └── 2026-02-03-bug-fix.md
│   └── project-b/
│       └── ...
├── memory.sqlite
└── logs/
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
