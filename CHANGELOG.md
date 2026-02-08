# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.6] - 2026-02-08

### Fixed
- 修复 find_current_session 不匹配当前项目的 bug (P0-1)
- 保存后自动触发增量索引 (P0-2)
- cleanup 同步清理 full/ 文件和 SQLite 索引 (P1-3)

### Changed
- 提取共享工具模块 utils.py，消除 _get_model() 和路径获取重复代码 (P1-1, P1-2)

### Added
- 添加 CHANGELOG.md 变更日志
- 添加综合审查与修复追踪文档

## [2.2.5] - 2026-02-09

### Added
- 添加记忆导出功能，支持 Markdown 和 JSON 格式
- 添加统一日志系统，日志存储在 `~/.claude/Claudememv2-data/logs/memory.log`

### Changed
- 同步所有模块版本号至 v2.2.5

## [2.2.4] - 2026-02-08

### Fixed
- 修复自然语言触发时不调用 Python 脚本的问题

## [2.2.3] - 2026-02-07

### Added
- 添加 AI 摘要生成功能，使用 Claude API 自动生成对话摘要

### Changed
- 移除摘要文件中的原始对话内容，仅保留摘要

### Fixed
- 修正文档中的模型选项描述

## [2.2.2] - 2026-02-06

### Added
- 动态读取 Claude Code 模型配置，自动使用用户配置的模型

## [2.2.1] - 2026-02-05

### Fixed
- 修复 Windows 兼容性问题
- 修复会话路径解析错误

## [2.2.0] - 2026-02-04

### Added
- 双文件保存机制：同时保存摘要文件和完整对话文件
- 搜索范围配置选项

### Changed
- 修复命令命名规范

## [2.1.0] - 2026-02-03

### Added
- 初始版本发布
- 智能记忆系统核心功能
- 使用 Claude API 进行语义搜索
- 按项目组织记忆
- SQLite + FTS5 全文搜索
- Slash 命令支持：/memory save, /memory search, /memory status, /memory cleanup
- 自然语言触发支持

[2.2.6]: https://github.com/Pgooone/Claudememv2/compare/v2.2.5...v2.2.6
[2.2.5]: https://github.com/Pgooone/Claudememv2/compare/v2.2.4...v2.2.5
[2.2.4]: https://github.com/Pgooone/Claudememv2/compare/v2.2.3...v2.2.4
[2.2.3]: https://github.com/Pgooone/Claudememv2/compare/v2.2.2...v2.2.3
[2.2.2]: https://github.com/Pgooone/Claudememv2/compare/v2.2.1...v2.2.2
[2.2.1]: https://github.com/Pgooone/Claudememv2/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/Pgooone/Claudememv2/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/Pgooone/Claudememv2/releases/tag/v2.1.0
