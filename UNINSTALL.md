# Claudememv2 卸载指南

本文档提供从 Claude Code 完全卸载 Claudememv2 的详细说明。

## 快速卸载

### 使用插件命令卸载（推荐）

```bash
/plugin uninstall Claudememv2
```

然后可选择删除记忆数据：

**Windows (PowerShell):**
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\Claudememv2-data"
```

**macOS/Linux:**
```bash
rm -rf ~/.claude/Claudememv2-data
```

---

## 手动卸载

### 选项 1：保留记忆数据

删除插件但保留已保存的记忆，以便将来使用。

**Windows (PowerShell):**
```powershell
# 删除插件缓存
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache\Claudememv2" -ErrorAction SilentlyContinue

# 删除插件配置
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\Claudememv2" -ErrorAction SilentlyContinue

# 记忆数据保留在：
# $env:USERPROFILE\.claude\Claudememv2-data\
```

**macOS/Linux:**
```bash
# 删除插件缓存
rm -rf ~/.claude/plugins/cache/Claudememv2

# 删除插件配置
rm -rf ~/.claude/plugins/Claudememv2

# 记忆数据保留在：
# ~/.claude/Claudememv2-data/
```

### 选项 2：完全删除

删除所有内容，包括所有已保存的记忆。**此操作不可撤销。**

**Windows (PowerShell):**
```powershell
# 删除插件缓存
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache\Claudememv2" -ErrorAction SilentlyContinue

# 删除插件配置
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\Claudememv2" -ErrorAction SilentlyContinue

# 删除所有记忆数据（不可恢复）
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\Claudememv2-data" -ErrorAction SilentlyContinue
```

**macOS/Linux:**
```bash
# 删除插件缓存
rm -rf ~/.claude/plugins/cache/Claudememv2

# 删除插件配置
rm -rf ~/.claude/plugins/Claudememv2

# 删除所有记忆数据（不可恢复）
rm -rf ~/.claude/Claudememv2-data
```

---

## 更新插件注册表

手动删除后，编辑 `~/.claude/plugins/installed_plugins.json` 并删除 Claudememv2 条目。

---

## 验证清单

卸载后，验证以下路径不再存在：

| 项目 | Windows 路径 | macOS/Linux 路径 |
|------|--------------|------------------|
| 插件缓存 | `%USERPROFILE%\.claude\plugins\cache\Claudememv2\` | `~/.claude/plugins/cache/Claudememv2/` |
| 插件配置 | `%USERPROFILE%\.claude\plugins\Claudememv2\` | `~/.claude/plugins/Claudememv2/` |
| 记忆数据* | `%USERPROFILE%\.claude\Claudememv2-data\` | `~/.claude/Claudememv2-data/` |

*仅在选择完全删除时。

---

## 验证命令

**Windows (PowerShell):**
```powershell
# 检查插件是否已删除
Test-Path "$env:USERPROFILE\.claude\plugins\cache\Claudememv2"
# 应返回：False

# 检查数据是否已删除（如果选择完全删除）
Test-Path "$env:USERPROFILE\.claude\Claudememv2-data"
# 应返回：False
```

**macOS/Linux:**
```bash
# 检查插件是否已删除
ls ~/.claude/plugins/cache/Claudememv2 2>/dev/null || echo "插件已删除"

# 检查数据是否已删除（如果选择完全删除）
ls ~/.claude/Claudememv2-data 2>/dev/null || echo "数据已删除"
```

---

## 安全保证

**Claudememv2 不会修改任何 Claude Code 核心文件。**

所有数据存储在独立目录中：
- 插件文件：`~/.claude/plugins/cache/Claudememv2/`
- 配置文件：`~/.claude/plugins/Claudememv2/`
- 记忆数据：`~/.claude/Claudememv2-data/`

卸载后，Claude Code 将完全恢复到安装 Claudememv2 之前的状态。

---

## 故障排除

### 卸载后插件仍然显示

1. 重启 Claude Code
2. 检查 `~/.claude/plugins/installed_plugins.json` 是否有残留条目
3. 手动从 JSON 文件中删除任何 Claudememv2 条目

### 卸载后命令仍然有效

插件缓存可能未完全删除。运行：

**Windows:**
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache\Claudememv2"
```

**macOS/Linux:**
```bash
rm -rf ~/.claude/plugins/cache/Claudememv2
```

然后重启 Claude Code。

---

## 重新安装

如果以后想重新安装 Claudememv2：

```bash
/plugin marketplace add Pgooone/Claudememv2
/plugin install Claudememv2
/Claudememv2:setup
```

如果保留了记忆数据，重新安装后将自动可用。
