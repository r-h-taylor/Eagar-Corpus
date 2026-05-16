#!/usr/bin/env python3
"""
stitch_chunks.py — merge per-chunk pipeline outputs into canonical
lecture-level files for a chunked lecture.

For each chunk N, reads:
  chunks/<vid>/chunk_N/{layer2.md, layer3.md, anchors.json,
                        editorial_register.md, case_index.md,
                        metadata.json, transformation_log.md}

Produces in output/v1/lectures/<vid>/:
  layer2.md          (concatenated, global section renumbering)
  layer3.md          (concatenated, title block from chunk 1 only,
                      closing from last chunk only, sections renumbered)
  anchors.json       (merged with renumbered anchors)
  editorial_register.md  (concatenated with chunk-boundary markers)
  transformation_log.md  (concatenated with chunk-boundary markers)
  case_index.md      (deduplicated by canonical_cluster_id, anchor
                      ranges merged across chunks)
  metadata.json      (synthesized from per-chunk metadata)

Usage:
    python3 stitch_chunks.py --vid WhWf_cgsv0I
    python3 stitch_chunks.py --vid WhWf_cgsv0I --dry-run

NOTE FOR EDITORIAL REVIEW: the stitcher's output is mechanical. Section
boundaries near chunk transitions, case-index frame text after dedup,
and editorial-register entries will need human review and smoothing.
Chunk-boundary markers in editorial_register.md and transformation_log.md
are intentionally visible to flag where review is most needed.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
from pathlib import Path

CHUNK_DIR = Path("chunks")
OUTPUT_DIR = Path("output/v1/lectures")

PIPELINE_VERSION = "2.0-chunked"

# Match a section header like "## §3. ..." in layer 2 or layer 3
SECTION_HEADER_RE = re.compile(r"^(##\s+)§(\d+)(\.\s)", re.MULTILINE)
# Match an inline anchor like `§3.p2` in markdown body
ANCHOR_INLINE_RE = re.compile(r"`§(\d+)\.p(\d+)`")
# Match plain anchor reference like §3.p2 (no backticks)
ANCHOR_PLAIN_RE = re.compile(r"§(\d+)\.p(\d+)")


# ---------------------------------------------------------------------------
# Section renumbering
# ---------------------------------------------------------------------------

def count_sections(text: str) -> int:
    """Count distinct section numbers appearing as ## §N. headers."""
    matches = SECTION_HEADER_RE.findall(text)
    if not matches:
        return 0
    return max(int(m[1]) for m in matches)


def renumber_sections(text: str, offset: int) -> str:
    """Add `offset` to every section number in headers and anchors."""
    if offset == 0:
        return text

    def replace_header(m: re.Match) -> str:
        prefix, num, suffix = m.group(1), int(m.group(2)), m.group(3)
        return f"{prefix}§{num + offset}{suffix}"

    text = SECTION_HEADER_RE.sub(replace_header, text)

    def replace_inline(m: re.Match) -> str:
        sec, para = int(m.group(1)), int(m.group(2))
        return f"`§{sec + offset}.p{para}`"

    text = ANCHOR_INLINE_RE.sub(replace_inline, text)

    return text


def renumber_anchors_only(text: str, offset: int) -> str:
    """Renumber `§N.pM` anchor references (both backtick and plain),
    leaving header text alone. Used for editorial_register and case_index
    contents that reference anchors but don't contain ##§N headers."""
    if offset == 0:
        return text

    def replace_inline(m: re.Match) -> str:
        sec, para = int(m.group(1)), int(m.group(2))
        return f"`§{sec + offset}.p{para}`"

    def replace_plain(m: re.Match) -> str:
        sec, para = int(m.group(1)), int(m.group(2))
        return f"§{sec + offset}.p{para}"

    text = ANCHOR_INLINE_RE.sub(replace_inline, text)
    # Plain (no backtick) anchors — be careful not to double-apply
    # by only matching where backticks are NOT present
    text = re.sub(
        r"(?<![`§\d])§(\d+)\.p(\d+)(?![\d])",
        replace_plain,
        text,
    )
    return text


# ---------------------------------------------------------------------------
# Layer 2 / Layer 3 stitching
# ---------------------------------------------------------------------------

def strip_title_block(text: str) -> str:
    """Remove the YAML front matter and/or title block from a layer 2/3 file
    so we can concatenate chunks 2+ without redundant headers.

    Strategy: drop everything up to (but not including) the first `## §`
    section header. If no such header exists, return text unchanged.
    """
    m = SECTION_HEADER_RE.search(text)
    if not m:
        return text
    return text[m.start():]


def strip_closing_section(text: str) -> str:
    """If the chunk's editorial layer ended with a closing wrap-up
    paragraph (e.g. 'see you Tuesday'), this would attempt to remove it.
    For now this is a no-op; human editorial review will handle closing
    smoothing. We keep the function as a hook for future refinement."""
    return text


def stitch_layer(chunk_paths: list[Path], layer_name: str) -> str:
    """Concatenate layer 2 or layer 3 files across chunks, applying
    global section renumbering."""
    section_offset = 0
    pieces = []

    for i, chunk_path in enumerate(chunk_paths):
        text = chunk_path.read_text(encoding="utf-8")

        if i == 0:
            # Keep chunk 1's title block intact
            chunk_text = text
        else:
            # Strip title block, keep section content
            chunk_text = strip_title_block(text)
            chunk_text = (
                f"\n\n<!-- ============================================================ -->\n"
                f"<!-- chunk {i + 1} boundary — review for smoothing -->\n"
                f"<!-- ============================================================ -->\n\n"
                + chunk_text
            )

        # Apply offset to this chunk's section numbers
        chunk_text = renumber_sections(chunk_text, section_offset)

        # Count sections in this chunk for the next offset
        chunk_section_count = count_sections(chunk_path.read_text(encoding="utf-8"))
        section_offset += chunk_section_count

        pieces.append(chunk_text)

    return "\n".join(pieces)


# ---------------------------------------------------------------------------
# Anchors.json stitching
# ---------------------------------------------------------------------------

def stitch_anchors(chunk_paths: list[Path]) -> dict:
    """Merge per-chunk anchors.json files, applying section-number offsets."""
    section_offset = 0
    merged = {}

    for i, chunk_path in enumerate(chunk_paths):
        if not chunk_path.exists():
            continue
        try:
            data = json.loads(chunk_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  WARN: chunk {i + 1} anchors.json is not valid JSON; skipping")
            continue

        # Determine this chunk's section count from its layer 3 file
        layer3_path = chunk_path.parent / "layer3.md"
        chunk_section_count = 0
        if layer3_path.exists():
            chunk_section_count = count_sections(layer3_path.read_text(encoding="utf-8"))

        # Apply offset to keys
        def offset_anchor(anchor_key: str) -> str:
            m = re.match(r"§(\d+)\.p(\d+)", anchor_key)
            if not m:
                return anchor_key
            sec, para = int(m.group(1)), int(m.group(2))
            return f"§{sec + section_offset}.p{para}"

        if isinstance(data, dict):
            for k, v in data.items():
                merged[offset_anchor(k)] = v
        elif isinstance(data, list):
            # Some anchors.json files might be a list of {anchor, ...}
            if "anchors" not in merged:
                merged["anchors"] = []
            for item in data:
                if isinstance(item, dict) and "anchor" in item:
                    item = dict(item)
                    item["anchor"] = offset_anchor(item["anchor"])
                merged["anchors"].append(item)

        section_offset += chunk_section_count

    return merged


# ---------------------------------------------------------------------------
# Editorial register / transformation log stitching
# ---------------------------------------------------------------------------

def stitch_register_or_log(chunk_paths: list[Path], file_kind: str) -> str:
    """Concatenate per-chunk editorial_register.md or transformation_log.md
    with visible chunk-boundary markers. Apply anchor renumbering to
    references within each chunk's content."""
    section_offset = 0
    pieces = []

    n = len(chunk_paths)
    for i, chunk_path in enumerate(chunk_paths):
        if not chunk_path.exists():
            continue
        text = chunk_path.read_text(encoding="utf-8")

        # Apply anchor offset to references inside
        text = renumber_anchors_only(text, section_offset)

        if i == 0:
            pieces.append(text)
        else:
            pieces.append(
                f"\n\n---\n\n"
                f"## --- {file_kind} for chunk {i + 1} of {n} (sections §{section_offset + 1}+) ---\n\n"
                f"*Chunk boundary: review for editorial-decision continuity with previous chunk.*\n\n"
                + text
            )

        # Update offset for next chunk
        layer3_path = chunk_path.parent / "layer3.md"
        if layer3_path.exists():
            section_offset += count_sections(layer3_path.read_text(encoding="utf-8"))

    return "\n".join(pieces)


# ---------------------------------------------------------------------------
# Case index stitching (deduplicate by canonical_cluster_id)
# ---------------------------------------------------------------------------

CASE_HEADING_RE = re.compile(r"^### (.+)$", re.MULTILINE)
CLUSTER_ID_RE = re.compile(r'canonical_cluster_id:\*?\*?\s*"([^"]+)"')
ANCHOR_FIELD_RE = re.compile(r'\*\*Anchor:\*\*\s*([^\n]+)')


def parse_case_entries(case_index_text: str) -> list[dict]:
    """Parse a case_index.md into a list of case entries with name,
    cluster_id, anchor, and full block text."""
    # Split by ### headings
    entries = []
    parts = re.split(r"\n(?=### )", case_index_text)
    for part in parts:
        if not part.startswith("### "):
            continue
        name_match = re.match(r"### (.+?)\n", part)
        if not name_match:
            continue
        name = name_match.group(1).strip()

        cid_match = CLUSTER_ID_RE.search(part)
        cluster_id = cid_match.group(1) if cid_match else None

        anchor_match = ANCHOR_FIELD_RE.search(part)
        anchor = anchor_match.group(1).strip() if anchor_match else None

        entries.append({
            "name": name,
            "cluster_id": cluster_id,
            "anchor": anchor,
            "text": part.strip(),
        })
    return entries


def stitch_case_index(chunk_paths: list[Path], vid: str, metadata: dict) -> str:
    """Merge per-chunk case_index files, deduplicating by canonical_cluster_id."""
    section_offset = 0
    all_entries = []  # (chunk_id, entry_dict_with_offset_applied)

    n = len(chunk_paths)
    for i, chunk_path in enumerate(chunk_paths):
        if not chunk_path.exists():
            continue
        text = chunk_path.read_text(encoding="utf-8")
        text = renumber_anchors_only(text, section_offset)

        for entry in parse_case_entries(text):
            entry["chunk_id"] = i + 1
            all_entries.append(entry)

        layer3_path = chunk_path.parent / "layer3.md"
        if layer3_path.exists():
            section_offset += count_sections(layer3_path.read_text(encoding="utf-8"))

    # Deduplicate by cluster_id, merging anchor ranges and entry text
    by_cluster = OrderedDict()
    no_cluster = []  # entries without a parseable cluster_id

    for entry in all_entries:
        cid = entry["cluster_id"]
        if cid is None:
            no_cluster.append(entry)
            continue
        if cid not in by_cluster:
            by_cluster[cid] = {
                "name": entry["name"],
                "cluster_id": cid,
                "anchors": [entry["anchor"]] if entry["anchor"] else [],
                "chunk_ids": [entry["chunk_id"]],
                "entry_texts": [entry["text"]],
            }
        else:
            if entry["anchor"]:
                by_cluster[cid]["anchors"].append(entry["anchor"])
            by_cluster[cid]["chunk_ids"].append(entry["chunk_id"])
            by_cluster[cid]["entry_texts"].append(entry["text"])

    # Render the stitched case_index.md
    course = metadata.get("course") or "unknown"
    term = metadata.get("term", "unknown")
    n_chunks = metadata.get("n_chunks", n)

    out_lines = []
    out_lines.append(f"# Case Index — Lecture {vid} ({course}, {term})")
    out_lines.append("")
    out_lines.append("*Citation format: layer 3 paragraph anchor (e.g. `§1.p3`). "
                     "Click-through reveals the corresponding layer 2 passage with timestamp range.*")
    out_lines.append("")
    out_lines.append(f"*This lecture was processed in {n_chunks} chunks due to length. "
                     f"Case entries below have been deduplicated by canonical_cluster_id "
                     f"across chunks; where the same case appears in multiple chunks, "
                     f"anchor ranges are listed together and the per-chunk frame texts "
                     f"are presented for human editorial review and consolidation.*")
    out_lines.append("")
    out_lines.append(f"## All cases referenced ({len(by_cluster)} unique canonical, "
                     f"{len(no_cluster)} unparseable)")
    out_lines.append("")

    for cid, info in by_cluster.items():
        out_lines.append(f"### {info['name']}")
        # Combined anchor field
        if info["anchors"]:
            joined = ", ".join(info["anchors"])
            out_lines.append(f"- **Anchor:** {joined}")
        out_lines.append(f"- **canonical_cluster_id:** \"{cid}\"")
        if len(info["entry_texts"]) == 1:
            # Single chunk — keep original entry body (after the heading)
            body = info["entry_texts"][0]
            # Strip the ### heading and any redundant Anchor/cluster lines from the head
            body_lines = body.split("\n", 1)[1] if "\n" in body else ""
            # Remove the redundant heading-level fields we just emitted
            body_lines = re.sub(r"^- \*\*Anchor:\*\*[^\n]*\n", "", body_lines, count=1)
            body_lines = re.sub(r"^- \*\*canonical_cluster_id:\*\*[^\n]*\n", "", body_lines, count=1)
            out_lines.append(body_lines.rstrip())
        else:
            # Multiple chunks — show each chunk's frame for human consolidation
            out_lines.append(f"- **Cross-chunk appearance:** chunks {info['chunk_ids']}")
            for j, body in enumerate(info["entry_texts"]):
                out_lines.append(f"")
                out_lines.append(f"  *From chunk {info['chunk_ids'][j]}:*")
                body_lines = body.split("\n", 1)[1] if "\n" in body else ""
                body_lines = re.sub(r"^- \*\*Anchor:\*\*[^\n]*\n", "", body_lines, count=1)
                body_lines = re.sub(r"^- \*\*canonical_cluster_id:\*\*[^\n]*\n", "", body_lines, count=1)
                # Indent for visual separation
                indented = "\n".join("  " + line if line.strip() else line for line in body_lines.split("\n"))
                out_lines.append(indented.rstrip())
            out_lines.append(f"")
            out_lines.append(f"  *[Editor: consolidate the per-chunk frames above into a single Frame in this lecture entry.]*")
        out_lines.append("")

    if no_cluster:
        out_lines.append("## Cases with unparseable cluster_id (review required)")
        out_lines.append("")
        for entry in no_cluster:
            out_lines.append(f"### {entry['name']} (from chunk {entry['chunk_id']})")
            body = entry["text"]
            body_lines = body.split("\n", 1)[1] if "\n" in body else ""
            out_lines.append(body_lines.rstrip())
            out_lines.append("")

    return "\n".join(out_lines)


# ---------------------------------------------------------------------------
# Metadata synthesis
# ---------------------------------------------------------------------------

def synthesize_metadata(vid: str, chunk_paths: list[Path], manifest: dict) -> dict:
    """Build a single metadata.json for the full lecture by summing across
    chunk metadata."""
    out = {
        "video_id": vid,
        "raw_transcript_sha256": manifest.get("raw_transcript_sha256"),
        "raw_transcript_word_count": manifest.get("raw_transcript_word_count"),
        "raw_transcript_line_count": manifest.get("raw_transcript_line_count"),
        "pipeline_version": PIPELINE_VERSION,
        "model": "claude-opus-4-7",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chunked": True,
        "n_chunks": manifest.get("n_chunks"),
        "chunk_overlap_seconds": manifest.get("overlap_seconds"),
        "chunks_summary": [],
        "layer2_paragraph_count": 0,
        "cases_mentioned": [],
        "flags_for_editor": [
            {
                "issue": ("This lecture was processed via chunk-and-stitch due to "
                          "length exceeding the pipeline's effective output ceiling. "
                          "Section boundaries near chunk transitions and case-index "
                          "frame text for cross-chunk cases require human editorial "
                          "review and consolidation."),
            }
        ],
    }

    seen_courses = set()
    seen_terms = set()
    section_offset = 0

    for i, chunk_path in enumerate(chunk_paths):
        if not chunk_path.exists():
            continue
        try:
            chunk_meta = json.loads(chunk_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        if "course" in chunk_meta:
            seen_courses.add(chunk_meta["course"])
        if "term" in chunk_meta:
            seen_terms.add(chunk_meta["term"])

        para_count = chunk_meta.get("layer2_paragraph_count", 0)
        out["layer2_paragraph_count"] += para_count

        layer3_path = chunk_path.parent / "layer3.md"
        chunk_section_count = 0
        if layer3_path.exists():
            chunk_section_count = count_sections(layer3_path.read_text(encoding="utf-8"))

        out["chunks_summary"].append({
            "chunk_id": chunk_meta.get("chunk_id", i + 1),
            "chunk_start_seconds": chunk_meta.get("chunk_start_seconds"),
            "chunk_end_seconds": chunk_meta.get("chunk_end_seconds"),
            "section_count": chunk_section_count,
            "section_range_after_renumber": [section_offset + 1, section_offset + chunk_section_count] if chunk_section_count else None,
            "raw_word_count": chunk_meta.get("chunk_raw_word_count"),
        })

        for case in chunk_meta.get("cases_mentioned", []):
            out["cases_mentioned"].append(case)

        section_offset += chunk_section_count

    out["course"] = next(iter(seen_courses)) if len(seen_courses) == 1 else list(seen_courses)
    out["term"] = next(iter(seen_terms)) if len(seen_terms) == 1 else list(seen_terms)
    out["total_section_count"] = section_offset

    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vid", required=True, help="Video ID")
    parser.add_argument("--dry-run", action="store_true", help="Don't write output files")
    args = parser.parse_args()

    chunk_root = CHUNK_DIR / args.vid
    manifest_path = chunk_root / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} not found")
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    n_chunks = manifest["n_chunks"]
    chunk_dirs = [chunk_root / f"chunk_{i}" for i in range(1, n_chunks + 1)]

    # Verify all chunks complete
    required_files = ["layer2.md", "layer3.md", "anchors.json",
                      "editorial_register.md", "case_index.md",
                      "metadata.json", "transformation_log.md"]
    print(f"\nVerifying chunks for {args.vid}:")
    incomplete = []
    for i, cd in enumerate(chunk_dirs, 1):
        missing = [f for f in required_files if not (cd / f).exists()]
        if missing:
            incomplete.append((i, missing))
            print(f"  chunk {i}: MISSING {missing}")
        else:
            print(f"  chunk {i}: complete (7/7)")
    if incomplete:
        print(f"\nERROR: {len(incomplete)} chunk(s) incomplete. Run process_chunked_lecture.py.")
        sys.exit(1)

    out_dir = OUTPUT_DIR / args.vid
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    # --- Stitch layer 2 ---
    print(f"\nStitching layer2.md...")
    layer2 = stitch_layer([cd / "layer2.md" for cd in chunk_dirs], "layer 2")
    if args.dry_run:
        print(f"  DRY: would write {len(layer2):,} chars")
    else:
        (out_dir / "layer2.md").write_text(layer2, encoding="utf-8")
        print(f"  OK ({len(layer2):,} chars)")

    # --- Stitch layer 3 ---
    print(f"Stitching layer3.md...")
    layer3 = stitch_layer([cd / "layer3.md" for cd in chunk_dirs], "layer 3")
    if args.dry_run:
        print(f"  DRY: would write {len(layer3):,} chars")
    else:
        (out_dir / "layer3.md").write_text(layer3, encoding="utf-8")
        print(f"  OK ({len(layer3):,} chars)")

    # --- Stitch anchors ---
    print(f"Stitching anchors.json...")
    anchors = stitch_anchors([cd / "anchors.json" for cd in chunk_dirs])
    if args.dry_run:
        print(f"  DRY: would write {len(json.dumps(anchors))} chars of JSON")
    else:
        (out_dir / "anchors.json").write_text(json.dumps(anchors, indent=2), encoding="utf-8")
        print(f"  OK")

    # --- Stitch editorial register ---
    print(f"Stitching editorial_register.md...")
    register = stitch_register_or_log(
        [cd / "editorial_register.md" for cd in chunk_dirs],
        file_kind="editorial register"
    )
    if args.dry_run:
        print(f"  DRY: would write {len(register):,} chars")
    else:
        (out_dir / "editorial_register.md").write_text(register, encoding="utf-8")
        print(f"  OK ({len(register):,} chars)")

    # --- Stitch transformation log ---
    print(f"Stitching transformation_log.md...")
    tlog = stitch_register_or_log(
        [cd / "transformation_log.md" for cd in chunk_dirs],
        file_kind="transformation log"
    )
    if args.dry_run:
        print(f"  DRY: would write {len(tlog):,} chars")
    else:
        (out_dir / "transformation_log.md").write_text(tlog, encoding="utf-8")
        print(f"  OK ({len(tlog):,} chars)")

    # --- Synthesize metadata ---
    print(f"Synthesizing metadata.json...")
    metadata = synthesize_metadata(
        args.vid,
        [cd / "metadata.json" for cd in chunk_dirs],
        manifest,
    )
    if args.dry_run:
        print(f"  DRY: would write metadata with {metadata.get('total_section_count')} sections")
    else:
        (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(f"  OK ({metadata.get('total_section_count')} total sections)")

    # --- Stitch case index ---
    print(f"Stitching case_index.md...")
    case_index = stitch_case_index(
        [cd / "case_index.md" for cd in chunk_dirs],
        vid=args.vid,
        metadata={
            "course": metadata.get("course"),
            "term": metadata.get("term"),
            "n_chunks": n_chunks,
        }
    )
    if args.dry_run:
        print(f"  DRY: would write {len(case_index):,} chars")
    else:
        (out_dir / "case_index.md").write_text(case_index, encoding="utf-8")
        print(f"  OK ({len(case_index):,} chars)")

    print(f"\n=== Stitched output for {args.vid} written to {out_dir} ===")
    print(f"\nNEXT: human editorial review recommended for:")
    print(f"  - chunk-boundary smoothing in layer2.md and layer3.md")
    print(f"  - cross-chunk case-index consolidation")
    print(f"  - editorial_register.md continuity between chunk boundaries")


if __name__ == "__main__":
    main()
