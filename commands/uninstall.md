---
description: 从 Claude Code 完全卸载 Claudememv2
---

# Claudememv2 卸载

此命令引导你完全卸载 Claudememv2。

## 卸载选项

当用户运行 `/Claudememv2:uninstall` 时，询问：

```
你希望如何卸载 Claudememv2？

1. 保留记忆数据（推荐）
   - 删除插件但保留已保存的记忆
   - 以后可以重新安装并访问旧记忆

2. 完全删除
   - 删除插件和所有记忆数据
   - 此操作不可撤销
```

## 卸载流程

### 选项 1：保留记忆数据

**Windows (PowerShell):**
```powershell
# 删除插件缓存
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache\Claudememv2" -ErrorAction SilentlyContinue

# 删除插件配置（但保留数据）
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\Claudememv2" -ErrorAction SilentlyContinue

# 注意：记忆数据保留在：
# $env:USERPROFILE\.claude\Claudememv2-data\
```

**macOS/Linux:**
```bash
# 删除插件缓存
rm -rf ~/.claude/plugins/cache/Claudememv2

# 删除插件配置（但保留数据）
rm -rf ~/.claude/plugins/Claudememv2

# 注意：记忆数据保留在：
# ~/.claude/Claudememv2-data/
```

### 选项 2：完全删除

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

### 步骤 3：更新插件注册表

编辑 `~/.claude/plugins/installed_plugins.json` 并删除 Claudememv2 条目。

或使用插件命令：
```
/plugin uninstall Claudememv2
```

## 验证

卸载后，验证以下路径不再存在：

| 项目 | Windows 路径 | macOS/Linux 路径 |
|------|--------------|------------------|
| 插件缓存 | `%USERPROFILE%\.claude\plugins\cache\Claudememv2\` | `~/.claude/plugins/cache/Claudememv2/` |
| 插件配置 | `%USERPROFILE%\.claude\plugins\Claudememv2\` | `~/.claude/plugins/Claudememv2/` |
| 记忆数据* | `%USERPROFILE%\.claude\Claudememv2-data\` | `~/.claude/Claudememv2-data/` |

*仅在选择"完全删除"时删除。

## 成功消息

```
✓ Claudememv2 已卸载。

[如果保留数据：]
  你的记忆数据保留在：
  ~/.claude/Claudememv2-data/

  如需完全删除数据，请手动删除此目录。

[如果完全删除：]
  所有 Claudememv2 数据已删除。

Claude Code 将继续正常运行。
```

## 安全保证

Claudememv2 不会修改任何 Claude Code 核心文件。所有数据存储在独立目录中。卸载后，Claude Code 将完全恢复到安装前的状态。
