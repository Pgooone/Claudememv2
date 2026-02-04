#!/usr/bin/env python3
"""
Claudememv2 Session Parser
Parses Claude Code session files and saves to memory
"""

import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

# Try to import anthropic for slug generation
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class SessionParser:
    """Parse Claude Code sessions and save to memory."""

    def __init__(self, config: dict):
        self.config = config
        self.memory_config = config.get("memory", {})
        self.model_config = config.get("model", {})

        # Get data directory
        data_dir = self.memory_config.get("dataDir", "~/.claude/Claudememv2-data")
        self.data_dir = Path(data_dir).expanduser()
        self.memory_dir = self.data_dir / "memory"

    def get_claude_projects_dir(self) -> Path:
        """Get Claude Code projects directory."""
        if os.name == "nt":
            base = Path(os.environ.get("USERPROFILE", ""))
        else:
            base = Path.home()
        return base / ".claude" / "projects"

    def find_current_session(self, working_dir: Optional[str] = None) -> Optional[Path]:
        """Find the most recent session file for current/specified project."""
        projects_dir = self.get_claude_projects_dir()

        if not projects_dir.exists():
            return None

        # Get working directory
        if working_dir is None:
            working_dir = os.getcwd()

        # Claude Code uses a hash of the project path
        # We need to find the matching project directory
        working_path = Path(working_dir).resolve()

        # Search for matching project
        latest_session = None
        latest_time = 0

        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            # Session files are directly in project directory (not in sessions/ subdirectory)
            # Look for .jsonl files directly in project_dir
            for session_file in project_dir.glob("*.jsonl"):
                mtime = session_file.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime
                    latest_session = session_file

        return latest_session

    def parse_session_file(self, session_path: Path) -> list:
        """Parse a session JSONL file and extract messages."""
        messages = []

        content_scope = self.memory_config.get("contentScope", "standard")
        include_thinking = self.memory_config.get("includeThinking", False)
        include_tool_calls = self.memory_config.get("includeToolCalls", True)
        max_messages = self.memory_config.get("maxMessages", 25)

        with open(session_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Claude Code session format: type is "user" or "assistant"
                # Message content is in entry["message"]["content"]
                entry_type = entry.get("type")

                # Skip non-message entries (file-history-snapshot, progress, system, summary, etc.)
                if entry_type not in ("user", "assistant"):
                    continue

                # Get the message object
                message = entry.get("message", {})
                role = message.get("role")

                if not role:
                    continue

                # Skip meta messages (system reminders, etc.)
                if entry.get("isMeta"):
                    continue

                # Extract content from message
                content = self._extract_content(message, include_thinking=(content_scope == "full"))

                if not content:
                    continue

                # Skip command messages (starting with / or containing command tags)
                if role == "user":
                    if content.startswith("/") or "<command-name>" in content:
                        continue
                    # Skip local command outputs
                    if "<local-command" in content:
                        continue

                # Extract tool calls from assistant messages if needed
                tool_calls = []
                if include_tool_calls and role == "assistant":
                    tool_calls = self._extract_tool_calls(message)

                # Filter based on content scope
                if content_scope == "minimal":
                    # Only user and assistant text messages (no tool calls)
                    messages.append({
                        "role": role,
                        "content": content,
                        "timestamp": entry.get("timestamp")
                    })
                elif content_scope == "standard":
                    # User, assistant, and tool call summaries (no thinking)
                    messages.append({
                        "role": role,
                        "content": content,
                        "timestamp": entry.get("timestamp")
                    })
                    # Add tool calls as separate entries
                    for tool_call in tool_calls:
                        messages.append({
                            "role": "tool",
                            "tool_name": tool_call.get("name", "unknown"),
                            "content": self._summarize_tool_call(tool_call),
                            "timestamp": entry.get("timestamp")
                        })
                else:  # full
                    # Everything including thinking (already extracted above)
                    messages.append({
                        "role": role,
                        "content": content,
                        "timestamp": entry.get("timestamp")
                    })
                    # Add tool calls as separate entries
                    for tool_call in tool_calls:
                        messages.append({
                            "role": "tool",
                            "tool_name": tool_call.get("name", "unknown"),
                            "content": self._summarize_tool_call(tool_call),
                            "timestamp": entry.get("timestamp")
                        })

        # Apply message limit (0 or None = no limit)
        if max_messages and max_messages > 0 and len(messages) > max_messages:
            messages = messages[-max_messages:]

        return messages

    def _extract_content(self, message: dict, include_thinking: bool = False) -> Optional[str]:
        """Extract text content from a message object.

        Args:
            message: The message object (entry["message"]) containing role and content
            include_thinking: Whether to include thinking blocks in output
        """
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get("type")
                    if item_type == "text":
                        text = item.get("text", "")
                        if text:
                            parts.append(text)
                    elif item_type == "thinking" and include_thinking:
                        thinking = item.get("thinking", "")
                        if thinking:
                            parts.append(f"\n<thinking>\n{thinking}\n</thinking>\n")
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts) if parts else None

        return None

    def _extract_tool_calls(self, message: dict) -> list:
        """Extract tool calls from an assistant message.

        Args:
            message: The message object containing content with tool_use blocks

        Returns:
            List of tool call dicts with name and input
        """
        content = message.get("content")
        tool_calls = []

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_calls.append({
                        "name": item.get("name", "unknown"),
                        "input": item.get("input", {})
                    })

        return tool_calls

    def _summarize_tool_call(self, tool_call: dict) -> str:
        """Create a summary of a tool call.

        Args:
            tool_call: Dict with 'name' and 'input' keys
        """
        tool_name = tool_call.get("name", "unknown")
        tool_input = tool_call.get("input", {})

        # Create a brief summary based on tool type
        if tool_name == "Read":
            return f"[Read: {tool_input.get('file_path', 'unknown')}]"
        elif tool_name == "Write":
            return f"[Write: {tool_input.get('file_path', 'unknown')}]"
        elif tool_name == "Edit":
            return f"[Edit: {tool_input.get('file_path', 'unknown')}]"
        elif tool_name == "Bash":
            cmd = tool_input.get("command", "")
            if len(cmd) > 100:
                cmd = cmd[:100] + "..."
            return f"[Bash: {cmd}]"
        elif tool_name == "Grep":
            pattern = tool_input.get("pattern", "")
            path = tool_input.get("path", "")
            return f"[Grep: '{pattern}' in {path or 'cwd'}]"
        elif tool_name == "Glob":
            return f"[Glob: {tool_input.get('pattern', '')}]"
        elif tool_name == "Task":
            desc = tool_input.get("description", "")
            return f"[Task: {desc}]"
        elif tool_name == "WebFetch":
            url = tool_input.get("url", "")
            return f"[WebFetch: {url}]"
        elif tool_name == "WebSearch":
            query = tool_input.get("query", "")
            return f"[WebSearch: {query}]"
        else:
            return f"[{tool_name}]"

    def generate_slug(self, messages: list) -> str:
        """Generate a descriptive slug for the session using Claude API."""
        if not HAS_ANTHROPIC:
            return datetime.now().strftime("%H%M")

        # Create a summary of the conversation
        summary_parts = []
        for msg in messages[:10]:  # Use first 10 messages for context
            role = msg.get("role", "")
            content = msg.get("content", "")
            if content and len(content) > 200:
                content = content[:200] + "..."
            summary_parts.append(f"{role}: {content}")

        summary = "\n".join(summary_parts)

        try:
            # Get model from config
            model = self._get_model()

            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": f"""Based on this conversation, generate a 1-3 word slug (lowercase, hyphen-separated) that describes the main topic. Only output the slug, nothing else.

Conversation:
{summary}

Slug:"""
                }]
            )

            slug = response.content[0].text.strip().lower()
            # Clean up slug
            slug = re.sub(r"[^a-z0-9-]", "", slug)
            slug = re.sub(r"-+", "-", slug)
            slug = slug.strip("-")

            if len(slug) > 30:
                slug = slug[:30].rsplit("-", 1)[0]

            return slug if slug else datetime.now().strftime("%H%M")

        except Exception:
            return datetime.now().strftime("%H%M")

    def _get_model(self) -> str:
        """Get the model to use from config."""
        source = self.model_config.get("source", "inherit")

        if source == "custom" and self.model_config.get("customModelId"):
            return self.model_config["customModelId"]

        # Try to read from Claude Code settings
        try:
            if os.name == "nt":
                settings_path = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "settings.json"
            else:
                settings_path = Path.home() / ".claude" / "settings.json"

            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    env = settings.get("env", {})

                    # Map source to environment variable
                    model_map = {
                        "inherit": "ANTHROPIC_MODEL",
                        "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
                        "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
                        "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
                    }

                    if source in model_map and model_map[source] in env:
                        return env[model_map[source]]

                    # Fallback to ANTHROPIC_MODEL if source not found
                    if "ANTHROPIC_MODEL" in env:
                        return env["ANTHROPIC_MODEL"]

                    # Legacy format support
                    if "model" in settings:
                        return settings["model"]
        except Exception:
            pass

        return self.model_config.get("fallback", "claude-3-haiku-20240307")

    def generate_summary(self, messages: list) -> Optional[str]:
        """使用 Claude API 生成对话摘要。"""
        summary_config = self.config.get("summary", {})

        # 检查是否启用摘要
        if not summary_config.get("enabled", True):
            return None

        timing = summary_config.get("timing", "on_save")
        if timing == "disabled":
            return None

        if not HAS_ANTHROPIC:
            return None

        format_type = summary_config.get("format", "structured")

        # 准备对话内容
        conversation = self._format_conversation_for_summary(messages)

        # 获取对应的 prompt
        prompt = self._get_summary_prompt(format_type, conversation)

        try:
            model = self._get_model()
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            # API 调用失败时返回 None，仍保存原始对话
            return None

    def _format_conversation_for_summary(self, messages: list) -> str:
        """将消息列表格式化为摘要用的文本。"""
        parts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "tool":
                tool_name = msg.get("tool_name", "unknown")
                parts.append(f"[工具调用: {tool_name}] {content}")
            else:
                role_cn = {"user": "用户", "assistant": "助手"}.get(role, role)
                # 截断过长的内容
                if len(content) > 500:
                    content = content[:500] + "..."
                parts.append(f"{role_cn}: {content}")

        return "\n\n".join(parts)

    def _get_summary_prompt(self, format_type: str, conversation: str) -> str:
        """根据格式类型获取摘要 prompt。"""
        if format_type == "structured":
            return f"""基于以下对话内容，生成一个结构化摘要。请使用中文输出（专有名词除外）。严格按照以下格式：

## 会话主题
[一句话描述本次会话的主要目标或主题]

## 关键决策和结论
- [决策/结论 1]
- [决策/结论 2]
...

## 完成的任务
- [x] [任务 1]
- [x] [任务 2]
...

## 遇到的问题和解决方案
- **问题**: [问题描述]
  **解决**: [解决方案]
...

## 后续待办
- [ ] [待办 1]
- [ ] [待办 2]
...

如果某个部分没有相关内容，写"无"。

---
对话内容：
{conversation}"""

        elif format_type == "freeform":
            return f"""基于以下对话内容，生成一段简洁的总结（150-300字）。请使用中文输出（专有名词除外）。
重点描述：做了什么、为什么这样做、结果如何。

对话内容：
{conversation}"""

        else:  # mixed
            return f"""基于以下对话内容，生成摘要。请使用中文输出（专有名词除外）。格式如下：

## 概述
[2-3句话总结本次会话]

## 关键点
- [要点 1]
- [要点 2]
- [要点 3]
...

对话内容：
{conversation}"""

    def parse_session_file_full(self, session_path: Path) -> list:
        """Parse a session JSONL file and extract full messages with tool results.

        This method extracts complete content including:
        - User messages
        - Assistant messages with thinking
        - Tool calls with full input
        - Tool results with full output
        """
        messages = []
        max_messages = self.memory_config.get("maxMessages", 25)

        # Track tool calls to match with results
        pending_tool_calls = {}  # tool_use_id -> tool_call_info

        with open(session_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type")

                # Skip non-message entries
                if entry_type not in ("user", "assistant"):
                    continue

                message = entry.get("message", {})
                role = message.get("role")

                if not role:
                    continue

                # Skip meta messages
                if entry.get("isMeta"):
                    continue

                content = message.get("content")

                # Handle assistant messages
                if entry_type == "assistant" and role == "assistant":
                    # Extract text and thinking
                    text_content = self._extract_content(message, include_thinking=True)

                    if text_content:
                        # Skip if it's just a command response
                        if "<command-name>" not in text_content:
                            messages.append({
                                "role": "assistant",
                                "content": text_content,
                                "timestamp": entry.get("timestamp")
                            })

                    # Extract and store tool calls
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "tool_use":
                                tool_id = item.get("id")
                                tool_name = item.get("name", "unknown")
                                tool_input = item.get("input", {})

                                # Store for later matching with result
                                pending_tool_calls[tool_id] = {
                                    "name": tool_name,
                                    "input": tool_input
                                }

                                # Add tool call entry
                                messages.append({
                                    "role": "tool_call",
                                    "tool_name": tool_name,
                                    "tool_id": tool_id,
                                    "input": tool_input,
                                    "timestamp": entry.get("timestamp")
                                })

                # Handle user messages (including tool results)
                elif entry_type == "user" and role == "user":
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                item_type = item.get("type")

                                # Tool result
                                if item_type == "tool_result":
                                    tool_id = item.get("tool_use_id")
                                    result_content = item.get("content", "")

                                    # Get tool info from pending calls
                                    tool_info = pending_tool_calls.get(tool_id, {})

                                    messages.append({
                                        "role": "tool_result",
                                        "tool_name": tool_info.get("name", "unknown"),
                                        "tool_id": tool_id,
                                        "result": result_content,
                                        "timestamp": entry.get("timestamp")
                                    })

                    elif isinstance(content, str):
                        # Regular user message
                        if content.startswith("/") or "<command-name>" in content:
                            continue
                        if "<local-command" in content:
                            continue

                        messages.append({
                            "role": "user",
                            "content": content,
                            "timestamp": entry.get("timestamp")
                        })

        # Apply message limit (0 or None = no limit)
        if max_messages and max_messages > 0 and len(messages) > max_messages:
            messages = messages[-max_messages:]

        return messages

    def save_session(self, project_override: Optional[str] = None) -> dict:
        """Save the current session to memory (summary + full files)."""
        # Find current session
        session_path = self.find_current_session()
        if session_path is None:
            raise ValueError("No current session found. Please have a conversation first.")

        # Parse messages for summary
        messages = self.parse_session_file(session_path)
        if not messages:
            raise ValueError("Current session has no valid content.")

        # Get project name
        if project_override:
            project = project_override
        else:
            project = Path(os.getcwd()).name

        # Generate slug
        slug = self.generate_slug(messages)

        # Create file path
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-{slug}.md"

        project_dir = self.memory_dir / project
        project_dir.mkdir(parents=True, exist_ok=True)

        file_path = project_dir / filename

        # Handle duplicate filenames
        counter = 1
        base_filename = filename
        while file_path.exists():
            filename = f"{date_str}-{slug}-{counter}.md"
            file_path = project_dir / filename
            counter += 1

        # Generate and write summary markdown
        summary_content = self._generate_markdown(messages, project)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(summary_content)

        # Save full file if enabled
        save_full = self.memory_config.get("saveFull", True)
        full_file_path = None

        if save_full:
            # Parse full messages
            full_messages = self.parse_session_file_full(session_path)

            if full_messages:
                # Create full directory
                full_dir = project_dir / "full"
                full_dir.mkdir(parents=True, exist_ok=True)

                full_file_path = full_dir / filename

                # Generate and write full markdown
                full_content = self._generate_full_markdown(full_messages, project)
                with open(full_file_path, "w", encoding="utf-8") as f:
                    f.write(full_content)

        result = {
            "file_path": str(file_path),
            "message_count": len(messages),
            "project": project
        }

        if full_file_path:
            result["full_file_path"] = str(full_file_path)

        return result

    def _generate_markdown(self, messages: list, project: str) -> str:
        """Generate markdown content for the summary memory file."""
        now = datetime.now()
        summary_config = self.config.get("summary", {})
        summary_format = summary_config.get("format", "structured")

        # 尝试生成 AI 摘要
        ai_summary = self.generate_summary(messages)

        # YAML frontmatter
        lines = [
            "---",
            f"project: {project}",
            f"created: {now.isoformat()}",
            "source: claude-code",
            f"messages: {len(messages)}",
            f"content_scope: {self.memory_config.get('contentScope', 'standard')}",
            f"summary_format: {summary_format}",
            f"has_ai_summary: {ai_summary is not None}",
            "type: summary",
            "---",
            "",
            f"# 会话记录: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 元数据",
            f"- **项目**: {project}",
            f"- **工作目录**: {os.getcwd()}",
            f"- **消息数**: {len(messages)}",
            ""
        ]

        # 添加 AI 生成的摘要
        if ai_summary:
            lines.append(ai_summary)
            lines.append("")
        else:
            # 如果没有 AI 摘要，添加简短说明
            lines.append("*（AI 摘要未生成，请查看 full/ 目录下的完整对话记录）*")
            lines.append("")

        return "\n".join(lines)

    def _generate_full_markdown(self, messages: list, project: str) -> str:
        """Generate markdown content for the full memory file with complete tool I/O."""
        now = datetime.now()

        # YAML frontmatter
        lines = [
            "---",
            f"project: {project}",
            f"created: {now.isoformat()}",
            "source: claude-code",
            f"messages: {len(messages)}",
            "content_scope: full",
            "type: full",
            "---",
            "",
            f"# Session: {now.strftime('%Y-%m-%d %H:%M:%S')} (Full)",
            "",
            "## Metadata",
            f"- **Project**: {project}",
            f"- **Working Directory**: {os.getcwd()}",
            f"- **Messages**: {len(messages)}",
            "",
            "## Conversation",
            ""
        ]

        # Add messages
        for msg in messages:
            role = msg.get("role", "unknown")

            if role == "user":
                content = msg.get("content", "")
                lines.append(f"### User")
                lines.append("")
                lines.append(content)
                lines.append("")

            elif role == "assistant":
                content = msg.get("content", "")
                lines.append(f"### Assistant")
                lines.append("")
                lines.append(content)
                lines.append("")

            elif role == "tool_call":
                tool_name = msg.get("tool_name", "unknown")
                tool_input = msg.get("input", {})
                lines.append(f"### Tool Call: {tool_name}")
                lines.append("")
                lines.append("**Input:**")
                lines.append("```json")
                lines.append(json.dumps(tool_input, indent=2, ensure_ascii=False))
                lines.append("```")
                lines.append("")

            elif role == "tool_result":
                tool_name = msg.get("tool_name", "unknown")
                result = msg.get("result", "")
                lines.append(f"### Tool Result: {tool_name}")
                lines.append("")
                lines.append("**Output:**")
                lines.append("```")
                # Handle result that might be very long
                if isinstance(result, str):
                    lines.append(result)
                else:
                    lines.append(json.dumps(result, indent=2, ensure_ascii=False))
                lines.append("```")
                lines.append("")

        return "\n".join(lines)
