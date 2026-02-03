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

            sessions_dir = project_dir / "sessions"
            if not sessions_dir.exists():
                continue

            # Find latest session in this project
            for session_file in sessions_dir.glob("*.jsonl"):
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

                # Extract message based on entry type
                msg_type = entry.get("type")
                role = entry.get("role")

                # Skip command messages (starting with /)
                if role == "user":
                    content = self._extract_content(entry)
                    if content and content.startswith("/"):
                        continue

                # Filter based on content scope
                if content_scope == "minimal":
                    # Only user and assistant text messages
                    if role in ("user", "assistant"):
                        content = self._extract_content(entry, include_thinking=False)
                        if content:
                            messages.append({
                                "role": role,
                                "content": content,
                                "timestamp": entry.get("timestamp")
                            })
                elif content_scope == "standard":
                    # User, assistant, and tool calls (no thinking)
                    if role in ("user", "assistant"):
                        content = self._extract_content(entry, include_thinking=False)
                        if content:
                            messages.append({
                                "role": role,
                                "content": content,
                                "timestamp": entry.get("timestamp")
                            })
                    elif include_tool_calls and msg_type == "tool_use":
                        messages.append({
                            "role": "tool",
                            "tool_name": entry.get("name", "unknown"),
                            "content": self._summarize_tool_call(entry),
                            "timestamp": entry.get("timestamp")
                        })
                else:  # full
                    # Everything including thinking
                    if role in ("user", "assistant"):
                        content = self._extract_content(entry, include_thinking=True)
                        if content:
                            messages.append({
                                "role": role,
                                "content": content,
                                "timestamp": entry.get("timestamp")
                            })
                    elif include_tool_calls and msg_type == "tool_use":
                        messages.append({
                            "role": "tool",
                            "tool_name": entry.get("name", "unknown"),
                            "content": self._summarize_tool_call(entry),
                            "timestamp": entry.get("timestamp")
                        })

        # Apply message limit (0 = no limit)
        if max_messages > 0 and len(messages) > max_messages:
            messages = messages[-max_messages:]

        return messages

    def _extract_content(self, entry: dict, include_thinking: bool = False) -> Optional[str]:
        """Extract text content from a message entry."""
        content = entry.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    elif item.get("type") == "thinking" and include_thinking:
                        parts.append(f"[Thinking: {item.get('thinking', '')}]")
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts) if parts else None

        return None

    def _summarize_tool_call(self, entry: dict) -> str:
        """Create a summary of a tool call."""
        tool_name = entry.get("name", "unknown")
        tool_input = entry.get("input", {})

        # Create a brief summary based on tool type
        if tool_name == "Read":
            return f"[Read file: {tool_input.get('file_path', 'unknown')}]"
        elif tool_name == "Write":
            return f"[Write file: {tool_input.get('file_path', 'unknown')}]"
        elif tool_name == "Edit":
            return f"[Edit file: {tool_input.get('file_path', 'unknown')}]"
        elif tool_name == "Bash":
            cmd = tool_input.get("command", "")
            if len(cmd) > 50:
                cmd = cmd[:50] + "..."
            return f"[Bash: {cmd}]"
        elif tool_name == "Grep":
            return f"[Grep: {tool_input.get('pattern', '')}]"
        elif tool_name == "Glob":
            return f"[Glob: {tool_input.get('pattern', '')}]"
        else:
            return f"[Tool: {tool_name}]"

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

        # Try to inherit from Claude Code settings
        if source == "inherit":
            try:
                if os.name == "nt":
                    settings_path = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "settings.json"
                else:
                    settings_path = Path.home() / ".claude" / "settings.json"

                if settings_path.exists():
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                        if "model" in settings:
                            return settings["model"]
            except Exception:
                pass

        return self.model_config.get("fallback", "claude-3-haiku-20240307")

    def save_session(self, project_override: Optional[str] = None) -> dict:
        """Save the current session to memory."""
        # Find current session
        session_path = self.find_current_session()
        if session_path is None:
            raise ValueError("No current session found. Please have a conversation first.")

        # Parse messages
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
        while file_path.exists():
            filename = f"{date_str}-{slug}-{counter}.md"
            file_path = project_dir / filename
            counter += 1

        # Generate markdown content
        content = self._generate_markdown(messages, project)

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "file_path": str(file_path),
            "message_count": len(messages),
            "project": project
        }

    def _generate_markdown(self, messages: list, project: str) -> str:
        """Generate markdown content for the memory file."""
        now = datetime.now()

        # YAML frontmatter
        lines = [
            "---",
            f"project: {project}",
            f"created: {now.isoformat()}",
            "source: claude-code",
            f"messages: {len(messages)}",
            f"content_scope: {self.memory_config.get('contentScope', 'standard')}",
            "---",
            "",
            f"# Session: {now.strftime('%Y-%m-%d %H:%M:%S')}",
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
            content = msg.get("content", "")

            if role == "tool":
                lines.append(f"**[Tool: {msg.get('tool_name', 'unknown')}]**: {content}")
            else:
                lines.append(f"**{role}**: {content}")
            lines.append("")

        return "\n".join(lines)
