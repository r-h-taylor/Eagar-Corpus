#!/usr/bin/env python3
"""
fix_belmar.py — bulk corpus fix for Simone Belmar name variants.

The YouTube auto-captioner consistently mistranscribed "Belmar" as
various surnames-that-sound-similar (Belmare, Belmares, Belmire,
Belmore, Bellemare, Belmonte, Bell Mars). The Layer 2/3 reconstruction
sometimes caught these with bracketed alternatives (e.g.,
`Belmar [Bel Mar?]`, `Bel Mars [Belmar]`) and sometimes propagated them
silently as the primary reading.

This script standardizes everything to the canonical "Belmar" spelling,
and confirms "Simone" as the first name (replacing the lone "Simo Belmar"
in u0VksY_PRps).

Replacements, in priority order (most specific first):
  - "Simo Belmar"  →  "Simone Belmar"          (first-name correction)
  - "Belmar [Bel Mar?]"  →  "Belmar"           (resolved bracketed)
  - "Belmar [Belmonte]"  →  "Belmar"
  - "Belmar [Belmore]"   →  "Belmar"
  - "Belmar [Bellemare]" →  "Belmar"
  - "Belmar [Bel-Mar]"   →  "Belmar"
  - "Bel Mars [Belmar]"  →  "Belmar"
  - "Belmare"   →  "Belmar"                    (bare mishearings)
  - "Belmares"  →  "Belmar"
  - "Belmire"   →  "Belmar"
  - "Belmore"   →  "Belmar"
  - "Bellemare" →  "Belmar"
  - "Belmonte"  →  "Belmar"                    (only when isolated — guarded)

Word-boundary protection on bare forms so we don't accidentally match
substring occurrences in unrelated content.

Idempotent. Writes .bak before each modified file.

Usage:
  python3 fix_belmar.py --dry-run
  python3 fix_belmar.py
"""

import argparse
import re
import sys
from pathlib import Path

LECTURES_DIR = Path("output/v1/lectures")

FILES_TO_CHECK = [
    "layer2.md",
    "layer3.md",
    "case_index.md",
    "editorial_register.md",
    "extended_case_references.md",
]

# Bracketed-resolution patterns (literal string replacements; idempotent)
BRACKETED = [
    ("Belmar [Bel Mar?]",   "Belmar"),
    ("Belmar [Bel-Mar]",    "Belmar"),
    ("Belmar [Belmonte]",   "Belmar"),
    ("Belmar [Belmore]",    "Belmar"),
    ("Belmar [Bellemare]",  "Belmar"),
    ("Bel Mars [Belmar]",   "Belmar"),
]

# Bare-form patterns (regex, word-boundary protected)
BARE_PATTERNS = [
    (re.compile(r'\bSimo Belmar\b'),  "Simone Belmar"),
    (re.compile(r'\bBelmare\b'),      "Belmar"),
    (re.compile(r'\bBelmares\b'),     "Belmar"),
    (re.compile(r'\bBelmire\b'),      "Belmar"),
    (re.compile(r'\bBelmore\b'),      "Belmar"),
    (re.compile(r'\bBellemare\b'),    "Belmar"),
    # "Belmonte" only when paired with Dr. or Simone context — safer not to
    # auto-replace bare "Belmonte" since it is a real surname; but in our
    # corpus the only Belmonte occurrences are in the bracketed forms above,
    # which were already handled. Leaving bare Belmonte alone defensively.
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not LECTURES_DIR.exists():
        print(f"ERROR: {LECTURES_DIR} not found")
        sys.exit(1)

    total_replacements = 0
    files_changed = []

    for lec_dir in sorted(LECTURES_DIR.iterdir()):
        if not lec_dir.is_dir():
            continue
        for fname in FILES_TO_CHECK:
            fpath = lec_dir / fname
            if not fpath.exists():
                continue

            text = fpath.read_text(encoding="utf-8")
            original = text
            file_replacements = 0
            change_summary = []

            # Bracketed resolutions
            for old, new in BRACKETED:
                n = text.count(old)
                if n > 0:
                    text = text.replace(old, new)
                    file_replacements += n
                    change_summary.append(f"  '{old[:40]}...' x{n}" if len(old) > 40 else f"  '{old}' x{n}")

            # Bare-form regex
            for pat, repl in BARE_PATTERNS:
                matches = pat.findall(text)
                n = len(matches)
                if n > 0:
                    text = pat.sub(repl, text)
                    file_replacements += n
                    change_summary.append(f"  /{pat.pattern}/ x{n}")

            if file_replacements > 0:
                files_changed.append((fpath, file_replacements, change_summary))
                total_replacements += file_replacements
                if not args.dry_run:
                    Path(str(fpath) + ".bak").write_text(original, encoding="utf-8")
                    fpath.write_text(text, encoding="utf-8")

    print(f"\n=== Summary ===")
    print(f"  Files changed: {len(files_changed)}")
    print(f"  Total replacements: {total_replacements}")
    if files_changed:
        print(f"\n  Per-file breakdown (first 30 shown):")
        for fpath, n, changes in files_changed[:30]:
            print(f"    {n:>3} ×  {fpath}")
            for c in changes:
                print(f"          {c}")
        if len(files_changed) > 30:
            print(f"    ... and {len(files_changed) - 30} more files")

    if args.dry_run:
        print(f"\n[DRY RUN: no files written]")
    elif files_changed:
        print(f"\n  Backups written as <file>.bak")
        print(f"\nNext step: rebuild the site")
        print(f"  python3 site_build/build_site.py")


if __name__ == "__main__":
    main()
