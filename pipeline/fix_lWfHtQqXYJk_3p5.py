#!/usr/bin/env python3
"""
fix_lWfHtQqXYJk_3p5.py — surgical correction to Layer 3 §3.p5 in
lWfHtQqXYJk.

Background: the YouTube auto-caption at 18:47-19:01 reads
  "version and when life one of them was in a 1948 seaplane he operated
   about four or five years ago Miami crash my apartment"
First-pass Layer 2/3 reconstruction rendered the closing clause as
"off Miami, crashed near my apartment", introducing a biographical
detail (Tom owning a Miami apartment) that doesn't match the speaker's
known biography. Audio re-listen + external identification (Chalk's
Ocean Airways Flight 101) confirm Tom said "crashed in Miami harbor".

This script makes the minimal Layer 3 edit. Companion scholarly
annotations (identification, date refinement) live in
output/v1/lectures/lWfHtQqXYJk/layer4.md, not here — those are Layer 4
work. This is editorial correction work.

Idempotent: re-running after a successful first run is a no-op (the
old sentence won't be found, the script will say so).

Usage:
  python3 fix_lWfHtQqXYJk_3p5.py --dry-run   # show diff, don't write
  python3 fix_lWfHtQqXYJk_3p5.py             # apply
"""

import argparse
import difflib
import sys
from pathlib import Path

LECTURE_DIR = Path("output/v1/lectures/lWfHtQqXYJk")
LAYER3 = LECTURE_DIR / "layer3.md"

OLD_SENTENCE = (
    "I've only seen two cases of exfoliation corrosion in my life. "
    "One of them was a 1948 seaplane that operated about four or "
    "five years ago off Miami, crashed near my apartment."
)

NEW_SENTENCE = (
    "I've only seen two cases of exfoliation corrosion in my life. "
    "One of them was a 1948 seaplane that crashed in Miami harbor "
    "about four or five years ago — it was in the news a lot."
)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the diff, don't write")
    args = parser.parse_args()

    if not LAYER3.exists():
        print(f"ERROR: {LAYER3} not found")
        sys.exit(1)

    text = LAYER3.read_text(encoding="utf-8")

    # Idempotency check: already corrected?
    if NEW_SENTENCE in text:
        print(f"  {LAYER3} already contains the corrected sentence. No change.")
        sys.exit(0)

    # Locate the old sentence
    if OLD_SENTENCE not in text:
        print(f"ERROR: old sentence not found in {LAYER3}.")
        print(f"\nLooking for:")
        print(f"  {OLD_SENTENCE!r}")
        print(f"\nThis may mean the file has been edited differently. "
              f"Manual inspection required.")
        sys.exit(1)

    new_text = text.replace(OLD_SENTENCE, NEW_SENTENCE)

    # Show diff
    print(f"Proposed change to {LAYER3}:\n")
    diff = list(difflib.unified_diff(
        text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"{LAYER3} (current)",
        tofile=f"{LAYER3} (corrected)",
        n=2,
    ))
    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            print(f"  {line}", end="")
        elif line.startswith("@@"):
            print(f"  \033[36m{line}\033[0m", end="")  # cyan
        elif line.startswith("-"):
            print(f"  \033[31m{line}\033[0m", end="")  # red
        elif line.startswith("+"):
            print(f"  \033[32m{line}\033[0m", end="")  # green
        else:
            print(f"  {line}", end="")

    if args.dry_run:
        print("\n[DRY RUN: not writing]")
        return

    LAYER3.write_text(new_text, encoding="utf-8")
    print(f"\nWrote {LAYER3}")
    print(f"\nNext step: regenerate the site if it's been built:")
    print(f"  python3 site_build/build_site.py")


if __name__ == "__main__":
    main()
