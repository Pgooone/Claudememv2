#!/usr/bin/env python3
"""
Claudememv2 Memory Core
Main entry point for memory operations: save, search, index, status, cleanup
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding issues
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Import submodules
from session_parser import SessionParser
from search_engine import SearchEngine


def get_config_path():
    """Get the configuration file path."""
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", ""))
    else:
        base = Path.home()
    return base / ".claude" / "plugins" / "Claudememv2" / "config.json"


def get_data_dir():
    """Get the data directory path."""
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", ""))
    else:
        base = Path.home()
    return base / ".claude" / "Claudememv2-data"


def load_config():
    """Load configuration from file."""
    config_path = get_config_path()
    default_config = {
        "model": {
            "source": "inherit",
            "customModelId": None,
            "fallback": "claude-3-haiku-20240307"
        },
        "memory": {
            "dataDir": str(get_data_dir()),
            "contentScope": "standard",
            "includeThinking": False,
            "includeToolCalls": True,
            "maxMessages": 25,
            "cleanupDays": 90
        }
    }

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key in user_config:
                        default_config[key].update(user_config[key])
                return default_config
        except Exception as e:
            print(f"Warning: Could not load config: {e}", file=sys.stderr)

    return default_config


def cmd_save(args):
    """Save current session to memory."""
    config = load_config()
    parser = SessionParser(config)

    # Override config with command line args
    if args.messages is not None:
        config["memory"]["maxMessages"] = args.messages
    if args.full:
        config["memory"]["contentScope"] = "full"
        config["memory"]["includeThinking"] = True
    if args.minimal:
        config["memory"]["contentScope"] = "minimal"
        config["memory"]["includeToolCalls"] = False
    if args.all:
        config["memory"]["maxMessages"] = 0

    try:
        result = parser.save_session(args.project)
        print(f"[OK] Session saved to memory")
        print(f"  File: {result['file_path']}")
        print(f"  Messages: {result['message_count']}")
        print(f"  Project: {result['project']}")
    except Exception as e:
        print(f"[ERROR] Error saving session: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_search(args):
    """Search memories."""
    config = load_config()
    engine = SearchEngine(config)

    try:
        results = engine.search(
            query=args.query,
            limit=args.limit,
            project=args.project,
            threshold=args.threshold
        )

        if not results:
            print(f"[SEARCH] No matching memories found for: \"{args.query}\"")
            return

        print(f"[SEARCH] Search results (query: \"{args.query}\")\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['score']:.2f}] {result['file']}:{result['lines']}")
            print(f"   \"{result['excerpt'][:100]}...\"\n")
    except Exception as e:
        print(f"[ERROR] Error searching: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_index(args):
    """Index all memory files."""
    config = load_config()
    engine = SearchEngine(config)

    try:
        result = engine.index(force=args.force)
        print(f"[INDEX] Memory index updated")
        print(f"  Files scanned: {result['scanned']}")
        print(f"  New indexed: {result['new']}")
        print(f"  Updated: {result['updated']}")
        print(f"  Total chunks: {result['chunks']}")
    except Exception as e:
        print(f"[ERROR] Error indexing: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_status(args):
    """Show memory system status."""
    config = load_config()
    data_dir = Path(config["memory"]["dataDir"]).expanduser()
    memory_dir = data_dir / "memory"

    # Count projects and files
    projects = 0
    files = 0
    total_size = 0
    latest_update = None

    if memory_dir.exists():
        for project_dir in memory_dir.iterdir():
            if project_dir.is_dir():
                projects += 1
                for md_file in project_dir.glob("*.md"):
                    files += 1
                    total_size += md_file.stat().st_size
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if latest_update is None or mtime > latest_update:
                        latest_update = mtime

    # Format size
    if total_size < 1024:
        size_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        size_str = f"{total_size / 1024:.1f} KB"
    else:
        size_str = f"{total_size / (1024 * 1024):.1f} MB"

    # Get model info
    model_source = config["model"]["source"]
    if model_source == "inherit":
        model_str = f"{config['model']['fallback']} (inherited)"
    else:
        model_str = config["model"]["customModelId"] or config["model"]["fallback"]

    print(f"[STATUS] Claudememv2 Memory Status")
    print(f"  Projects: {projects}")
    print(f"  Files: {files}")
    print(f"  Total size: {size_str}")
    print(f"  Last updated: {latest_update.strftime('%Y-%m-%d %H:%M:%S') if latest_update else 'Never'}")
    print(f"  Model: {model_str}")
    print(f"  Content scope: {config['memory']['contentScope']}")
    print(f"  Max messages: {config['memory']['maxMessages'] or 'unlimited'}")


def cmd_cleanup(args):
    """Clean up old memory files."""
    config = load_config()
    data_dir = Path(config["memory"]["dataDir"]).expanduser()
    memory_dir = data_dir / "memory"

    days = args.days or config["memory"]["cleanupDays"]
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

    deleted = 0
    freed = 0
    remaining = 0

    if memory_dir.exists():
        for project_dir in memory_dir.iterdir():
            if project_dir.is_dir():
                for md_file in project_dir.glob("*.md"):
                    if md_file.stat().st_mtime < cutoff:
                        if not args.dry_run:
                            freed += md_file.stat().st_size
                            md_file.unlink()
                        deleted += 1
                    else:
                        remaining += 1

    if args.dry_run:
        print(f"[CLEANUP] Memory cleanup preview (dry run)")
    else:
        print(f"[CLEANUP] Memory cleanup complete")
    print(f"  Files {'to delete' if args.dry_run else 'deleted'}: {deleted}")
    print(f"  Space {'to free' if args.dry_run else 'freed'}: {freed / 1024:.1f} KB")
    print(f"  Remaining files: {remaining}")


def cmd_config(args):
    """View or modify configuration."""
    config_path = get_config_path()
    config = load_config()

    if args.key is None:
        # Show all config
        print(json.dumps(config, indent=2))
        return

    # Map simple keys to config paths
    key_map = {
        "model": ("model", "customModelId"),
        "source": ("model", "source"),
        "fallback": ("model", "fallback"),
        "contentScope": ("memory", "contentScope"),
        "maxMessages": ("memory", "maxMessages"),
        "cleanupDays": ("memory", "cleanupDays"),
        "includeThinking": ("memory", "includeThinking"),
        "includeToolCalls": ("memory", "includeToolCalls"),
    }

    if args.key not in key_map:
        print(f"[ERROR] Unknown config key: {args.key}")
        print(f"Available keys: {', '.join(key_map.keys())}")
        sys.exit(1)

    section, key = key_map[args.key]

    if args.value is None:
        # Show specific config
        print(f"{args.key}: {config[section][key]}")
    else:
        # Set config
        # Type conversion
        if key in ("maxMessages", "cleanupDays"):
            config[section][key] = int(args.value)
        elif key in ("includeThinking", "includeToolCalls"):
            config[section][key] = args.value.lower() in ("true", "1", "yes")
        else:
            config[section][key] = args.value

        # Save config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"[OK] Config updated: {args.key} = {config[section][key]}")


def main():
    parser = argparse.ArgumentParser(
        description="Claudememv2 - Intelligent memory system for Claude Code"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # save command
    save_parser = subparsers.add_parser("save", help="Save current session to memory")
    save_parser.add_argument("--messages", "-m", type=int, help="Max messages to save (0=all)")
    save_parser.add_argument("--full", action="store_true", help="Include thinking process")
    save_parser.add_argument("--minimal", action="store_true", help="Only user/assistant messages")
    save_parser.add_argument("--all", action="store_true", help="Save all messages")
    save_parser.add_argument("--project", "-p", help="Override project name")
    save_parser.set_defaults(func=cmd_save)

    # search command
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=6, help="Max results")
    search_parser.add_argument("--project", "-p", help="Search in specific project")
    search_parser.add_argument("--threshold", "-t", type=float, default=0.35, help="Min score")
    search_parser.set_defaults(func=cmd_search)

    # index command
    index_parser = subparsers.add_parser("index", help="Index all memory files")
    index_parser.add_argument("--force", "-f", action="store_true", help="Force full reindex")
    index_parser.set_defaults(func=cmd_index)

    # status command
    status_parser = subparsers.add_parser("status", help="Show memory status")
    status_parser.set_defaults(func=cmd_status)

    # cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old memories")
    cleanup_parser.add_argument("--days", "-d", type=int, help="Delete files older than N days")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    cleanup_parser.set_defaults(func=cmd_cleanup)

    # config command
    config_parser = subparsers.add_parser("config", help="View or modify configuration")
    config_parser.add_argument("key", nargs="?", help="Config key")
    config_parser.add_argument("value", nargs="?", help="New value")
    config_parser.set_defaults(func=cmd_config)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
