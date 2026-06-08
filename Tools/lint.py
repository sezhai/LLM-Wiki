#!/usr/bin/env python3
from __future__ import annotations

"""
Lint the LLM Wiki for health issues.

Usage:
    python tools/lint.py
    python tools/lint.py --save          # save lint report to wiki/lint-report.md

Checks:
  - Orphan pages (no inbound wikilinks from other pages)
  - Broken wikilinks (pointing to pages that don't exist)
  - Missing entity pages (entities mentioned in 3+ pages but no page)
  - Contradictions between pages
  - Data gaps and suggested new sources
"""

import re
import sys
import json
import argparse
import statistics
from pathlib import Path
from collections import defaultdict

from datetime import date

import os

from common import (
    REPO_ROOT, WIKI_DIR, LOG_FILE, GRAPH_DIR,
    read_file, call_llm, extract_wikilinks, all_wiki_pages,
    resolve_wikilink, load_allowed_raw_dirs,
    append_log, ensure_utf8, init_env,
)

GRAPH_JSON = GRAPH_DIR / "graph.json"
SCHEMA_FILE = REPO_ROOT / "AGENTS.md"




def find_orphans(pages: list[Path]) -> list[Path]:
    inbound = defaultdict(int)
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            for r in resolve_wikilink(link):
                inbound[r] += 1
    return [p for p in pages if inbound[p] == 0 and p != WIKI_DIR / "overview.md"]


def find_broken_links(pages: list[Path]) -> list[tuple[Path, str]]:
    broken = []
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            # Raw/ provenance markers handled inside resolve_wikilink (returns [])
            # but we skip them here explicitly to avoid adding them to "broken" list
            if link.startswith("Raw/") or link.startswith("raw/"):
                continue
            if not resolve_wikilink(link):
                broken.append((p, link))
    return broken


def find_missing_entities(pages: list[Path]) -> list[str]:
    """Find entity-like names mentioned in 3+ pages but lacking their own page."""
    mention_counts: dict[str, int] = defaultdict(int)
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            # Skip Raw/ provenance markers
            if link.startswith("Raw/") or link.startswith("raw/"):
                continue
            if not resolve_wikilink(link):
                mention_counts[link] += 1
    return [name for name, count in mention_counts.items() if count >= 3]


def check_link_density(pages: list[Path], min_outbound: int = 2) -> list[dict]:
    """Find pages with fewer than min_outbound outgoing wikilinks.

    Pages without enough outgoing connections contribute to wiki fragmentation.
    Excludes overview.md (which is a synthesis page with different linking patterns).
    Excludes Raw/ provenance markers (not navigable wiki pages).
    """
    results = []
    for p in pages:
        if p.name == "overview.md":
            continue
        content = read_file(p)
        links = extract_wikilinks(content)
        # Filter out Raw/ provenance markers
        internal_links = [
            l for l in links
            if not l.lower().startswith("raw/")
        ]
        # Deduplicate links per page
        unique_links = set(link.lower() for link in internal_links)
        if len(unique_links) < min_outbound:
            results.append({
                "path": str(p.relative_to(REPO_ROOT)),
                "outbound_links": len(unique_links),
                "links": sorted(unique_links),
            })
    results.sort(key=lambda x: x["outbound_links"])
    return results


# ── Slug collision check ────────────────────────────────────────────

def check_slug_collisions() -> list[dict]:
    """Detect slug collisions: same slug recorded for different source files.

    Reads all `slug:` fields from log.md. A collision means two different
    Raw/ files were assigned the same kebab-case filename, which would cause
    one Wiki/sources/ page to silently overwrite the other.

    Returns list of dicts with keys: slug, paths (list of raw paths that share it).
    """
    log_content = read_file(LOG_FILE)
    if not log_content:
        return []

    # slug -> list of raw paths that produced it
    slug_to_paths: dict[str, list[str]] = defaultdict(list)
    for line in log_content.splitlines():
        if "slug:" not in line or "ingest" not in line:
            continue
        m_slug = re.search(r'slug:([A-Za-z0-9][A-Za-z0-9-]*)', line)
        m_path = re.search(r'\[\[(Raw/[^\]]+)\]\]', line)
        if not m_slug or not m_path:
            continue
        slug = m_slug.group(1)
        raw_path = m_path.group(1).strip()
        if raw_path not in slug_to_paths[slug]:
            slug_to_paths[slug].append(raw_path)

    return [
        {"slug": slug, "paths": paths}
        for slug, paths in sorted(slug_to_paths.items())
        if len(paths) > 1
    ]


# ── Annotation coverage check ──────────────────────────────────────

# Annotation markers expected per Raw/ source type
_ANNOTATION_MAP = {
    "sources":  "（据文献）",
    "thoughts": "（个人思考）",
    "records":  "（个人经验）",
}


def _get_source_type_from_log(slug: str) -> str | None:
    """Look up the Raw/ subdirectory for a given slug from log.md entries.

    Returns e.g. 'sources', 'thoughts', 'records', or None if not found.
    """
    log_content = read_file(LOG_FILE)
    for line in log_content.splitlines():
        if f"slug:{slug}" not in line:
            continue
        m = re.search(r'\[\[Raw/([^/\]]+)/', line)
        if m:
            return m.group(1).lower()
    return None


def check_annotation_coverage(pages: list[Path]) -> list[dict]:
    """Find Wiki/sources/ pages that lack the expected annotation marker in their body.

    Only checks pages in Wiki/sources/ because those are the direct 1-to-1 mappings
    of Raw/ files. Concept/entity pages may legitimately mix content from multiple
    sources and are harder to audit deterministically.

    Returns list of dicts with: path, slug, expected_annotation, found.
    """
    sources_dir = WIKI_DIR / "sources"
    if not sources_dir.exists():
        return []

    results = []
    for p in sorted(sources_dir.glob("*.md")):
        slug = p.stem
        source_type = _get_source_type_from_log(slug)
        if source_type is None:
            continue  # not in log yet — not our problem here
        expected = _ANNOTATION_MAP.get(source_type)
        if expected is None:
            continue  # Assets or unknown type — skip

        content = read_file(p)
        # Strip YAML frontmatter before scanning
        body = re.sub(r'^---\n.*?\n---\n?', '', content, flags=re.DOTALL)
        if expected not in body:
            results.append({
                "path": str(p.relative_to(REPO_ROOT)),
                "slug": slug,
                "source_type": source_type,
                "expected_annotation": expected,
                "found": False,
            })

    return results

def load_graph_data() -> dict | None:
    """Load graph.json if it exists. Returns None if missing (graceful degradation)."""
    if not GRAPH_JSON.exists():
        return None
    try:
        return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        print("  [warn] graph.json is corrupted — skipping graph-aware checks")
        return None


def _build_degree_map(graph_data: dict) -> dict[str, int]:
    """Build node_id -> degree mapping from graph edges (extracted + inferred)."""
    degrees: dict[str, int] = {}
    for node in graph_data.get("nodes", []):
        degrees[node["id"]] = 0
    all_edges = graph_data.get("edges", []) + graph_data.get("inferred_edges", [])
    for edge in all_edges:
        degrees[edge["from"]] = degrees.get(edge["from"], 0) + 1
        degrees[edge["to"]] = degrees.get(edge["to"], 0) + 1
    return degrees


def _build_community_map(graph_data: dict) -> dict[str, int]:
    """Build node_id -> community_id mapping from graph nodes."""
    return {
        node["id"]: node.get("group", -1)
        for node in graph_data.get("nodes", [])
    }


def check_hub_stubs(graph_data: dict, pages: list[Path], min_content_chars: int = 500) -> list[dict]:
    """Find god nodes (degree > μ+2σ) with suspiciously short content."""
    degrees = _build_degree_map(graph_data)
    deg_values = list(degrees.values())
    if len(deg_values) < 2:
        return []

    mean_deg = statistics.mean(deg_values)
    std_deg = statistics.stdev(deg_values)
    threshold = mean_deg + 2 * std_deg

    # Map node_id -> page path
    node_to_path: dict[str, Path] = {}
    for p in pages:
        nid = p.relative_to(WIKI_DIR).as_posix().replace(".md", "")
        node_to_path[nid] = p

    results = []
    for node_id, deg in degrees.items():
        if deg <= threshold:
            continue
        path = node_to_path.get(node_id)
        if not path:
            continue
        content_len = len(read_file(path))
        if content_len < min_content_chars:
            results.append({
                "node_id": node_id,
                "degree": deg,
                "content_len": content_len,
                "path": str(path.relative_to(REPO_ROOT)),
            })
    return sorted(results, key=lambda x: x["degree"], reverse=True)


def check_fragile_bridges(graph_data: dict) -> list[dict]:
    """Find community pairs connected by only 1 edge (extracted or inferred)."""
    comm_map = _build_community_map(graph_data)
    cross_comm: dict[tuple[int, int], list[dict]] = {}

    all_edges = graph_data.get("edges", []) + graph_data.get("inferred_edges", [])
    for edge in all_edges:
        ca = comm_map.get(edge["from"], -1)
        cb = comm_map.get(edge["to"], -1)
        if ca < 0 or cb < 0 or ca == cb:
            continue
        key = (min(ca, cb), max(ca, cb))
        cross_comm.setdefault(key, []).append(edge)

    return [
        {
            "comm_a": pair[0],
            "comm_b": pair[1],
            "bridge_from": edges[0]["from"],
            "bridge_to": edges[0]["to"],
        }
        for pair, edges in sorted(cross_comm.items())
        if len(edges) == 1
    ]


def check_isolated_communities(graph_data: dict) -> list[dict]:
    """Find communities with zero external edges (knowledge silos)."""
    comm_map = _build_community_map(graph_data)

    # Build community -> members
    comm_members: dict[int, list[str]] = {}
    for node_id, comm_id in comm_map.items():
        if comm_id < 0:
            continue
        comm_members.setdefault(comm_id, []).append(node_id)

    # Track which communities have external edges (extracted + inferred)
    has_external = set()
    all_edges = graph_data.get("edges", []) + graph_data.get("inferred_edges", [])
    for edge in all_edges:
        ca = comm_map.get(edge["from"], -1)
        cb = comm_map.get(edge["to"], -1)
        if ca >= 0 and cb >= 0 and ca != cb:
            has_external.add(ca)
            has_external.add(cb)

    results = []
    for comm_id, members in sorted(comm_members.items()):
        if len(members) < 2:  # skip single-node "communities"
            continue
        if comm_id not in has_external:
            results.append({
                "community_id": comm_id,
                "node_count": len(members),
                "members": members[:10],  # cap display
            })
    return results


def run_lint():
    pages = all_wiki_pages()
    today = date.today().isoformat()

    if not pages:
        print("Wiki is empty. Nothing to lint.")
        return None

    print(f"Linting {len(pages)} wiki pages...")

    # Deterministic checks
    orphans = find_orphans(pages)
    broken = find_broken_links(pages)
    missing_entities = find_missing_entities(pages)

    print(f"  orphans: {len(orphans)}")
    print(f"  broken links: {len(broken)}")
    print(f"  missing entity pages: {len(missing_entities)}")

    # Link density check
    sparse_pages = check_link_density(pages)
    print(f"  sparse pages (< 2 outbound links): {len(sparse_pages)}")

    # Slug collision check (deterministic, reads log.md)
    slug_collisions = check_slug_collisions()
    print(f"  slug collisions: {len(slug_collisions)}")

    # Annotation coverage check (deterministic, reads page frontmatter + body)
    annotation_gaps = check_annotation_coverage(pages)
    print(f"  annotation gaps: {len(annotation_gaps)}")

    # ── Graph-aware checks ──
    graph_data = load_graph_data()
    hub_stubs: list[dict] = []
    fragile_bridges: list[dict] = []
    isolated_comms: list[dict] = []

    if graph_data and graph_data.get("nodes") and graph_data.get("edges"):
        print("  running graph-aware checks...")
        hub_stubs = check_hub_stubs(graph_data, pages)
        fragile_bridges = check_fragile_bridges(graph_data)
        isolated_comms = check_isolated_communities(graph_data)
        print(f"    hub stubs: {len(hub_stubs)}")
        print(f"    fragile bridges: {len(fragile_bridges)}")
        print(f"    isolated communities: {len(isolated_comms)}")
    elif graph_data:
        print("  [skip] graph.json has no data — skipping graph-aware checks")
    else:
        print("  [skip] no graph.json — run build_graph.py first for graph-aware checks")

    # Build context for semantic checks (contradictions, gaps)
    # Use a sample of pages to stay within context limits
    sample = pages[:20]
    pages_context = ""
    for p in sample:
        rel = p.relative_to(REPO_ROOT)
        pages_context += f"\n\n### {rel}\n{read_file(p)[:1500]}"  # truncate long pages

    print("  running semantic lint via API...")
    prompt = f"""You are linting an LLM Wiki. Review the pages below and identify:
1. Contradictions between pages (claims that conflict)
2. Stale content (summaries that newer sources have superseded)
3. Data gaps (important questions the wiki can't answer — suggest specific sources to find)
4. Concepts mentioned but lacking depth

Wiki pages (sample of {len(sample)} pages):
{pages_context}

Return a markdown lint report with these sections:
## Contradictions
## Stale Content
## Data Gaps & Suggested Sources
## Concepts Needing More Depth

Be specific — name the exact pages and claims involved.
"""
    semantic_report = call_llm(prompt, "LLM_MODEL", "claude-3-5-sonnet-latest", max_tokens=3000, exit_on_error=False)
    ctx_path = WIKI_DIR / "_semantic_lint_context.md"
    if not semantic_report.strip() or semantic_report.startswith("> API call failed") or semantic_report.startswith("> Semantic lint skipped"):
        # Dump context for agent to analyze manually
        ctx_content = f"""---
title: Semantic Lint Context
type: internal
last_updated: {today}
---

# Semantic Lint Context

This file is auto-generated by `lint.py` when no LLM API is available.
The Agent should read this file and perform the semantic analysis below.

## Instructions

Review the sampled pages and produce a markdown report with these sections:
1. **Contradictions** — claims that conflict between pages
2. **Stale Content** — summaries superseded by newer sources
3. **Data Gaps** — important questions the wiki cannot answer
4. **Concepts Needing Depth** — mentioned but thinly covered

Write your findings to `Wiki/lint-report.md` under `## Semantic Lint — Manual Audit`.

---
## Sampled Pages ({len(sample)} of {len(pages)} total)
{pages_context}
"""
        ctx_path.write_text(ctx_content, encoding="utf-8")
        print(f"  [agent] API unavailable — context dumped to {ctx_path.relative_to(REPO_ROOT)}")
        print(f"  [agent] Read that file and run the semantic analysis yourself.")
        semantic_report = f"""## Semantic Lint — Manual Agent Review Required

> Semantic lint context saved to `Wiki/_semantic_lint_context.md` ({len(sample)} pages sampled).
> Read that file and run the semantic analysis manually per AGENTS.md §八."""
    else:
        # LLM succeeded — clean up temp file if it exists from a previous failed run
        if ctx_path.exists():
            ctx_path.unlink()
            print(f"  cleaned: removed stale {ctx_path.name}")

    # Compose full report
    report_lines = [
        f"# Wiki Lint Report — {today}",
        "",
        f"Scanned {len(pages)} pages.",
        "",
        "## Structural Issues",
        "",
    ]

    if orphans:
        report_lines.append("### Orphan Pages (no inbound links)")
        for p in orphans:
            report_lines.append(f"- `{p.relative_to(REPO_ROOT)}`")
        report_lines.append("")

    if broken:
        report_lines.append("### Broken Wikilinks")
        for page, link in broken:
            report_lines.append(f"- `{page.relative_to(REPO_ROOT)}` links to `[[{link}]]` — not found")
        report_lines.append("")

    if missing_entities:
        report_lines.append("### Missing Entity Pages (mentioned 3+ times but no page)")
        report_lines.append("> Create these pages via `ingest` or manually in `Wiki/entities/`.")
        for name in missing_entities:
            report_lines.append(f"- `[[{name}]]`")
        report_lines.append("")

    if not orphans and not broken and not missing_entities and not sparse_pages:
        report_lines.append("No structural issues found.")
        report_lines.append("")

    if sparse_pages:
        report_lines.append(f"### Sparse Pages — Low Outbound Link Density ({len(sparse_pages)} pages)")
        report_lines.append("These pages have fewer than 2 outbound wikilinks. Add connections to prevent orphan accumulation:")
        report_lines.append("")
        report_lines.append("| Page | Outbound Links | Existing Links |")
        report_lines.append("|---|---|---|")
        for sp in sparse_pages:
            existing = ", ".join(f"`[[{l}]]`" for l in sp["links"]) if sp["links"] else "—"
            report_lines.append(f"| `{sp['path']}` | {sp['outbound_links']} | {existing} |")
        report_lines.append("")

    # ── Slug Collisions
    report_lines.append(f"## Slug Collisions ({len(slug_collisions)} found)")
    report_lines.append("")
    if slug_collisions:
        report_lines.append(
            "The same kebab-case slug was generated for multiple source files. "
            "One Wiki/sources/ page may have silently overwritten another. "
            "Rename slugs manually and re-ingest the affected files."
        )
        report_lines.append("")
        for sc in slug_collisions:
            report_lines.append(f"- **`{sc['slug']}`** — used by {len(sc['paths'])} files:")
            for rp in sc["paths"]:
                report_lines.append(f"  - `{rp}`")
        report_lines.append("")
    else:
        report_lines.append("No slug collisions detected.")
        report_lines.append("")

    # ── Annotation Coverage
    report_lines.append(f"## Annotation Coverage ({len(annotation_gaps)} pages missing expected annotation)")
    report_lines.append("")
    if annotation_gaps:
        report_lines.append(
            "These Wiki/sources/ pages do not contain the expected annotation marker "
            "for their source type. This suggests the LLM failed to apply annotations "
            "during ingest — review and add them manually."
        )
        report_lines.append("")
        report_lines.append("| Page | Source Type | Missing Annotation |")
        report_lines.append("|---|---|---|")
        for ag in annotation_gaps:
            report_lines.append(
                f"| `{ag['path']}` | `{ag['source_type']}` | `{ag['expected_annotation']}` |"
            )
        report_lines.append("")
    else:
        report_lines.append("All source pages contain the expected annotation markers.")
        report_lines.append("")

    # ── Graph-Aware Issues section ──
    report_lines.append("## Graph-Aware Issues")
    report_lines.append("")

    if not graph_data:
        report_lines.append("> [!tip]")
        report_lines.append("> Graph-aware checks were skipped. Run `python tools/build_graph.py` first, then re-run lint.")
        report_lines.append("")
    elif not graph_data.get("nodes") or not graph_data.get("edges"):
        report_lines.append("> [!tip]")
        report_lines.append("> Graph data is empty. Ingest sources and run `python tools/build_graph.py` to populate.")
        report_lines.append("")
    else:
        # Hub stubs
        report_lines.append(f"### Hub Pages with Insufficient Content ({len(hub_stubs)} pages)")
        if hub_stubs:
            report_lines.append("These hub nodes carry disproportionate connectivity but have thin content:")
            report_lines.append("")
            report_lines.append("| Page | Degree | Content Length | Status |")
            report_lines.append("|---|---|---|---|")
            for hs in hub_stubs:
                status = "🔴 stub" if hs["content_len"] < 250 else "🟡 thin"
                report_lines.append(f"| `{hs['path']}` | {hs['degree']} | {hs['content_len']} chars | {status} |")
        else:
            report_lines.append("No hub stubs detected — all high-degree nodes have sufficient content.")
        report_lines.append("")

        # Fragile bridges
        report_lines.append(f"### Fragile Bridges ({len(fragile_bridges)} community pairs)")
        if fragile_bridges:
            report_lines.append("These community connections rely on a single edge — one broken link isolates them:")
            for fb in fragile_bridges:
                report_lines.append(f"- Community {fb['comm_a']} ↔ Community {fb['comm_b']} via `{fb['bridge_from']}` → `{fb['bridge_to']}`")
        else:
            report_lines.append("No fragile bridges — all community connections have redundant links.")
        report_lines.append("")

        # Isolated communities
        report_lines.append(f"### Isolated Communities ({len(isolated_comms)} communities)")
        if isolated_comms:
            report_lines.append("These communities have zero external connections — knowledge silos:")
            report_lines.append("")
            report_lines.append("| Community | Nodes | Members |")
            report_lines.append("|---|---|---|")
            for ic in isolated_comms:
                members_str = ", ".join(ic["members"][:5])
                if ic["node_count"] > 5:
                    members_str += ", …"
                report_lines.append(f"| {ic['community_id']} | {ic['node_count']} | {members_str} |")
        else:
            report_lines.append("No isolated communities — all clusters have external connections.")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append(semantic_report)

    report = "\n".join(report_lines)
    print("\n" + report)
    return report, {
        "orphans": orphans,
        "broken": broken,
        "missing_entities": missing_entities,
        "slug_collisions": slug_collisions,
    }


# append_log imported from common


if __name__ == "__main__":
    init_env()
    ensure_utf8()

    parser = argparse.ArgumentParser(description="Lint the LLM Wiki")
    parser.add_argument("--save", action="store_true", help="Save lint report to wiki/lint-report.md")
    args = parser.parse_args()

    result = run_lint()
    if not result:
        sys.exit(0)
    report, issues = result

    if args.save and report:
        report_path = WIKI_DIR / "lint-report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\nSaved: {report_path.relative_to(REPO_ROOT)}")

    today = date.today().isoformat()
    append_log(f"## [{today}] lint | Wiki health check\n\nRan lint. See lint-report.md for details.")

    # Exit 1 if serious structural issues found (broken links, orphans, slug collisions, missing entities)
    serious = (
        bool(issues.get("broken"))
        or bool(issues.get("orphans"))
        or bool(issues.get("slug_collisions"))
        or bool(issues.get("missing_entities"))
    )
    sys.exit(1 if serious else 0)
