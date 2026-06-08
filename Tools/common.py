#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import re
import hashlib
import subprocess
from pathlib import Path

# ── Path Constants ──────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "Wiki"
RAW_DIR = REPO_ROOT / "Raw"
GRAPH_DIR = REPO_ROOT / "Graph"
LOG_FILE = WIKI_DIR / "log.md"
INDEX_FILE = WIKI_DIR / "index.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"


# ── I/O Tools ───────────────────────────────────────────────────────

def ensure_utf8():
    """Ensure standard input/output streams use UTF-8 on Windows."""
    if sys.platform.startswith("win"):
        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["PYTHONUTF8"] = "1"
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass


def init_env():
    """Initialize environment, ensure required directories exist, and configure encodings."""
    ensure_utf8()
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)


def read_file(path: Path | str) -> str:
    """Read file content with UTF-8 encoding, handling errors gracefully."""
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return p.read_text(encoding="gbk", errors="replace")
        except Exception:
            return ""
    except Exception:
        return ""


def write_file(path: Path | str, content: str):
    """Write content to file atomically, ensuring parent directory exists."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file first and rename to ensure atomicity
    temp_p = p.with_suffix(p.suffix + ".tmp")
    try:
        temp_p.write_text(content, encoding="utf-8")
        if p.exists():
            p.unlink()
        temp_p.rename(p)
    except Exception as e:
        if temp_p.exists():
            try:
                temp_p.unlink()
            except Exception:
                pass
        # Fallback to direct write
        p.write_text(content, encoding="utf-8")


# ── Content Tools ───────────────────────────────────────────────────

def extract_wikilinks(text: str) -> list[str]:
    """Extract all targets of [[wikilinks]] from text."""
    # Matches [[target]] or [[target|label]]
    links = re.findall(r'\[\[([^\]\|]+?)(?:\|[^\]]*)?\]\]', text)
    return [l.strip() for l in links]


def all_wiki_pages() -> list[Path]:
    """Return all markdown files under WIKI_DIR recursively, excluding index.md, log.md, and reports."""
    if not WIKI_DIR.exists():
        return []
    pages = []
    for p in WIKI_DIR.rglob("*.md"):
        # Exclude index.md, log.md, and reports at any level
        if p.name in ("index.md", "log.md", "health-report.md", "lint-report.md"):
            continue
        pages.append(p)
    return sorted(pages)


def append_log(entry: str):
    """Append a log entry to Wiki/log.md, ensuring a trailing newline."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not entry.endswith("\n"):
        entry += "\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def resolve_wikilink(name: str) -> list[Path]:
    """Resolve a wikilink string to a list of matching Path objects under WIKI_DIR.
    
    If the link is a Raw/ provenance marker (starts with 'raw/'), returns [].
    Otherwise, search for the page in WIKI_DIR.
    """
    if name.lower().startswith("raw/"):
        return []
    
    # Try resolving as an absolute-like path from REPO_ROOT (e.g. "Wiki/concepts/A.md")
    path_with_ext = name if name.endswith(".md") else f"{name}.md"
    repo_path = REPO_ROOT / path_with_ext
    if repo_path.is_file():
        return [repo_path]
    
    # Also support name without "Wiki/" prefix, e.g. "concepts/A"
    if not name.lower().startswith("wiki/"):
        wiki_path = WIKI_DIR / path_with_ext
        if wiki_path.is_file():
            return [wiki_path]
            
    # Also support pure filename shorthand, e.g. "A" -> search in all subdirectories of Wiki/
    target_name = Path(path_with_ext).name.lower()
    matches = []
    for p in all_wiki_pages():
        if p.name.lower() == target_name:
            matches.append(p)
    return matches


def load_allowed_raw_dirs() -> set[str]:
    """Load allowed Raw/ subdirectories.
    
    Reads Tools/.raw_dirs if present, otherwise returns defaults.
    """
    raw_dirs_file = REPO_ROOT / "Tools" / ".raw_dirs"
    if raw_dirs_file.exists():
        try:
            lines = raw_dirs_file.read_text(encoding="utf-8").splitlines()
            return {line.strip().lower() for line in lines if line.strip() and not line.strip().startswith("#")}
        except Exception:
            pass
    return {"sources", "thoughts", "records", "assets"}


# ── Hash Tools ──────────────────────────────────────────────────────

def sha256_full(content: str | bytes) -> str:
    """Compute full sha256 hex digest of string or bytes."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def sha256_short(content: str | bytes) -> str:
    """Compute short (8-char) sha256 hex digest of string or bytes."""
    return sha256_full(content)[:8]


# ── LLM Calling ─────────────────────────────────────────────────────

def call_llm(prompt: str, model_env_var: str | None = None, default_model: str | None = None, **kwargs) -> str:
    """Invoke LLM via opencode CLI, claude CLI, or environment variables.
    
    依次尝试 opencode / claude CLI；支持 LLM_BACKEND 环境变量覆盖；
    exit_on_error=False 时返回占位符而非抛异常.
    """
    exit_on_error = kwargs.get("exit_on_error", True)
    
    backend = os.environ.get("LLM_BACKEND", "").lower()
    
    cmds_to_try = []
    if backend == "opencode":
        cmds_to_try = [["opencode", prompt]]
    elif backend == "claude":
        cmds_to_try = [["claude", prompt]]
    else:
        cmds_to_try = [
            ["opencode", prompt],
            ["claude", prompt]
        ]
        
    for cmd in cmds_to_try:
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                shell=True,
                timeout=60
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            continue
            
    if exit_on_error:
        print("Error: Failed to invoke LLM through opencode or claude CLI.", file=sys.stderr)
        sys.exit(1)
    else:
        return "<!-- LLM Call Failed Placeholder -->\n"
