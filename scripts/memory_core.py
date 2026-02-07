#!/usr/bin/env python3
"""
Claudememv2 Memory Core
Main entry point for memory operations: save, search, index, status, cleanup
"""

import argparse
import json
import os
import sys
import shutil
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
from logger import setup_logger

log = setup_logger("claudememv2.core")


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
        },
        "summary": {
            "enabled": True,
            "format": "structured",
            "timing": "on_save"
        }
    }

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key in user_config:
                        if isinstance(default_config[key], dict):
                            default_config[key].update(user_config[key])
                        else:
                            default_config[key] = user_config[key]
                # Also copy any extra keys from user config
                for key in user_config:
                    if key not in default_config:
                        default_config[key] = user_config[key]
                return default_config
        except Exception as e:
            log.warning("Could not load config from %s: %s", config_path, e)
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
        log.info("Session saved: %s (%d messages, project=%s)", result['file_path'], result['message_count'], result['project'])
        print(f"[OK] Session saved to memory")
        print(f"  File: {result['file_path']}")
        print(f"  Messages: {result['message_count']}")
        print(f"  Project: {result['project']}")
    except Exception as e:
        log.error("Error saving session: %s", e, exc_info=True)
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

        log.info("Search completed: query='%s', results=%d", args.query, len(results))
        print(f"[SEARCH] Search results (query: \"{args.query}\")\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['score']:.2f}] {result['file']}:{result['lines']}")
            print(f"   \"{result['excerpt'][:100]}...\"\n")
    except Exception as e:
        log.error("Error searching: %s", e, exc_info=True)
        print(f"[ERROR] Error searching: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_index(args):
    """Index all memory files."""
    config = load_config()
    engine = SearchEngine(config)

    try:
        result = engine.index(force=args.force)
        log.info("Index updated: scanned=%d, new=%d, updated=%d, chunks=%d", result['scanned'], result['new'], result['updated'], result['chunks'])
        print(f"[INDEX] Memory index updated")
        print(f"  Files scanned: {result['scanned']}")
        print(f"  New indexed: {result['new']}")
        print(f"  Updated: {result['updated']}")
        print(f"  Total chunks: {result['chunks']}")
    except Exception as e:
        log.error("Error indexing: %s", e, exc_info=True)
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

    # Get model info - read actual model from Claude Code settings
    model_source = config["model"]["source"]
    model_str = config["model"].get("fallback", "unknown")

    try:
        if sys.platform == "win32":
            settings_path = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "settings.json"
        else:
            settings_path = Path.home() / ".claude" / "settings.json"

        if settings_path.exists():
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                env = settings.get("env", {})

                model_map = {
                    "inherit": "ANTHROPIC_MODEL",
                    "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
                    "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
                    "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
                }

                if model_source == "custom":
                    model_str = config["model"].get("customModelId", model_str)
                elif model_source in model_map and model_map[model_source] in env:
                    model_str = f"{env[model_map[model_source]]} ({model_source})"
                elif "ANTHROPIC_MODEL" in env:
                    model_str = f"{env['ANTHROPIC_MODEL']} (inherit)"
    except Exception:
        pass

    print(f"[STATUS] Claudememv2 Memory Status")
    print(f"  Projects: {projects}")
    print(f"  Files: {files}")
    print(f"  Total size: {size_str}")
    print(f"  Last updated: {latest_update.strftime('%Y-%m-%d %H:%M:%S') if latest_update else 'Never'}")
    print(f"  Model: {model_str}")
    print(f"  Content scope: {config['memory']['contentScope']}")
    print(f"  Max messages: {config['memory']['maxMessages'] or 'unlimited'}")

    # 显示摘要配置
    summary_config = config.get("summary", {})
    summary_enabled = summary_config.get("enabled", True)
    summary_format = summary_config.get("format", "structured")
    summary_timing = summary_config.get("timing", "on_save")

    format_names = {
        "structured": "结构化",
        "freeform": "自由格式",
        "mixed": "混合格式"
    }
    timing_names = {
        "on_save": "保存时生成",
        "async": "异步生成",
        "on_demand": "按需生成",
        "disabled": "禁用"
    }

    if summary_enabled and summary_timing != "disabled":
        print(f"  Summary format: {format_names.get(summary_format, summary_format)}")
        print(f"  Summary timing: {timing_names.get(summary_timing, summary_timing)}")
    else:
        print(f"  Summary: disabled")


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


def cmd_export(args):
    """Export memories to Markdown or JSON format."""
    config = load_config()
    data_dir = Path(config["memory"]["dataDir"]).expanduser()
    memory_dir = data_dir / "memory"

    if not memory_dir.exists():
        print("[ERROR] No memories found. Memory directory does not exist.", file=sys.stderr)
        sys.exit(1)

    # Collect target project directories
    project_dirs = []
    if args.project:
        target = memory_dir / args.project
        if not target.exists():
            print(f"[ERROR] Project '{args.project}' not found.", file=sys.stderr)
            sys.exit(1)
        project_dirs.append(target)
    else:
        for d in sorted(memory_dir.iterdir()):
            if d.is_dir():
                project_dirs.append(d)

    if not project_dirs:
        print("[ERROR] No projects found in memory.", file=sys.stderr)
        sys.exit(1)

    # Determine source: summary (default) or full
    use_full = args.full

    # Collect all memory files
    memories = []
    for project_dir in project_dirs:
        project_name = project_dir.name
        source_dir = project_dir / "full" if use_full else project_dir
        if use_full and not source_dir.exists():
            source_dir = project_dir  # fallback to summary

        for md_file in sorted(source_dir.glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                stat = md_file.stat()
                memories.append({
                    "project": project_name,
                    "filename": md_file.name,
                    "path": str(md_file),
                    "content": content,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size,
                })
            except (OSError, PermissionError) as e:
                print(f"  Warning: Could not read {md_file}: {e}", file=sys.stderr)

    if not memories:
        print("[ERROR] No memory files found to export.", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    fmt = args.format
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        suffix = "full" if use_full else "summary"
        if args.project:
            output_path = Path(f"claudememv2-export-{args.project}-{suffix}-{timestamp}.{fmt}")
        else:
            output_path = Path(f"claudememv2-export-all-{suffix}-{timestamp}.{fmt}")

    try:
        if fmt == "json":
            _export_json(memories, output_path)
        else:
            _export_markdown(memories, output_path)

        log.info("Export completed: format=%s, files=%d, output=%s", fmt, len(memories), output_path)
        print(f"[OK] Memories exported successfully")
        print(f"  Format: {fmt}")
        print(f"  Source: {'full conversations' if use_full else 'summaries'}")
        print(f"  Files: {len(memories)}")
        print(f"  Projects: {len(project_dirs)}")
        print(f"  Output: {output_path}")
    except (OSError, PermissionError) as e:
        log.error("Failed to write export file: %s", e, exc_info=True)
        print(f"[ERROR] Failed to write export file: {e}", file=sys.stderr)
        sys.exit(1)


def _export_markdown(memories, output_path):
    """Export memories as a single Markdown document."""
    lines = []
    lines.append("# Claudememv2 Memory Export")
    lines.append(f"\n> Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> Total files: {len(memories)}\n")

    current_project = None
    for mem in memories:
        if mem["project"] != current_project:
            current_project = mem["project"]
            lines.append(f"\n---\n\n## Project: {current_project}\n")

        lines.append(f"### {mem['filename']}\n")
        lines.append(f"*Modified: {mem['modified'][:10]} | Size: {mem['size']} bytes*\n")
        lines.append(mem["content"])
        lines.append("\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _export_json(memories, output_path):
    """Export memories as a JSON file."""
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "total_files": len(memories),
        "projects": {},
    }

    for mem in memories:
        project = mem["project"]
        if project not in export_data["projects"]:
            export_data["projects"][project] = []
        export_data["projects"][project].append({
            "filename": mem["filename"],
            "created": mem["created"],
            "modified": mem["modified"],
            "size": mem["size"],
            "content": mem["content"],
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


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

    # export command
    export_parser = subparsers.add_parser("export", help="Export memories to file")
    export_parser.add_argument("--format", "-f", choices=["md", "json"], default="md", help="Export format (default: md)")
    export_parser.add_argument("--project", "-p", help="Export specific project only")
    export_parser.add_argument("--output", "-o", help="Output file path")
    export_parser.add_argument("--full", action="store_true", help="Export full conversations instead of summaries")
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
