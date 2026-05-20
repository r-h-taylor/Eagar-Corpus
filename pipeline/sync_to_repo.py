#!/usr/bin/env python3
"""
sync_to_repo.py — copy today's corpus work from the working directory
into the git clone, mapping paths correctly.

Working dir:  ~/Dropbox/Research/Eagar Corpus/
Repo clone:   ~/code/Eagar-Corpus/

Path mapping:
  output/v1/lectures/<vid>/<file>   →  corpus/lectures/<vid>/<file>
  <root>/<script>.py                →  pipeline/<script>.py
  output/v1/corpus_id_index.json    →  ontology/corpus_id_index.json
  output/v1/corpus_id_audit.csv     →  ontology/corpus_id_audit.csv
  output/v1/case_function_tags.json →  ontology/case_function_tags.json
  output/v1/case_*_audit.json       →  ontology/

Per-lecture files synced (the 8 repo-tracked types + new layer4.md):
  anchors.json, case_index.md, editorial_register.md,
  extended_case_references.md, layer2.md, layer3.md, metadata.json,
  transformation_log.md, layer4.md (new, only where present)

NOT synced (not in repo / not redistributable / build artifacts):
  - eagar_corpus/ (Layer 1 sources — license-restricted)
  - site/, site_build/ (website not tracked in this repo)
  - *.bak, venv/, __pycache__/
  - Paper/ (manuscript — separate)

Scripts synced to pipeline/ (today's new/modified work):
  generate_corpus_ids.py, add_course_module.py, fix_belmar.py,
  fix_gordon_forward.py, fix_lWfHtQqXYJk_3p5.py,
  fix_chunked_lecture_metadata.py, fix_concept_doi.py,
  reclassify_biographical.py, classify_cases.py

This script COPIES only; it does not stage or commit. After running,
review `git status` in the repo and commit in logical groups.

Usage:
  python3 sync_to_repo.py --dry-run
  python3 sync_to_repo.py
"""

import argparse
import shutil
import sys
from pathlib import Path

WORK = Path.home() / "Dropbox" / "Research" / "Eagar Corpus"
REPO = Path.home() / "code" / "Eagar-Corpus"

PER_LECTURE_FILES = [
    "anchors.json",
    "case_index.md",
    "editorial_register.md",
    "extended_case_references.md",
    "layer2.md",
    "layer3.md",
    "metadata.json",
    "transformation_log.md",
    "layer4.md",  # new optional file; only synced where it exists
]

# Scripts to sync into pipeline/ (today's work)
SCRIPTS = [
    "generate_corpus_ids.py",
    "add_course_module.py",
    "fix_belmar.py",
    "fix_gordon_forward.py",
    "fix_lWfHtQqXYJk_3p5.py",
    "fix_chunked_lecture_metadata.py",
    "fix_concept_doi.py",
    "reclassify_biographical.py",
    "classify_cases.py",
]

# Corpus-level artifacts → ontology/
ONTOLOGY_FILES = [
    ("output/v1/corpus_id_index.json", "ontology/corpus_id_index.json"),
    ("output/v1/corpus_id_audit.csv", "ontology/corpus_id_audit.csv"),
    ("output/v1/case_function_tags.json", "ontology/case_function_tags.json"),
    ("output/v1/case_classification_audit.json", "ontology/case_classification_audit.json"),
    ("output/v1/case_reclassification_audit.json", "ontology/case_reclassification_audit.json"),
]


def copy_file(src: Path, dst: Path, dry_run: bool, stats: dict):
    """Copy src→dst if src exists and differs from dst (or dst missing)."""
    if not src.exists():
        return
    needs_copy = True
    if dst.exists():
        try:
            if src.read_bytes() == dst.read_bytes():
                needs_copy = False
        except Exception:
            needs_copy = True
    if not needs_copy:
        stats["unchanged"] += 1
        return
    stats["changed"] += 1
    stats["changed_paths"].append(str(dst.relative_to(REPO)))
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not WORK.exists():
        print(f"ERROR: working dir not found: {WORK}")
        sys.exit(1)
    if not REPO.exists():
        print(f"ERROR: repo not found: {REPO}")
        sys.exit(1)

    stats = {"changed": 0, "unchanged": 0, "changed_paths": []}

    # 1. Per-lecture files
    work_lectures = WORK / "output" / "v1" / "lectures"
    repo_lectures = REPO / "corpus" / "lectures"
    n_lectures = 0
    for lec_dir in sorted(work_lectures.iterdir()):
        if not lec_dir.is_dir():
            continue
        n_lectures += 1
        vid = lec_dir.name
        for fname in PER_LECTURE_FILES:
            src = lec_dir / fname
            dst = repo_lectures / vid / fname
            copy_file(src, dst, args.dry_run, stats)

    # 2. Scripts → pipeline/
    for script in SCRIPTS:
        src = WORK / script
        dst = REPO / "pipeline" / script
        copy_file(src, dst, args.dry_run, stats)

    # 3. Ontology artifacts
    for rel_src, rel_dst in ONTOLOGY_FILES:
        src = WORK / rel_src
        dst = REPO / rel_dst
        copy_file(src, dst, args.dry_run, stats)

    print(f"=== Sync summary ===")
    print(f"  Lectures scanned: {n_lectures}")
    print(f"  Files changed: {stats['changed']}")
    print(f"  Files unchanged: {stats['unchanged']}")

    if stats["changed_paths"]:
        print(f"\n  Changed paths (first 40):")
        for p in stats["changed_paths"][:40]:
            print(f"    {p}")
        if len(stats["changed_paths"]) > 40:
            print(f"    ... and {len(stats['changed_paths']) - 40} more")

    if args.dry_run:
        print(f"\n[DRY RUN: no files copied]")
    else:
        print(f"\nFiles copied into {REPO}")
        print(f"\nNext steps:")
        print(f"  cd ~/code/Eagar-Corpus")
        print(f"  git status")
        print(f"  # then commit in logical groups (see suggested plan)")


if __name__ == "__main__":
    main()
