# Claudememv2 改进计划

> 日期：2026-02-07
> 版本：v2.2.4 → v2.2.5
> 状态：迭代 4/5/7 已完成，其余待完善

## 一、Bug 修复（高优先级）

### Bug 1：路径回退机制缺陷
- **文件**：`memory_core.py` 行 30/39/199, `session_parser.py`
- **问题**：`os.environ.get("USERPROFILE", "")` 当环境变量未设置时，`Path("")` 产生无效路径
- **影响**：Windows 系统上所有文件操作可能失败
- **修复**：统一使用 `Path.home()` 作为跨平台回退
```python
# 修复前
base = Path(os.environ.get("USERPROFILE", ""))
# 修复后
base = Path(os.environ.get("USERPROFILE", "")) if os.environ.get("USERPROFILE") else Path.home()
```

### Bug 2：API 响应格式假设
- **文件**：`session_parser.py` 行 307/394
- **问题**：直接访问 `response.content[0].text`，未检查 content 是否为空
- **影响**：API 异常返回时触发 `IndexError`
- **修复**：添加响应内容校验
```python
if not response.content or not hasattr(response.content[0], 'text'):
    raise ValueError("Unexpected API response format")
```

### Bug 3：config 命令类型转换崩溃
- **文件**：`memory_core.py` 行 328
- **问题**：`int(args.value)` 在用户输入非数字时直接抛出 `ValueError`
- **影响**：程序崩溃，无友好提示
- **修复**：添加 try-except 并给出友好提示
```python
try:
    config[section][key] = int(args.value)
except ValueError:
    print(f"[ERROR] '{args.value}' is not a valid integer", file=sys.stderr)
    sys.exit(1)
```

### Bug 4：cleanup 的 --days 0 被忽略
- **文件**：`memory_core.py` 行 264
- **问题**：`args.days or config[...]` 中 `0` 被视为 falsy，用户指定 `--days 0` 时被忽略
- **修复**：
```python
# 修复前
days = args.days or config["memory"]["cleanupDays"]
# 修复后
days = args.days if args.days is not None else config["memory"]["cleanupDays"]
```

### Bug 5：搜索引擎正则不支持小数分数
- **文件**：`search_engine.py` 行 395
- **问题**：正则 `r"\[[\d,\s]+\]"` 不匹配小数（如 `[85.5, 90.2]`）
- **影响**：语义评分解析失败，回退到纯 FTS 搜索
- **修复**：改为 `r"\[[\d.,\s]+\]"`

---

## 二、健壮性增强（中优先级）

### 增强 1：文件 I/O 操作统一错误处理
- **涉及文件**：
  - `session_parser.py` 行 86/489（会话文件读取）
  - `session_parser.py` 行 637/657（记忆文件写入）
  - `search_engine.py` 行 266（索引时文件读取）
  - `memory_core.py` 行 175-183（status 命令遍历文件）
  - `memory_core.py` 行 336-337（配置文件写入）
- **修复**：对所有文件 I/O 添加 `FileNotFoundError`、`PermissionError`、`OSError` 捕获

### 增强 2：数据库连接健壮性
- **文件**：`search_engine.py` 行 44/193/301
- **问题**：`sqlite3.connect()` 未处理数据库锁定或损坏
- **修复**：添加连接超时参数和异常处理，损坏时提示重建索引

### 增强 3：JSON 解析防御
- **文件**：`memory_core.py` 行 204-206, `search_engine.py` 行 98-99
- **问题**：读取配置/设置文件时未处理 `JSONDecodeError`
- **修复**：捕获异常并回退到默认配置，同时警告用户

### 增强 4：cleanup 命令竞态条件
- **文件**：`memory_core.py` 行 275-278
- **问题**：两次调用 `stat()` 之间文件可能被删除
- **修复**：缓存第一次 `stat()` 结果，用 try-except 包裹 `unlink()`

### 增强 5：异常捕获过于宽泛
- **文件**：`search_engine.py` 行 327-338/421
- **问题**：`except Exception` 可能隐藏 API 密钥错误等关键问题
- **修复**：区分 `anthropic.AuthenticationError`、`RateLimitError`、`sqlite3.Error` 等

### 增强 6：项目名称路径遍历防护
- **文件**：`memory_core.py` 行 109
- **问题**：`args.project` 未验证，可能包含 `../` 等路径遍历字符
- **修复**：对项目名称进行清理，只允许字母、数字、连字符和下划线

---

## 三、功能迭代（低优先级 / 未来规划）

### 迭代 1：会话文件重复解析优化
- **文件**：`session_parser.py` 行 605/646
- **问题**：同一 JSONL 文件被 `parse_session_file()` 和 `parse_session_file_full()` 解析两次
- **方案**：合并为一次解析，同时输出摘要版和完整版内容

### 迭代 2：Hook 自动保存
- **设计文档**：`docs/v2.2-hook-design.md`（已有）
- **方案**：通过 Claude Code Hook 系统在会话结束时自动保存记忆

### 迭代 3：记忆标签/分类系统
- **方案**：增加标签系统（如 `#bug-fix`、`#architecture`），支持按标签过滤搜索

### 迭代 4：记忆导出功能 ✅ 本次实现
- **方案**：添加 `export` 子命令，支持导出为 Markdown 合集或 JSON 格式
- **选项**：`--format md|json`、`--project`、`--output`

### 迭代 5：marketplace.json 版本同步 ✅ 本次实现
- **问题**：`marketplace.json` 版本 2.1.0 落后于 `plugin.json` 的 2.2.4
- **修复**：同步版本号和描述信息

### 迭代 6：搜索结果分页
- **文件**：`search_engine.py` 行 318
- **问题**：`fetchall()` 在数据量大时消耗大量内存
- **方案**：增加 `--page` 和 `--limit` 参数

### 迭代 7：日志系统完善 ✅ 本次实现
- **问题**：JSON 解析错误等被静默忽略
- **方案**：引入 Python `logging` 模块，写入 `~/.claude/Claudememv2-data/logs/`
- **实现**：在三个核心脚本中添加统一日志模块，支持文件日志和控制台输出
