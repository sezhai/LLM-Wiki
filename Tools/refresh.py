#!/usr/bin/env python3
"""
Refresh stale source pages by re-ingesting from raw documents.

Usage:
    python tools/refresh.py                     # refresh only changed sources
    python tools/refresh.py --force             # force re-ingest all sources
    python tools/refresh.py --page sources/X    # refresh a specific page
    python tools/refresh.py --dry-run           # list stale pages without refreshing

Source-of-truth for "already ingested" state is Wiki/log.md (sha256: field).
Graph/.refresh_cache.json is used as a fast-path cache to avoid re-reading
all Raw/ files on every run, but the log.md record is always authoritative.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import date

from common import (
    REPO_ROOT, WIKI_DIR, RAW_DIR, LOG_FILE,
    read_file, sha256_short, sha256_full, append_log, ensure_utf8, init_env,
)

SOURCES_DIR = WIKI_DIR / "sources"
REFRESH_CACHE = REPO_ROOT / "Graph" / ".refresh_cache.json"


def load_refresh_cache() -> dict:
    if REFRESH_CACHE.exists():
        try:
            return json.loads(REFRESH_CACHE.read_text())
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_refresh_cache(cache: dict):
    REFRESH_CACHE.parent.mkdir(parents=True, exist_ok=True)
    REFRESH_CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def extract_source_file(content: str) -> str | None:
    """Extract raw document path from YAML frontmatter.

    Supports two formats to match AGENTS.md §3.3 (source_map template):

    1. Standard (AGENTS.md §3.3):
         raw_link: "[[Raw/Sources/path/to/file.md]]"
       The double-bracket wikilink format is stripped to yield the bare path.

    2. Legacy / hand-written:
         source_file: Raw/Sources/path/to/file.md
       Accepted for backwards compatibility.

    Returns the bare path string (e.g. "Raw/Sources/foo.md"), or None if
    neither field is found.
    """
    # Primary: raw_link with wikilink syntax  [[Raw/...]]
    m = re.search(
        r'^raw_link:\s*["\']?\[\[([^\]]+)\]\]["\']?',
        content, re.MULTILINE
    )
    if m:
        return m.group(1).strip()

    # Fallback: legacy source_file field (bare path)
    m = re.search(r'^source_file:\s*(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")


def _recorded_hash_from_log(raw_rel: str) -> str | None:
    """Look up the sha256 recorded in log.md for a given Raw/ file path.

    Scans log.md for entries containing the file path and a sha256: field.
    Returns the most recently recorded hash (log.md is newest-first), or None.

    This is the authoritative source for "what hash was ingested" per v4.0 design.
    """
    log_content = read_file(LOG_FILE)
    if not log_content:
        return None
    filename = Path(raw_rel).name
    for line in log_content.splitlines():
        if raw_rel not in line and filename not in line:
            continue
        m = re.search(r'sha256:([0-9a-f]{8,64})', line)
        if m:
            return m.group(1)
    return None


def find_stale_sources(force: bool = False) -> list[tuple[Path, Path]]:
    """Return list of (wiki_source_page, raw_document) pairs that need refresh.

    Uses log.md sha256 as the authoritative baseline (v4.0 design).
    Falls back to the local .refresh_cache.json for files not yet in log.md
    (e.g. ingested before v4.0 log format was adopted).
    """
    cache = load_refresh_cache()
    stale = []

    if not SOURCES_DIR.exists():
        return stale

    for wiki_page in sorted(SOURCES_DIR.glob("*.md")):
        content = read_file(wiki_page)
        source_file = extract_source_file(content)
        if not source_file:
            continue

        raw_path = REPO_ROOT / source_file
        if not raw_path.exists():
            raw_path = RAW_DIR / source_file
            if not raw_path.exists():
                continue

        try:
            raw_rel = raw_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            raw_rel = source_file

        raw_bytes = raw_path.read_bytes()
        current_full = sha256_full(raw_bytes.decode("utf-8", errors="replace"))
        current_short = current_full[:8]

        if force:
            stale.append((wiki_page, raw_path))
            continue

        # Primary: check log.md (authoritative v4.0 source)
        recorded = _recorded_hash_from_log(raw_rel)
        if recorded is not None:
            # Accept both short (8-char) and full (64-char) recorded hashes
            match = (recorded == current_full) or (recorded == current_short)
            if not match:
                stale.append((wiki_page, raw_path))
            # Update local cache to stay in sync
            cache[str(raw_path)] = current_short
            continue

        # Fallback: no log.md entry — check local cache (pre-v4.0 compat)
        cached_hash = cache.get(str(raw_path))
        if cached_hash != current_short:
            stale.append((wiki_page, raw_path))

    return stale


def refresh_page(wiki_page: Path, raw_path: Path) -> bool:
    """Re-ingest a single source document."""
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from ingest import ingest
        print(f"\n{'='*60}")
        print(f"  Refreshing: {wiki_page.name}")
        print(f"  From:       {raw_path}")
        print(f"{'='*60}")
        return ingest(str(raw_path))
    except Exception as e:
        print(f"  [ERROR] Failed to refresh {wiki_page.name}: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Refresh stale wiki source pages")
    parser.add_argument("--force", action="store_true", help="Force re-ingest all sources")
    parser.add_argument("--page", type=str, help="Refresh a specific wiki source page (e.g., sources/my-page)")
    parser.add_argument("--dry-run", action="store_true", help="Only list stale pages, don't refresh")
    args = parser.parse_args()

    if args.page:
        # Refresh a single specific page
        wiki_page = WIKI_DIR / args.page
        if not wiki_page.suffix:
            wiki_page = wiki_page.with_suffix(".md")
        if not wiki_page.exists():
            print(f"Page not found: {wiki_page}")
            sys.exit(1)
        content = read_file(wiki_page)
        source_file = extract_source_file(content)
        if not source_file:
            print(f"No source_file found in frontmatter of {wiki_page.name}")
            sys.exit(1)
        raw_path = REPO_ROOT / source_file
        if not raw_path.exists():
            raw_path = RAW_DIR / source_file
        if not raw_path.exists():
            print(f"Raw document not found: {source_file}")
            sys.exit(1)
        stale = [(wiki_page, raw_path)]
    else:
        stale = find_stale_sources(force=args.force)

    if not stale:
        print("All source pages are up to date. Nothing to refresh.")
        return

    print(f"Found {len(stale)} stale source page(s):")
    for wiki_page, raw_path in stale:
        print(f"  • {wiki_page.name} ← {raw_path.relative_to(REPO_ROOT)}")

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    # Refresh each stale page; update local cache on success
    cache = load_refresh_cache()
    refreshed = 0
    failed = 0

    for wiki_page, raw_path in stale:
        if refresh_page(wiki_page, raw_path):
            # Update local cache (log.md is updated by ingest() itself)
            raw_bytes = raw_path.read_bytes()
            cache[str(raw_path)] = sha256_full(
                raw_bytes.decode("utf-8", errors="replace")
            )[:8]
            refreshed += 1
        else:
            failed += 1

    save_refresh_cache(cache)

    print(f"\n{'='*60}")
    print(f"  Refresh complete: {refreshed} updated, {failed} failed")
    print(f"{'='*60}")

    today = date.today().isoformat()
    append_log(
        f"## [{today}] chore | refresh\n\n"
        f"Re-ingested {refreshed} stale source page(s)."
        + (f" {failed} failed — see ERROR entries in log.md." if failed else "")
    )


if __name__ == "__main__":
    init_env()
    ensure_utf8()
    main()
