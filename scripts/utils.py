#!/usr/bin/env python3
"""
Claudememv2 Utilities
Shared utility functions for path handling and model configuration
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional


def get_home_dir() -> Path:
    """Get user home directory with fallback handling.

    Returns:
        Path object for user home directory
    """
    if sys.platform == "win32":
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            return Path(userprofile)
    return Path.home()


def get_model(model_config: dict) -> str:
    """Get the model to use from config.

    Args:
        model_config: Dict containing 'source', 'customModelId', 'fallback' keys

    Returns:
        Model ID string
    """
    source = model_config.get("source", "inherit")

    if source == "custom" and model_config.get("customModelId"):
        return model_config["customModelId"]

    # Try to read from Claude Code settings
    try:
        settings_path = get_home_dir() / ".claude" / "settings.json"

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

    return model_config.get("fallback", "claude-3-haiku-20240307")
