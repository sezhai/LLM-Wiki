#!/usr/bin/env python3
from __future__ import annotations

"""
Structural health checks for the LLM Wiki.

Unlike lint.py (which includes expensive LLM-powered semantic analysis),
health.py is purely deterministic — zero API calls, fast enough to run
every session.

Usage:
    python tools/health.py              # print report to stdout
    python tools/health.py --save       # also save to wiki/health-report.md
    python tools/health.py --json       # machine-readable output

Checks:
  - Empty / stub files (pages with no real content beyond frontmatter)
  - Index sync (wiki/index.md entries vs actual files on disk)
  - Log coverage (source pages without a corresponding log entry)

Design boundary (see AGENTS.md):
  health.py = structural integrity, deterministic, run every session
  lint.py   = content quality, semantic (LLM), run every 10-15 ingests
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import date

from common import REPO_ROOT, WIKI_DIR, RAW_DIR, INDEX_FILE, LOG_FILE, read_file, all_wiki_pages, ensure_utf8, init_env

# Minimum content length (excluding frontmatter) to not be considered a stub
STUB_THRESHOLD_CHARS = 100


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter (--- ... ---) from content."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].strip()
    return content.strip()


# ── Check: Empty / Stub files ───────────────────────────────────────

def check_empty_files(pages: list[Path], threshold: int = STUB_THRESHOLD_CHARS) -> list[dict]:
    """Find wiki pages that are empty or contain only frontmatter / minimal content."""
    results = []
    for p in pages:
        raw = read_file(p)
        body = strip_frontmatter(raw)
        if len(body) < threshold:
            results.append({
                "path": str(p.relative_to(REPO_ROOT)),
                "total_bytes": len(raw),
                "body_bytes": len(body),
                "status": "empty" if len(body) == 0 else "stub",
            })
    results.sort(key=lambda x: x["body_bytes"])
    return results


# ── Check: Index sync ───────────────────────────────────────────────

def _parse_index_links(index_content: str) -> set[str]:
    """Extract markdown link targets from index.md.

    Matches patterns like: [Title](sources/slug.md)
    Returns set of relative paths (e.g. 'sources/slug.md').
    """
    return set(re.findall(r'\[.*?\]\(([^)]+\.md)\)', index_content))


def check_index_sync(pages: list[Path]) -> dict:
    """Compare wiki/index.md entries against actual files on disk.

    Returns:
        {
            "in_index_not_on_disk": [...],   # stale index entries
            "on_disk_not_in_index": [...],   # missing from index
        }
    """
    index_content = read_file(INDEX_FILE)
    index_links = _parse_index_links(index_content)

    # Normalize index links to absolute paths for comparison
    # overview.md is listed under ## Overview, not in the per-type sections.
    # Exclude it from both sides to avoid false positives.
    meta_pages = {"overview.md"}

    index_paths = set()
    for link in index_links:
        resolved = (WIKI_DIR / link).resolve()
        if Path(link).name not in meta_pages:
            index_paths.add(resolved)

    disk_paths = set()
    for p in pages:
        if p.name not in meta_pages:
            disk_paths.add(p.resolve())

    in_index_not_on_disk = [
        str(p.relative_to(REPO_ROOT)) for p in sorted(index_paths - disk_paths)
        if REPO_ROOT in p.parents or p == REPO_ROOT
    ]
    on_disk_not_in_index = [
        str(p.relative_to(REPO_ROOT)) for p in sorted(disk_paths - index_paths)
    ]

    return {
        "in_index_not_on_disk": in_index_not_on_disk,
        "on_disk_not_in_index": on_disk_not_in_index,
    }


# ── Check: Log coverage ────────────────────────────────────────────

def _parse_log_entries(log_content: str) -> set[str]:
    """Extract page titles/slugs from log.md entries.

    Log format: ## [YYYY-MM-DD] ingest | Title Here
    Returns set of lowercase title strings.
    """
    return set(
        m.group(1).strip().lower()
        for m in re.finditer(r'^## \[\d{4}-\d{2}-\d{2}\] ingest \| ([^|\n]+?)(?:\s*\|\s*\[\[.*)?$', log_content, re.MULTILINE)
    )


def _parse_frontmatter_title(content: str) -> str:
    """Extract and lightly unescape a frontmatter title scalar.

    Handles YAML-escaped quotes (e.g. title: "few \"people\" laptop")
    so that log coverage matching doesn't false-positive on escaped strings.
    """
    match = re.search(r'^title:\s*(.+?)\s*$', content, re.MULTILINE)
    if not match:
        return ""
    raw = match.group(1).strip()
    # Strip surrounding quotes and unescape inner ones
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        raw = raw[1:-1]
        raw = raw.replace(r'\"', '"').replace(r"\'", "'").replace(r"\\", "\\")
    elif len(raw) >= 2 and raw[0] == raw[-1] == "'":
        raw = raw[1:-1].replace("''", "'")
    return raw.strip().lower()


def check_log_coverage(pages: list[Path]) -> list[dict]:
    """Find source pages that have no corresponding ingest entry in log.md.

    Only checks wiki/sources/*.md — entity/concept pages are created as
    side-effects of ingest and don't need their own log entry.
    """
    log_content = read_file(LOG_FILE)
    logged_titles = _parse_log_entries(log_content)

    source_dir = WIKI_DIR / "sources"
    if not source_dir.exists():
        return []

    missing = []
    for p in sorted(source_dir.glob("*.md")):
        # Try matching by slug (filename without .md) or by frontmatter title
        slug = p.stem.lower().replace("-", " ").replace("_", " ")

        content = read_file(p)
        fm_title = _parse_frontmatter_title(content)

        if slug not in logged_titles and fm_title not in logged_titles:
            missing.append({
                "path": str(p.relative_to(REPO_ROOT)),
                "slug": p.stem,
                "title": fm_title or p.stem,
            })

    return missing


# ── Check: Broken wikilinks ────────────────────────────────────────

def check_broken_links(pages: list[Path]) -> list[dict]:
    """Find [[wikilinks]] pointing to non-existent pages (deterministic, no LLM).

    Skips Raw/ provenance markers — they are intentional citations, not navigable links.
    """
    existing_stems = {p.stem.lower() for p in pages}
    existing_paths = {
        p.relative_to(WIKI_DIR).as_posix().removesuffix(".md").lower()
        for p in pages
    }
    # Also accept vault-absolute format "Wiki/concepts/Foo"
    existing_vault = {"wiki/" + x for x in existing_paths}

    results = []
    for p in pages:
        content = read_file(p)
        rel = str(p.relative_to(REPO_ROOT))
        for link in re.findall(r'\[\[([^\]\|]+?)(?:\|[^\]]*)?\]\]', content):
            link = link.strip()
            # Skip image embeds handled separately
            if link.startswith("!"):
                continue
            # Skip Raw/ provenance markers
            nl = link.lower().replace("\\", "/")
            if nl.startswith("raw/"):
                continue
            # Normalize vault-absolute Wiki/ prefix
            if nl.startswith("wiki/"):
                nl_stem = nl[5:].removesuffix(".md")
            else:
                nl_stem = Path(nl).stem.lower()
                nl_path = nl.removesuffix(".md").lower()

            resolved = (
                nl_stem in existing_stems
                or nl.removesuffix(".md").lower() in existing_paths
                or nl.lower() in existing_vault
            )
            if not resolved:
                results.append({"page": rel, "link": link})
    return results


# ── Check: Assets broken links ─────────────────────────────────────

def check_assets_broken_links(pages: list[Path]) -> list[dict]:
    """Find ![[Raw/Assets/...]] image embeds whose target files don't exist.

    Direction: Wiki → Assets (does not flag unused assets as broken).
    """
    results = []
    assets_dir = RAW_DIR / "Assets"
    for p in pages:
        content = read_file(p)
        rel = str(p.relative_to(REPO_ROOT))
        # Match both ![[Raw/Assets/...]] and standard markdown ![...](Raw/Assets/...)
        embed_patterns = re.findall(
            r'!\[\[Raw/Assets/([^\]\|]+?)(?:\|[^\]]*)?\]\]'
            r'|!\[.*?\]\(Raw/Assets/([^)]+)\)',
            content,
        )
        for m in embed_patterns:
            fname = (m[0] or m[1]).strip()
            target = assets_dir / fname
            if not target.exists():
                results.append({"page": rel, "missing_asset": f"Raw/Assets/{fname}"})
    return results


# ── Check: Raw directory compliance ────────────────────────────────

def check_raw_compliance() -> list[str]:
    """Find subdirectories inside Raw/ that are not in the allowed whitelist.

    Allowed: Sources, Thoughts, Records, Assets (case-insensitive).
    Returns list of unexpected subdirectory paths relative to REPO_ROOT.
    """
    allowed = {"sources", "thoughts", "records", "assets"}
    unexpected = []
    if not RAW_DIR.exists():
        return []
    for child in RAW_DIR.iterdir():
        if child.is_dir() and child.name.lower() not in allowed:
            unexpected.append(str(child.relative_to(REPO_ROOT)))
    return sorted(unexpected)


# ── Report Generation ───────────────────────────────────────────────

def run_health() -> dict:
    """Run all health checks, return structured results."""
    pages = all_wiki_pages()

    return {
        "date": date.today().isoformat(),
        "total_pages": len(pages),
        "empty_files": check_empty_files(pages),
        "index_sync": check_index_sync(pages),
        "log_coverage": check_log_coverage(pages),
        "broken_links": check_broken_links(pages),
        "assets_broken_links": check_assets_broken_links(pages),
        "raw_compliance": check_raw_compliance(),
    }


def format_report(results: dict) -> str:
    """Format health check results as markdown."""
    lines = [
        f"# Wiki Health Report — {results['date']}",
        "",
        f"Scanned {results['total_pages']} wiki pages. "
        "Checks are purely structural (no LLM calls).",
        "",
    ]

    # ── Empty / Stub Files
    empty = results["empty_files"]
    lines.append(f"## Empty / Stub Files ({len(empty)} found)")
    lines.append("")
    if empty:
        lines.append("| Page | Total Bytes | Body Bytes | Status |")
        lines.append("|---|---|---|---|")
        for ef in empty:
            mark = "[EMPTY]" if ef["status"] == "empty" else "[STUB]"
            lines.append(f"| `{ef['path']}` | {ef['total_bytes']} | {ef['body_bytes']} | {mark} {ef['status']} |")
    else:
        lines.append("All pages have content beyond frontmatter.")
    lines.append("")

    # ── Index Sync
    isync = results["index_sync"]
    stale = isync["in_index_not_on_disk"]
    missing = isync["on_disk_not_in_index"]
    total_issues = len(stale) + len(missing)
    lines.append(f"## Index Sync ({total_issues} issues)")
    lines.append("")

    if stale:
        lines.append("### Stale Index Entries (in index.md but no file on disk)")
        for s in stale:
            lines.append(f"- `{s}`")
        lines.append("")

    if missing:
        lines.append("### Missing from Index (file exists but not in index.md)")
        for m in missing:
            lines.append(f"- `{m}`")
        lines.append("")

    if not stale and not missing:
        lines.append("index.md is in sync with disk.")
        lines.append("")

    # ── Log Coverage
    log_missing = results["log_coverage"]
    lines.append(f"## Log Coverage ({len(log_missing)} source pages without log entry)")
    lines.append("")
    if log_missing:
        lines.append("These source pages have no corresponding `ingest` entry in log.md:")
        lines.append("")
        for lm in log_missing:
            lines.append(f"- `{lm['path']}` — {lm['title']}")
    else:
        lines.append("All source pages have corresponding log entries.")
    lines.append("")

    # ── Broken Wikilinks
    broken = results["broken_links"]
    lines.append(f"## Broken Wikilinks ({len(broken)} found)")
    lines.append("")
    if broken:
        lines.append("| Page | Broken Link |")
        lines.append("|---|---|")
        for b in broken:
            lines.append(f"| `{b['page']}` | `[[{b['link']}]]` |")
    else:
        lines.append("No broken wikilinks.")
    lines.append("")

    # ── Assets Broken Links
    assets_broken = results["assets_broken_links"]
    lines.append(f"## Assets Broken Links ({len(assets_broken)} found)")
    lines.append("")
    if assets_broken:
        lines.append("These Wiki pages reference image files that don't exist in Raw/Assets/:")
        lines.append("")
        lines.append("| Page | Missing Asset |")
        lines.append("|---|---|")
        for ab in assets_broken:
            lines.append(f"| `{ab['page']}` | `{ab['missing_asset']}` |")
    else:
        lines.append("All referenced Assets exist on disk.")
    lines.append("")

    # ── Raw Directory Compliance
    raw_unexpected = results["raw_compliance"]
    lines.append(f"## Raw Directory Compliance ({len(raw_unexpected)} unexpected directories)")
    lines.append("")
    if raw_unexpected:
        lines.append("These subdirectories in Raw/ are outside the allowed whitelist (Sources / Thoughts / Records / Assets).")
        lines.append("Please move or remove them manually:")
        for d in raw_unexpected:
            lines.append(f"- `{d}`")
    else:
        lines.append("Raw/ directory structure is compliant.")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    init_env()
    ensure_utf8()

    parser = argparse.ArgumentParser(
        description="Structural health checks for the LLM Wiki (deterministic, no LLM calls)"
    )
    parser.add_argument("--save", action="store_true",
                        help="Save report to wiki/health-report.md")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON instead of markdown")
    args = parser.parse_args()

    results = run_health()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report = format_report(results)
        print(report)

        if args.save:
            report_path = WIKI_DIR / "health-report.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"\nSaved: {report_path.relative_to(REPO_ROOT)}")
