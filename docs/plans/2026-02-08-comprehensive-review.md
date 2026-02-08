# Claudememv2 综合审查与修复追踪

> 日期：2026-02-08
> 审查版本：v2.2.5
> 状态：进行中

## 问题追踪表

| ID | 优先级 | 问题 | 影响 | 状态 |
|----|--------|------|------|------|
| P0-1 | P0 | `find_current_session` 不匹配当前项目 | 可能保存错误项目的会话 | ✅ 已修复 |
| P0-2 | P0 | 保存后不自动触发索引 | 新记忆搜索不到 | ✅ 已修复 |
| P1-1 | P1 | `Path("")` 空路径风险 | 环境变量缺失时写入错误位置 | ✅ 已修复 |
| P1-2 | P1 | `_get_model()` 三处重复 | 维护负担，改一处漏两处 | ✅ 已修复 |
| P1-3 | P1 | cleanup 不清理 full/ 和索引 | 数据不一致，磁盘空间浪费 | ✅ 已修复 |
| P2-1 | P2 | 搜索硬编码 50 chunk 上限 | 大记忆库搜索不全 | ⏳ 待修复 |
| P2-2 | P2 | API 调用无超时 | 网络异常时无限阻塞 | ⏳ 待修复 |
| P2-3 | P2 | async/on_demand 摘要模式未实现 | 配置选项名不副实 | ⏳ 待修复 |
| P2-4 | P2 | plugin.json 缺少命令注册字段 | 插件发现可能失败 | ⏳ 待修复 |
| P2-5 | P2 | API 响应格式未校验 | API 异常返回时 IndexError | ⏳ 待修复 |
| P2-6 | P2 | 搜索引擎正则不支持小数 | 语义评分解析失败 | ⏳ 待修复 |
| P3-1 | P3 | 日志无轮转机制 | 长期使用文件无限增长 | ⏳ 待修复 |
| P3-2 | P3 | SQLite 连接无 context manager | 异常时连接泄漏 | ⏳ 待修复 |
| P3-3 | P3 | 配置合并只做一层 update | 部分默认值可能丢失 | ⏳ 待修复 |
| P3-4 | P3 | Setup 流程过长（10步） | 用户体验差 | ⏳ 待修复 |
| P3-5 | P3 | 无自动化测试 | 回归风险高 | ⏳ 待修复 |
| P3-6 | P3 | 缺少 CHANGELOG.md | 用户难以了解版本变化 | ⏳ 待修复 |
| P3-7 | P3 | 缺少 Git 标签 | 版本追溯困难 | ⏳ 待修复 |
| P3-8 | P3 | config 命令类型转换无友好提示 | 输入非数字时崩溃 | ⏳ 待修复 |
| P3-9 | P3 | cleanup --days 0 被忽略 | 0 被视为 falsy | ⏳ 待修复 |
| P3-10 | P3 | 项目名称路径遍历风险 | 安全隐患 | ⏳ 待修复 |

---

## P0 问题详情

### P0-1: find_current_session 不匹配当前项目 ✅

**文件**: `session_parser.py:45-84`
**问题**: `working_path` 被计算但从未使用，遍历所有项目取全局最新 session，可能保存错误项目的会话。
**修复**: 将工作路径转换为 Claude Code 项目目录名格式（路径分隔符替换为 `-`），优先匹配当前项目的会话，无匹配时 fallback 到全局最新。

### P0-2: 保存后不自动触发索引 ✅

**文件**: `memory_core.py:114-118`
**问题**: `cmd_save()` 保存成功后没有调用索引，新记忆搜索不到。
**修复**: 在 `cmd_save()` 保存成功后调用 `SearchEngine(config).index()`，索引失败不阻止保存成功报告。

---

## P1 问题详情

### P1-1: Path("") 空路径风险 ✅

**问题**: 多处 `Path(os.environ.get("USERPROFILE", ""))` 当环境变量不存在时产生 `Path("")`。
**修复**: 创建 `scripts/utils.py`，提供 `get_home_dir()` 函数，Windows 优先用 USERPROFILE，fallback 到 `Path.home()`。所有文件已改用此函数。

### P1-2: _get_model() 三处重复 ✅

**问题**: 几乎完全相同的模型获取逻辑在三个文件中重复。
**修复**: 提取到 `scripts/utils.py` 的 `get_model(model_config)` 函数。删除了 `session_parser.py` 和 `search_engine.py` 中的 `_get_model()` 方法，`memory_core.py` 中 `cmd_status` 的模型读取也改用此函数。

### P1-3: cleanup 不清理 full/ 和索引 ✅

**文件**: `memory_core.py:243-307`
**问题**: cleanup 只删除摘要文件，不删除 full/ 对应文件，也不清理 SQLite 索引。
**修复**: 删除摘要文件时同步删除 `full/` 子目录中同名文件；删除完成后清理 SQLite 中的孤立记录（files 和 chunks 表），重建 FTS 索引。输出增加 full 文件删除数量。
