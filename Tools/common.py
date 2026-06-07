#!/usr/bin/env python3
"""Shared utilities for all LLM Wiki tools."""

import hashlib
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "Wiki"
RAW_DIR = REPO_ROOT / "Raw"
LOG_FILE = WIKI_DIR / "log.md"
INDEX_FILE = WIKI_DIR / "index.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"
GRAPH_DIR = REPO_ROOT / "Graph"

WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def init_env():
    """Auto-configure LLM env vars from opencode.json provider config.
    
    Also reconfigures stdout/stderr to UTF-8 on Windows.
    """
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONUTF8", "1")
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    config_paths = [
        REPO_ROOT / "opencode.json",
        REPO_ROOT / "opencode.jsonc",
        Path.home() / ".config" / "opencode" / "opencode.json",
    ]
    for cfg in config_paths:
        if cfg.exists():
            try:
                import json
                data = json.loads(cfg.read_text(encoding="utf-8"))
                provider = data.get("provider", {})
                # Find the first provider with baseURL + models
                for name, conf in provider.items():
                    if not isinstance(conf, dict):
                        continue
                    opts = conf.get("options") or {}
                    base_url = opts.get("baseURL", "").rstrip("/")
                    models = conf.get("models") or {}
                    if base_url and models:
                        model_name = next(iter(models.keys()))
                        os.environ.setdefault("OPENAI_API_BASE", base_url)
                        os.environ.setdefault("LLM_MODEL", f"openai/{model_name}")
                        os.environ.setdefault("OPENAI_API_KEY", "sk-no-key-required")
                        break
            except (json.JSONDecodeError, KeyError, IOError):
                pass
            break


def ensure_utf8():
    """On Windows, warn if PYTHONUTF8 is not set."""
    if sys.platform == "win32" and not os.environ.get("PYTHONUTF8"):
        print("  [hint] Set $env:PYTHONUTF8=1 to prevent encoding issues with CJK/emoji.")


def read_file(path: Path) -> str:
    """Read a file as UTF-8, returning '' if missing."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return ""


def write_file(path: Path, content: str):
    """Write a file to disk, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote: {path.relative_to(REPO_ROOT)}")


def sha256_short(text: str) -> str:
    """16-char SHA-256 fingerprint (used by ingest/refresh for change detection)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def sha256_full(text: str) -> str:
    """Full 64-char SHA-256 hash (used by build_graph for content integrity)."""
    return hashlib.sha256(text.encode()).hexdigest()


def call_llm(prompt: str, model_env: str = "LLM_MODEL",
             default_model: str = "claude-3-5-sonnet-latest",
             max_tokens: int = 4096, *, exit_on_error: bool = True) -> str:
    """Call litellm completion with consistent error handling.

    If *exit_on_error* is True (default), sys.exit(1) on failure.
    Otherwise returns a fallback string.
    """
    try:
        from litellm import completion
    except ImportError:
        msg = "Error: litellm not installed. Run: pip install litellm"
        if exit_on_error:
            print(msg); sys.exit(1)
        return f"> Semantic lint skipped: `litellm` not installed."

    model = os.getenv(model_env, default_model)
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        msg = response.choices[0].message
        # Thinking models (e.g. Qwen3.5, DeepSeek-R1) put output in
        # reasoning_content and leave content empty — fall back.
        if not msg.content and hasattr(msg, "reasoning_content"):
            return msg.reasoning_content or ""
        return msg.content or ""
    except Exception as e:
        if exit_on_error:
            print(f"Error: API call failed: {e}")
            sys.exit(1)
        return f"> API call failed: {e}"


def extract_wikilinks(content: str) -> list[str]:
    """Extract all [[WikiLink]] targets from page content, stripping display aliases."""
    links = WIKILINK_RE.findall(content)
    return [link.split("|")[0].split("#")[0] for link in links]


def all_wiki_pages() -> list[Path]:
    """Return all .md files under Wiki/, excluding meta pages."""
    exclude = {"index.md", "log.md", "lint-report.md", "health-report.md"}
    return [p for p in WIKI_DIR.rglob("*.md") if p.name not in exclude]


def append_log(entry: str):
    """Prepend an entry to Wiki/log.md."""
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")
