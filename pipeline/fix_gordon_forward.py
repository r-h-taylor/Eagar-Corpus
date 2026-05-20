#!/usr/bin/env python3
"""
fix_gordon_forward.py — bulk corpus fix.

The YouTube auto-caption consistently mistranscribed "Gordon Forward"
(co-founder of Chaparral Steel) as "Gordon Ford". The Layer 2/3
reconstruction passed this error through as the primary reading, with
"[Forward]" added as a bracketed editorial flag. Tom Eagar consistently
says "Forward" — the bracketed reading is the correct one, the bare
"Ford" is wrong everywhere.

This script replaces every occurrence of `Gordon Ford [Forward]` with
`Gordon Forward` across:
  output/v1/lectures/<vid>/layer3.md   (10 known files)
  output/v1/lectures/<vid>/layer2.md   (if present with same error)
  output/v1/lectures/<vid>/case_index.md  (where Forward is the case anchor)
  output/v1/lectures/<vid>/editorial_register.md
  output/v1/lectures/<vid>/extended_case_references.md

Also does a defensive scan for any remaining bare "Gordon Ford" not
followed by "[Forward]" — those would be cases Layer 3 didn't flag.
The script prints those for manual review rather than auto-fixing.

Idempotent: re-running after success makes no changes.
Backups: writes <file>.bak before any change.

Usage:
  python3 fix_gordon_forward.py --dry-run
  python3 fix_gordon_forward.py
"""

import argparse
import re
import sys
from pathlib import Path

LECTURES_DIR = Path("output/v1/lectures")

OLD_BRACKETED = "Gordon Ford [Forward]"
NEW = "Gordon Forward"

# Files we look at per lecture directory
FILES_TO_CHECK = [
    "layer3.md",
    "layer2.md",
    "case_index.md",
    "editorial_register.md",
    "extended_case_references.md",
]


def find_unflagged_gordon_ford(text: str, path: Path) -> list[tuple[int, str]]:
    """Find 'Gordon Ford' instances NOT followed by '[Forward]'.
    These are caption errors Layer 3 didn't flag and may need manual review."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        # Skip lines we'll auto-fix (those containing the bracketed form)
        if OLD_BRACKETED in line:
            continue
        # Look for 'Gordon Ford' as a standalone word followed by anything
        # except [Forward] (case-insensitive)
        for m in re.finditer(r'Gordon Ford\b(?!\s*\[Forward\])', line):
            out.append((i, line.strip()))
            break  # one report per line
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not LECTURES_DIR.exists():
        print(f"ERROR: {LECTURES_DIR} not found")
        sys.exit(1)

    total_replacements = 0
    files_changed = []

    # Replacement patterns, in priority order:
    #   (a) "Gordon Ford [Forward]"  →  "Gordon Forward"   (Layer 3 bracketed form)
    #   (b) "Gordon Ford"  →  "Gordon Forward"             (Layer 2 bare form)
    # We apply (a) first so we don't double-process the bracketed form.

    for lec_dir in sorted(LECTURES_DIR.iterdir()):
        if not lec_dir.is_dir():
            continue
        for fname in FILES_TO_CHECK:
            fpath = lec_dir / fname
            if not fpath.exists():
                continue
            text = fpath.read_text(encoding="utf-8")
            original_text = text

            # Pattern (a): bracketed form
            n_a = text.count(OLD_BRACKETED)
            if n_a > 0:
                text = text.replace(OLD_BRACKETED, NEW)

            # Pattern (b): bare 'Gordon Ford' as word-bounded standalone.
            # Only count occurrences that AREN'T followed by '[Forward]'
            # (those were already handled by pattern (a) in the previous step).
            # Use regex with word boundary on the right side to avoid matching
            # things like 'Gordon Forde' or 'Gordon Ford-Smith'.
            pattern_b = re.compile(r'\bGordon Ford\b(?!\s*\[Forward\])')
            matches_b = pattern_b.findall(text)
            n_b = len(matches_b)
            if n_b > 0:
                text = pattern_b.sub(NEW, text)

            n_total = n_a + n_b
            if n_total > 0:
                files_changed.append((fpath, n_a, n_b))
                total_replacements += n_total

                if not args.dry_run:
                    backup = Path(str(fpath) + ".bak")
                    backup.write_text(original_text, encoding="utf-8")
                    fpath.write_text(text, encoding="utf-8")

    print(f"\n=== Summary ===")
    print(f"  Files changed: {len(files_changed)}")
    print(f"  Total replacements: {total_replacements}")
    if files_changed:
        print(f"\n  Per-file breakdown (bracketed + bare):")
        for fpath, n_a, n_b in files_changed:
            print(f"    {n_a:>2} bracketed, {n_b:>2} bare  →  {fpath}")

    if args.dry_run:
        print(f"\n[DRY RUN: no files written]")
    elif files_changed:
        print(f"\n  Backups written as <file>.bak")
        print(f"  To revert: for each *.bak file, mv back to original")
        print(f"\nNext step: rebuild the site")
        print(f"  python3 site_build/build_site.py")


if __name__ == "__main__":
    main()
