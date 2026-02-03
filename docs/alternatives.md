# Claudememv2 备选方案文档

本文档记录了设计过程中考虑但未采用的备选方案，供未来参考。

## 1. 触发方式

### v2.1 采用：手动命令触发
用户主动输入 `/memory save` 来保存当前会话。

### 备选方案：Claude Code Hook 触发（v2.2 计划）
配置 `PostToolUse` 或 `Stop` hook 自动保存。
- 优点：自动化程度高
- 缺点：Claude Code 的 hook 无法直接访问会话内容

### 备选方案：定时/条件触发
每隔 N 条消息或检测到特定关键词时保存。
- 优点：智能触发
- 缺点：实现复杂，可能产生大量冗余文件

---

## 2. 向量搜索实现

### v2.1 采用：Claude API（用户可选模型）
使用 Claude API 进行语义匹配，用户可在安装时选择模型。

### 备选方案：Python + sentence-transformers
使用 `all-MiniLM-L6-v2` 模型进行本地向量嵌入。
- 优点：成熟稳定，本地运行，无需 API 调用
- 缺点：需要 Python 环境和依赖安装（约 500MB）

```python
# 示例实现
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)
```

### 备选方案：纯 FTS5 全文搜索
只保留 SQLite FTS5 全文搜索，去掉向量搜索。
- 优点：实现简单，无需 ML 依赖
- 缺点：搜索质量下降，无语义理解

---

## 3. 会话内容获取

### v2.1 采用：读取 Claude Code 会话文件
自动读取 `~/.claude/projects/<hash>/sessions/` 目录下的会话 JSONL 文件。

### 备选方案：用户手动粘贴/描述
用户执行 `/memory save` 后，Claude 提示用户提供要保存的内容摘要。
- 优点：简单可靠
- 缺点：需要用户额外操作

### 备选方案：基于当前对话上下文
Claude 直接基于当前对话窗口的上下文生成摘要。
- 优点：无需文件操作
- 缺点：上下文长度有限，可能丢失早期内容

---

## 4. 文件组织方式

### v2.1 采用：按项目/主题组织
```
memory/
├── <project-name>/
│   ├── 2026-02-03-api-design.md
│   └── 2026-02-03-bug-fix.md
└── <another-project>/
    └── ...
```

### 备选方案：按日期组织（扁平目录）
```
memory/
├── 2026-02-03-api-design.md
├── 2026-02-03-bug-fix.md
└── 2026-02-04-feature-plan.md
```
- 优点：清晰，易于手动浏览
- 缺点：多项目混杂

### 备选方案：扁平结构 + YAML frontmatter 标签
```
memory/
└── *.md  # 文件内用 YAML frontmatter 标记项目/标签
```
- 优点：灵活
- 缺点：依赖元数据搜索

---

## 5. 项目名称获取

### v2.1 采用：自动从工作目录获取
读取当前工作目录名称作为项目名。

### 备选方案：从配置文件读取
在 `config.json` 中配置项目映射。
- 优点：可自定义项目名
- 缺点：需要额外配置

### 备选方案：每次保存时询问
执行 `/memory save` 时提示用户输入或选择项目名。
- 优点：灵活
- 缺点：每次都需要交互

---

## 6. 安装位置

### v2.1 采用：全局安装（插件方式）
位置：`~/.claude/plugins/cache/Claudememv2/`

### 备选方案：项目本地安装
位置：`<project>/.claude/Claudememv2/`
- 优点：项目隔离
- 缺点：跨项目搜索困难

### 备选方案：自定义位置
用户指定任意目录。
- 优点：完全灵活
- 缺点：配置复杂
