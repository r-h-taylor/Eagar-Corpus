#!/usr/bin/env python3
"""
add_course_module.py — Stage 1 of the corpus_id refactor.

Adds a `course_module` field to each lecture's metadata.json. The
module is the YouTube playlist Tom uploaded the lecture under, which
is the structural unit for citation (corpus_id). It differs from
`course_canonical`, which captures subject-matter tagging that Tom's
editorial pipeline sometimes splits across a single playlist (e.g.,
his Welding Metallurgy Summer 2014 playlist has subject phases for
"Corrosion Cracking", "Welding Metallurgy proper", "Welding Quality").

Strategy:
  1. Parse `video_title` for "3.371 <playlist> - <term> [N/M]" pattern
  2. Parse `video_title` for "3.371 <playlist> [N/M]" pattern (no term)
  3. Parse `video_title` for "<playlist> - <term> [N/M]" pattern (no 3.371)
  4. For unmatched (date-only titles, plain titles, empty titles):
     fall back to `course_canonical` from metadata.json

Output mapping uses the canonical names already in COURSE_CODES so
corpus_id generation works downstream.

Idempotent. Writes .bak before overwriting each metadata.json.

Usage:
  python3 add_course_module.py --preview
  python3 add_course_module.py --apply
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


LECTURES_DIR = Path("output/v1/lectures")


# Map playlist title (as found in video_title) → canonical module name.
# Right side matches the codes in generate_corpus_ids.py COURSE_CODES.
PLAYLIST_TO_MODULE = {
    "Welding Metallurgy": "Welding Metallurgy",
    "Structural Materials Selection": "Structural Materials Selection",
    "Codes and Standards": "Codes and Standards",
    "Deformation Processing": "Deformation Processing",
    "Solid State Welding": "Solid State Welding",
    "What is Engineering": "What is Engineering",
    "Materials Processing and Casting": "Casting",  # playlist name vs canonical
    "Fusion Welding": "Fusion Welding",
    "Corrosion": "Corrosion",
    "Materials Selection and Economics": "Materials Selection and Economics",
    "Materials Selection": "Materials Selection",
    "Additive Manufacturing": "Additive Manufacturing",
    "Corrosion Cracking and More": "Corrosion Cracking and More",
    "Welding Quality": "Welding Quality",
    "How to be a Successful Engineer": "How to be a Successful Engineer",
    "Total Quality Improvement": "Total Quality Improvement",
    "Recitations": "Recitations",
}


# Regexes for video_title parsing
P_FULL = re.compile(
    r'^3\.371\s+(.+?)\s+-\s+(?:Spring|Summer|Fall)\s+\d{4}(?:\s+\[\d+/\d+\])?$'
)
P_FULL_NOTERM = re.compile(
    r'^3\.371\s+(.+?)(?:\s+\[\d+/\d+\])?$'
)
P_NOPREFIX = re.compile(
    r'^(.+?)\s+-\s+(?:Spring|Summer|Fall)\s+\d{4}(?:\s+\[\d+/\d+\])?$'
)

# Date-only title detection (e.g., "2018-09-05" or "2017 09 26")
P_DATE_ONLY = re.compile(r'^\d{4}[-_ ]\d{2}[-_ ]\d{2}$')


def parse_module_from_title(video_title: str) -> str | None:
    """Try to extract a playlist module name from the video_title.
    Returns the canonical module name or None if unparseable."""
    if not video_title:
        return None
    t = video_title.strip()

    # Date-only titles are explicitly not parseable
    if P_DATE_ONLY.match(t):
        return None

    # Try patterns in order
    for pattern in (P_FULL, P_FULL_NOTERM, P_NOPREFIX):
        m = pattern.match(t)
        if m:
            raw = m.group(1).strip()
            # Canonicalize via the playlist map
            if raw in PLAYLIST_TO_MODULE:
                return PLAYLIST_TO_MODULE[raw]
            # If it's exactly one of our canonical module names, accept it
            if raw in PLAYLIST_TO_MODULE.values():
                return raw
            # Otherwise leave it for fallback
            return None

    return None


def derive_module_for_lecture(meta: dict) -> tuple[str | None, str]:
    """Returns (module_name, source_of_decision)."""
    vt = meta.get("video_title") or ""

    # Strategy 1: parse video_title
    module = parse_module_from_title(vt)
    if module is not None:
        return module, "video_title"

    # Strategy 2: fall back to course_canonical (the existing subject-based field)
    cc = meta.get("course_canonical")
    if cc and cc in PLAYLIST_TO_MODULE.values():
        return cc, "course_canonical_fallback"

    # Strategy 3: fall back to raw course
    co = meta.get("course")
    if isinstance(co, list):
        co = co[0] if co else None
    if co and co in PLAYLIST_TO_MODULE.values():
        return co, "course_fallback"

    return None, "UNRESOLVED"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.preview and not args.apply:
        print("ERROR: must specify --preview or --apply")
        sys.exit(1)

    decisions = []
    for meta_path in sorted(LECTURES_DIR.glob("*/metadata.json")):
        vid = meta_path.parent.name
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        module, source = derive_module_for_lecture(meta)
        decisions.append({
            "video_id": vid,
            "video_title": meta.get("video_title") or "",
            "course": meta.get("course"),
            "course_canonical": meta.get("course_canonical"),
            "course_module": module,
            "source": source,
            "meta_path": meta_path,
            "existing_course_module": meta.get("course_module"),
        })

    # Summary
    total = len(decisions)
    by_module = Counter(d["course_module"] for d in decisions)
    by_source = Counter(d["source"] for d in decisions)

    print(f"=== Summary ===")
    print(f"  Total lectures: {total}")
    print()
    print(f"By module:")
    for mod, n in sorted(by_module.items(), key=lambda x: (x[0] is None, -x[1])):
        print(f"  {n:>3}  {mod or '(UNRESOLVED)'}")
    print()
    print(f"By source of decision:")
    for src, n in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {n:>3}  {src}")

    # Show unresolved
    unresolved = [d for d in decisions if d["course_module"] is None]
    if unresolved:
        print(f"\nUNRESOLVED lectures ({len(unresolved)}):")
        for d in unresolved[:20]:
            print(f"  {d['video_id']:15s}  title={d['video_title']!r:50s}  cc={d['course_canonical']!r}")

    if args.preview:
        print(f"\n[PREVIEW: no files written]")
        return

    # Apply
    n_written = 0
    n_skipped = 0
    for d in decisions:
        if d["course_module"] is None:
            n_skipped += 1
            continue
        if d["existing_course_module"] == d["course_module"]:
            continue  # idempotent
        meta_path = d["meta_path"]
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        Path(str(meta_path) + ".bak").write_text(
            meta_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        m["course_module"] = d["course_module"]
        meta_path.write_text(json.dumps(m, indent=2), encoding="utf-8")
        n_written += 1

    print(f"\n=== Applied ===")
    print(f"  metadata.json files updated: {n_written}")
    if n_skipped:
        print(f"  Unresolved (skipped): {n_skipped}")
    print(f"\n  Backups at <metadata.json>.bak alongside each modified file.")


if __name__ == "__main__":
    main()
