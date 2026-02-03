---
description: Claudememv2 记忆管理命令 - 保存、搜索、索引、状态、清理
---

# Memory 命令

`/memory` 命令提供所有 Claudememv2 记忆管理功能。

## 可用子命令

### /memory save

将当前 Claude Code 对话保存到记忆。

**用法：**
```
/memory save [选项]
```

**选项：**
- `--messages N` - 覆盖最大保存消息数（0 = 全部）
- `--full` - 包含思考过程
- `--minimal` - 仅用户/助手消息
- `--all` - 保存所有消息（无限制）

**流程：**
1. 获取当前工作目录 → 提取项目名称
2. 定位 Claude Code 会话文件 `~/.claude/projects/<hash>/sessions/`
3. 解析会话 JSONL 文件
4. 根据内容范围配置过滤消息
5. 调用 Claude API 生成描述性 slug
6. 写入记忆文件到 `~/.claude/Claudememv2-data/memory/<project>/YYYY-MM-DD-slug.md`
7. 触发增量索引更新

**输出：**
```
✓ 会话已保存到记忆
  文件：~/.claude/Claudememv2-data/memory/openclaw/2026-02-03-api-design.md
  消息数：15
  项目：openclaw
```

---

### /memory search <查询>

使用语义匹配搜索记忆。

**用法：**
```
/memory search <查询> [选项]
```

**选项：**
- `--limit N` - 最大结果数（默认：6）
- `--project <名称>` - 仅在指定项目中搜索
- `--threshold N` - 最小相似度分数（默认：0.35）

**流程：**
1. 使用查询和记忆块调用 Claude API
2. 计算语义相似度分数
3. 结合 FTS5 全文搜索分数
4. 返回按相关性排序的前 N 个结果

**输出：**
```
🔍 搜索结果（查询："API 设计"）

1. [0.92] openclaw/2026-02-03-api-design.md:12-45
   "讨论了 REST API 设计原则，包括..."

2. [0.85] myproject/2026-01-28-backend.md:8-23
   "后端 API 架构采用分层设计..."
```

---

### /memory index

索引所有记忆文件到搜索数据库。

**用法：**
```
/memory index [选项]
```

**选项：**
- `--force` - 强制完全重建索引（忽略缓存）

**流程：**
1. 扫描 `~/.claude/Claudememv2-data/memory/` 目录
2. 比较文件哈希与数据库
3. 仅索引新增/修改的文件（增量）
4. 更新 SQLite 数据库和 FTS5 索引

**输出：**
```
📚 记忆索引已更新
  扫描文件：27
  新增索引：3
  已更新：1
  总分块数：156
```

---

### /memory status

显示记忆系统状态。

**用法：**
```
/memory status
```

**输出：**
```
📊 Claudememv2 记忆状态
  项目数：3
  文件数：27
  总大小：1.2 MB
  最近更新：2026-02-03 09:30:00
  模型：claude-3-haiku（继承自 Claude Code）
  内容范围：standard
  最大消息数：25
```

---

### /memory cleanup

清理旧记忆文件。

**用法：**
```
/memory cleanup [选项]
```

**选项：**
- `--days N` - 删除超过 N 天的文件（默认：90）
- `--dry-run` - 预览而不实际删除

**输出：**
```
🧹 记忆清理完成
  已删除文件：5
  释放空间：234 KB
  剩余文件：22
```

---

### /memory config

查看或修改配置。

**用法：**
```
/memory config [键] [值]
```

**示例：**
```
/memory config                    # 显示所有配置
/memory config model haiku        # 设置模型为 haiku
/memory config maxMessages 50     # 设置最大消息数
/memory config contentScope full  # 设置内容范围
```

---

## 错误处理

| 错误 | 消息 |
|------|------|
| 未找到会话 | "⚠️ 未找到当前会话，请先进行对话。" |
| API 调用失败 | "⚠️ 无法生成描述性名称，使用时间戳：2026-02-03-1030.md" |
| API 密钥缺失 | "⚠️ 请先配置 Anthropic API 密钥。" |
| 权限被拒绝 | "⚠️ 无法写入记忆目录，请检查权限。" |
| 无搜索结果 | "🔍 未找到匹配的记忆，请尝试其他关键词。" |
| 会话为空 | "⚠️ 当前会话无有效内容，跳过保存。" |
