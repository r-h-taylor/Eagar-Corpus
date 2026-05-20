#!/usr/bin/env python3
"""
fix_chunked_lecture_metadata.py — restore identifier metadata for the
two chunked-and-stitched lectures whose metadata was lost during stitching.

What this script DOES restore:
  - course (string, not list)
  - course_number, course_title (split components)
  - course_canonical (matches the canonicalization rule for Casting)
  - term
  - video_title
  - lecture_number_in_series, lecture_total_in_series

What this script does NOT touch:
  - cases_mentioned, topics_covered, people_mentioned, notes (require
    re-running the Layer 2/3 analysis pass; flagged for editor)
  - provenance fields (raw_transcript_sha256, line count, etc.) — already
    correctly populated by the chunk-stitch pipeline
  - pipeline metadata (pipeline_version, model, generated_at)

Source-derived values:
  TOum2TQZu_M  ←  06__3.371_Materials_Processing_and_Casting_-_Summer_2011__6_7__TOum2TQZu_M.txt
  WhWf_cgsv0I  ←  03__3.371_Materials_Processing_and_Casting_-_Summer_2011__3_7__WhWf_cgsv0I.txt

Idempotent. Writes .bak before overwriting.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import date


LECTURES_DIR = Path("output/v1/lectures")


FIXES = {
    "TOum2TQZu_M": {
        "course": "Casting",
        "course_number": "3.371",
        "course_title": "Materials Processing and Casting",
        "course_canonical": "Casting",
        "term": "Summer 2011",
        "video_title": "3.371 Materials Processing and Casting - Summer 2011 [6/7]",
        "lecture_number_in_series": 6,
        "lecture_total_in_series": 7,
    },
    "WhWf_cgsv0I": {
        "course": "Casting",
        "course_number": "3.371",
        "course_title": "Materials Processing and Casting",
        "course_canonical": "Casting",
        "term": "Summer 2011",
        "video_title": "3.371 Materials Processing and Casting - Summer 2011 [3/7]",
        "lecture_number_in_series": 3,
        "lecture_total_in_series": 7,
    },
}


FLAG_NOTE = (
    f"{date.today().isoformat()}: identifier metadata reconstructed manually "
    "after chunk-stitch pipeline left these fields empty. The following "
    "topical fields are still missing and require re-extraction from the "
    "stitched Layer 2/3 content: topics_covered, people_mentioned, notes, "
    "lecture_open, lecture_close."
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed_count = 0
    for vid, fixes in FIXES.items():
        p = LECTURES_DIR / vid / "metadata.json"
        if not p.exists():
            print(f"  ERROR: {p} not found")
            continue

        m = json.loads(p.read_text(encoding="utf-8"))
        new_m = dict(m)
        changes_in_this_file = []

        for key, target in fixes.items():
            existing = m.get(key)
            is_missing = (
                existing is None
                or existing == []
                or existing == ""
                or (isinstance(existing, list) and len(existing) == 0)
            )
            if is_missing:
                new_m[key] = target
                changes_in_this_file.append(f"{key}: {existing!r} → {target!r}")
            elif existing != target:
                changes_in_this_file.append(
                    f"{key}: KEEPING existing {existing!r} (proposed {target!r})"
                )

        existing_flags = new_m.get("flags_for_editor", [])
        if isinstance(existing_flags, list):
            already_noted = any(
                "identifier metadata reconstructed manually" in str(f)
                for f in existing_flags
            )
            if not already_noted and changes_in_this_file:
                new_m["flags_for_editor"] = existing_flags + [FLAG_NOTE]
                changes_in_this_file.append("flags_for_editor: appended reconstruction note")

        print(f"\n=== {vid} ===")
        if not changes_in_this_file:
            print("  No changes needed (already populated).")
            continue
        for c in changes_in_this_file:
            print(f"  {c}")

        if not args.dry_run:
            backup = Path(str(p) + ".bak")
            backup.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            p.write_text(json.dumps(new_m, indent=2), encoding="utf-8")
            changed_count += 1
            print(f"  → wrote {p}")
            print(f"  → backup at {backup}")

    if args.dry_run:
        print(f"\n[DRY RUN: no files written]")
    else:
        print(f"\n{changed_count} metadata file(s) updated.")
        print(f"\nNote: the following fields still need re-extraction for these "
              f"two lectures (topics, people, notes, lecture open/close). "
              f"Flagged in flags_for_editor.")
        print(f"\nNext: python3 site_build/build_site.py")


if __name__ == "__main__":
    main()
