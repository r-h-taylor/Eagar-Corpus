#!/usr/bin/env python3
"""
fix_concept_doi.py — replace incorrect Zenodo concept DOI everywhere.

The correct concept DOI (always resolves to latest version) is
  10.5281/zenodo.20226048
not
  10.5281/zenodo.20226049

The .20226049 number appears to have been propagated by mistake (it
was either the v1.0.0 specific DOI or a transcription error).

This script does a careful global string-replace in:
  - Paper/jme_manuscript.tex
  - site_build/templates/about.html  (source; rebuild propagates to site/)
  - site_build/templates/casemap.html (source if exists; otherwise
    just the rendered site/casemap.html will be overwritten on rebuild)

Files modified get a .bak backup. Idempotent.

Note: the v1.0.1 specific DOI 10.5281/zenodo.20226123 is correct and
NOT touched.
"""

import argparse
import sys
from pathlib import Path

WRONG = "20226049"
RIGHT = "20226048"

TARGETS = [
    Path("Paper/jme_manuscript.tex"),
    Path("site_build/templates/about.html"),
    Path("site_build/templates/casemap.html"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total = 0
    for p in TARGETS:
        if not p.exists():
            print(f"  {p}: not found (skipping)")
            continue
        text = p.read_text(encoding="utf-8")
        n = text.count(WRONG)
        if n == 0:
            print(f"  {p}: 0 occurrences (already fixed)")
            continue
        print(f"  {p}: {n} occurrence(s)")
        total += n
        if not args.dry_run:
            Path(str(p) + ".bak").write_text(text, encoding="utf-8")
            p.write_text(text.replace(WRONG, RIGHT), encoding="utf-8")

    print(f"\nTotal replacements: {total}")
    if args.dry_run:
        print("[DRY RUN: no files written]")
    elif total > 0:
        print("\nBackups at <file>.bak alongside each modified file.")
        print("\nNext steps:")
        print("  python3 site_build/build_site.py")
        print("  (rebuild manuscript PDF if needed)")


if __name__ == "__main__":
    main()
