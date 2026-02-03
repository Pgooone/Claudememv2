#!/usr/bin/env python3
"""
Claudememv2 Search Engine
Semantic search using Claude API
"""

import json
import os
import sqlite3
import hashlib
import re
from pathlib import Path
from typing import Optional

# Try to import anthropic for semantic search
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class SearchEngine:
    """Search engine for memory files using Claude API."""

    def __init__(self, config: dict):
        self.config = config
        self.memory_config = config.get("memory", {})
        self.model_config = config.get("model", {})

        # Get data directory
        data_dir = self.memory_config.get("dataDir", "~/.claude/Claudememv2-data")
        self.data_dir = Path(data_dir).expanduser()
        self.memory_dir = self.data_dir / "memory"
        self.db_path = self.data_dir / "memory.sqlite"

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                project TEXT NOT NULL,
                hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (file_path) REFERENCES files(path)
            )
        """)

        # Create FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                content,
                id UNINDEXED,
                file_path UNINDEXED,
                content=chunks,
                content_rowid=rowid,
                tokenize='trigram'
            )
        """)

        conn.commit()
        conn.close()

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

    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _chunk_content(self, content: str, max_chars: int = 1600, overlap: int = 320) -> list:
        """Split content into chunks."""
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_chars = 0
        start_line = 1

        for i, line in enumerate(lines, 1):
            # Check for heading (new section)
            if re.match(r"^#{1,6}\s", line) and current_chunk:
                chunks.append({
                    "start_line": start_line,
                    "end_line": i - 1,
                    "content": "\n".join(current_chunk)
                })
                # Keep overlap
                overlap_lines = []
                overlap_chars = 0
                for prev_line in reversed(current_chunk):
                    if overlap_chars + len(prev_line) > overlap:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_chars += len(prev_line)

                current_chunk = overlap_lines
                current_chars = overlap_chars
                start_line = i - len(overlap_lines)

            current_chunk.append(line)
            current_chars += len(line)

            # Check if chunk is too large
            if current_chars > max_chars:
                chunks.append({
                    "start_line": start_line,
                    "end_line": i,
                    "content": "\n".join(current_chunk)
                })
                # Keep overlap
                overlap_lines = []
                overlap_chars = 0
                for prev_line in reversed(current_chunk):
                    if overlap_chars + len(prev_line) > overlap:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_chars += len(prev_line)

                current_chunk = overlap_lines
                current_chars = overlap_chars
                start_line = i - len(overlap_lines) + 1

        # Add remaining content
        if current_chunk:
            chunks.append({
                "start_line": start_line,
                "end_line": len(lines),
                "content": "\n".join(current_chunk)
            })

        return chunks

    def index(self, force: bool = False) -> dict:
        """Index memory files based on searchScope config."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        scanned = 0
        new_indexed = 0
        updated = 0

        if not self.memory_dir.exists():
            return {"scanned": 0, "new": 0, "updated": 0, "chunks": 0}

        # Get search scope from config
        search_scope = self.memory_config.get("searchScope", "summary")

        # Get existing file hashes
        existing_files = {}
        if not force:
            cursor.execute("SELECT path, hash FROM files")
            existing_files = {row[0]: row[1] for row in cursor.fetchall()}

        # Scan memory directory
        for project_dir in self.memory_dir.iterdir():
            if not project_dir.is_dir():
                continue

            project = project_dir.name

            # Index summary files (not in full/ directory)
            if search_scope in ("summary", "both"):
                for md_file in project_dir.glob("*.md"):
                    scanned += 1
                    rel_path = str(md_file.relative_to(self.memory_dir))

                    result = self._index_file(cursor, md_file, rel_path, project, existing_files, force)
                    if result == "new":
                        new_indexed += 1
                    elif result == "updated":
                        updated += 1

            # Index full files (in full/ directory)
            if search_scope in ("full", "both"):
                full_dir = project_dir / "full"
                if full_dir.exists():
                    for md_file in full_dir.glob("*.md"):
                        scanned += 1
                        rel_path = str(md_file.relative_to(self.memory_dir))

                        result = self._index_file(cursor, md_file, rel_path, project, existing_files, force)
                        if result == "new":
                            new_indexed += 1
                        elif result == "updated":
                            updated += 1

        # Rebuild FTS index
        cursor.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")

        conn.commit()

        # Get total chunks
        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cursor.fetchone()[0]

        conn.close()

        return {
            "scanned": scanned,
            "new": new_indexed,
            "updated": updated,
            "chunks": total_chunks
        }

    def _index_file(self, cursor, md_file: Path, rel_path: str, project: str, existing_files: dict, force: bool) -> str:
        """Index a single file. Returns 'new', 'updated', or 'skip'."""
        # Read file content
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        file_hash = self._compute_hash(content)

        # Check if file needs indexing
        if not force and rel_path in existing_files:
            if existing_files[rel_path] == file_hash:
                return "skip"
            result = "updated"
        else:
            result = "new"

        # Remove old chunks
        cursor.execute("DELETE FROM chunks WHERE file_path = ?", (rel_path,))

        # Update file record
        cursor.execute("""
            INSERT OR REPLACE INTO files (path, project, hash, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (rel_path, project, file_hash))

        # Chunk and index content
        chunks = self._chunk_content(content)
        for chunk in chunks:
            chunk_id = f"{rel_path}:{chunk['start_line']}-{chunk['end_line']}"
            cursor.execute("""
                INSERT INTO chunks (id, file_path, start_line, end_line, content)
                VALUES (?, ?, ?, ?, ?)
            """, (chunk_id, rel_path, chunk["start_line"], chunk["end_line"], chunk["content"]))

        return result

    def search(self, query: str, limit: int = 6, project: Optional[str] = None, threshold: float = 0.35) -> list:
        """Search memories using Claude API for semantic matching."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all chunks (optionally filtered by project)
        if project:
            cursor.execute("""
                SELECT c.id, c.file_path, c.start_line, c.end_line, c.content
                FROM chunks c
                JOIN files f ON c.file_path = f.path
                WHERE f.project = ?
            """, (project,))
        else:
            cursor.execute("""
                SELECT id, file_path, start_line, end_line, content
                FROM chunks
            """)

        chunks = cursor.fetchall()

        if not chunks:
            conn.close()
            return []

        # Also do FTS search for hybrid results
        fts_scores = {}
        try:
            cursor.execute("""
                SELECT id, bm25(chunks_fts) as score
                FROM chunks_fts
                WHERE chunks_fts MATCH ?
                ORDER BY score
                LIMIT ?
            """, (query, limit * 2))
            for row in cursor.fetchall():
                # BM25 returns negative scores, lower is better
                fts_scores[row[0]] = -row[1]
        except Exception:
            pass

        conn.close()

        # Use Claude API for semantic search
        if HAS_ANTHROPIC and chunks:
            results = self._semantic_search(query, chunks, fts_scores, limit, threshold)
        else:
            # Fallback to FTS only
            results = []
            for chunk_id, score in sorted(fts_scores.items(), key=lambda x: -x[1])[:limit]:
                for chunk in chunks:
                    if chunk[0] == chunk_id:
                        results.append({
                            "file": chunk[1],
                            "lines": f"{chunk[2]}-{chunk[3]}",
                            "score": min(score / 10, 1.0),  # Normalize
                            "excerpt": chunk[4][:200]
                        })
                        break

        return results

    def _semantic_search(self, query: str, chunks: list, fts_scores: dict, limit: int, threshold: float) -> list:
        """Use Claude API for semantic search."""
        try:
            model = self._get_model()
            client = anthropic.Anthropic()

            # Prepare chunks for evaluation (limit to avoid token limits)
            eval_chunks = chunks[:50]  # Evaluate top 50 chunks

            # Build prompt
            chunk_texts = []
            for i, chunk in enumerate(eval_chunks):
                chunk_texts.append(f"[{i}] {chunk[4][:500]}")

            prompt = f"""Rate the relevance of each text chunk to the query on a scale of 0-100.
Only output a JSON array of scores in the same order as the chunks.

Query: {query}

Chunks:
{chr(10).join(chunk_texts)}

Output format: [score1, score2, ...]
Scores:"""

            response = client.messages.create(
                model=model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse scores
            scores_text = response.content[0].text.strip()
            # Extract JSON array
            match = re.search(r"\[[\d,\s]+\]", scores_text)
            if match:
                scores = json.loads(match.group())
            else:
                scores = [50] * len(eval_chunks)

            # Combine with FTS scores (70% semantic, 30% FTS)
            results = []
            for i, chunk in enumerate(eval_chunks):
                semantic_score = scores[i] / 100 if i < len(scores) else 0.5
                fts_score = fts_scores.get(chunk[0], 0) / 10  # Normalize FTS

                combined_score = 0.7 * semantic_score + 0.3 * min(fts_score, 1.0)

                if combined_score >= threshold:
                    results.append({
                        "file": chunk[1],
                        "lines": f"{chunk[2]}-{chunk[3]}",
                        "score": combined_score,
                        "excerpt": chunk[4][:200]
                    })

            # Sort by score and limit
            results.sort(key=lambda x: -x["score"])
            return results[:limit]

        except Exception as e:
            # Fallback to FTS only on error
            results = []
            for chunk in chunks:
                fts_score = fts_scores.get(chunk[0], 0)
                if fts_score > 0:
                    results.append({
                        "file": chunk[1],
                        "lines": f"{chunk[2]}-{chunk[3]}",
                        "score": min(fts_score / 10, 1.0),
                        "excerpt": chunk[4][:200]
                    })

            results.sort(key=lambda x: -x["score"])
            return results[:limit]
