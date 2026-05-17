#!/usr/bin/env python3
"""
canonicalize_courses.py — normalize the `course` field across all lecture
metadata files, deduplicating naming variants into canonical module names.

Output:
  - Adds a `course_canonical` field to each metadata.json (preserves the
    original `course` value for audit)
  - Writes output/v1/course_canonicalization_map.json with the full mapping
  - Reports the count of distinct canonical (course, term) modules

The mapping is hand-curated based on inspection of the raw 31 (course, term)
pairs. Each rule has a source raw value and a target canonical value; rules
are applied in the order listed.

Usage:
    python3 canonicalize_courses.py --dry-run
    python3 canonicalize_courses.py
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

LECTURES_DIR = Path("output/v1/lectures")
MAP_OUTPUT = Path("output/v1/course_canonicalization_map.json")


# Canonicalization rules: (raw_course_substring, raw_term, canonical_course)
# Order matters — first match wins.
RULES = [
    # Codes and standards Fall 2012: three names, one module
    ("Codes and Standards Definitions and History", "Fall 2012", "Codes and Standards"),
    ("Codes and Standards for Safety", "Fall 2012", "Codes and Standards"),
    ("Codes and Standards", "Fall 2012", "Codes and Standards"),

    # Codes and standards Summer 2012: keep as-is, separate offering
    ("Codes and Standards", "Summer 2012", "Codes and Standards"),

    # Materials Selection Fall 2016: three variants, one module
    ("Materials Selection — Properties, Costs, Externalities", "Fall 2016", "Materials Selection"),
    ("Materials Selection - Properties Costs Externalities", "Fall 2016", "Materials Selection"),
    ("Materials Selection - Weighing Trade-Offs", "Fall 2016", "Materials Selection"),

    # Materials Selection Fall 2017: keep, separate offering
    ("Materials Selection and Economics", "Fall 2017", "Materials Selection and Economics"),

    # Structural Materials Selection Spring 2016: three variants, one module
    ("Structural Materials Selection Examples", "Spring 2016", "Structural Materials Selection"),
    ("Structural Materials Selection Principles", "Spring 2016", "Structural Materials Selection"),
    ("Structural Materials Selection", "Spring 2016", "Structural Materials Selection"),

    # Structural Materials Selection Fall 2013/2014: keep as-is, separate offerings
    ("Structural Materials Selection", "Fall 2013", "Structural Materials Selection"),
    ("Structural Materials Selection", "Fall 2014", "Structural Materials Selection"),

    # MrHfe8l0600 — Fall 2017 lecture metadata says "3.371 Structural Materials"
    # but the YouTube title is "3.371 Structural Materials - Fall 2017 Course
    # Overview", and the other 6 Fall 2017 lectures are labeled "Materials
    # Selection and Economics". Treat this as the opening overview lecture of
    # the Materials Selection and Economics Fall 2017 module (giving a clean
    # 7-lecture module).
    ("Structural Materials", "Fall 2017", "Materials Selection and Economics"),

    # Corrosion Summer 2016 and Corrosion Cracking Summer 2014: distinct
    ("Corrosion Cracking and More", "Summer 2014", "Corrosion Cracking and More"),
    ("Corrosion", "Summer 2016", "Corrosion"),

    # Welding Metallurgy: three offerings (Spring 2014, Summer 2014, Summer 2015)
    # All keep the canonical name "Welding Metallurgy", distinguished by term.
    ("Welding Metallurgy", None, "Welding Metallurgy"),

    # Everything else is identity-mapped
    ("Additive Manufacturing", None, "Additive Manufacturing"),
    ("Casting", None, "Casting"),
    ("Deformation Processing", None, "Deformation Processing"),
    ("Fusion Welding", None, "Fusion Welding"),
    ("How to be a Successful Engineer", None, "How to be a Successful Engineer"),
    ("Recitations", None, "Recitations"),
    ("Solid State Welding", None, "Solid State Welding"),
    ("Total Quality Improvement", None, "Total Quality Improvement"),
    ("Welding Quality", None, "Welding Quality"),
    ("What is Engineering", None, "What is Engineering"),
]


def normalize_course_raw(course: str) -> str:
    """Strip leading '3.371' from raw course string for matching."""
    course = " ".join(course.split())
    if course.startswith("3.371 "):
        course = course[len("3.371 "):]
    return course


def canonicalize(course_raw: str, term: str) -> tuple[str, str] | None:
    """Return (canonical_course, matched_rule_index) or None if no rule matched."""
    norm = normalize_course_raw(course_raw)
    for i, (raw_pattern, raw_term, canonical) in enumerate(RULES):
        # Match by exact normalized course, with optional term constraint
        if norm == raw_pattern:
            if raw_term is None or raw_term == term:
                return canonical, i
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Plan only, don't modify metadata.json files")
    args = parser.parse_args()

    canonical_instances = Counter()
    audit = []
    unmatched = []

    metadata_files = sorted(LECTURES_DIR.glob("*/metadata.json"))
    print(f"Processing {len(metadata_files)} metadata files...")

    for p in metadata_files:
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ERROR reading {p}: {e}")
            continue

        course_raw = m.get("course")
        term = m.get("term")
        vid = m.get("video_id", p.parent.name)

        if not course_raw or not term:
            audit.append({"video_id": vid, "course_raw": course_raw, "term": term,
                          "status": "missing_field"})
            continue

        result = canonicalize(course_raw, term)
        if result is None:
            unmatched.append((course_raw, term, vid))
            audit.append({"video_id": vid, "course_raw": course_raw, "term": term,
                          "status": "no_rule_match"})
            continue

        canonical_course, rule_idx = result
        canonical_instances[(canonical_course, term)] += 1
        audit.append({
            "video_id": vid,
            "course_raw": course_raw,
            "term": term,
            "course_canonical": canonical_course,
            "rule_index": rule_idx,
            "status": "mapped",
        })

        if not args.dry_run:
            # Update the metadata file: add course_canonical, preserve course
            if m.get("course_canonical") != canonical_course:
                m["course_canonical"] = canonical_course
                p.write_text(json.dumps(m, indent=2), encoding="utf-8")

    # Report
    print(f"\nCanonical (course, term) instances: {len(canonical_instances)}")
    print()
    print("Canonical course modules (sorted by term then course):")
    for (course, term), n in sorted(canonical_instances.items(),
                                     key=lambda x: (x[0][1], x[0][0])):
        print(f"  {n:>3}  {course:<48s} {term}")

    if unmatched:
        print(f"\nWARNING: {len(unmatched)} unmatched (course, term) pairs:")
        for c, t, vid in unmatched[:10]:
            print(f"  {vid}  {c} | {t}")

    print(f"\nDistinct canonical courses: {len({c for c, _ in canonical_instances})}")
    print(f"Distinct canonical (course, term) modules: {len(canonical_instances)}")

    if not args.dry_run:
        report = {
            "rules_used": [{"raw_pattern": r[0], "raw_term": r[1], "canonical": r[2]}
                           for r in RULES],
            "canonical_modules": [
                {"course_canonical": c, "term": t, "n_lectures": n}
                for (c, t), n in sorted(canonical_instances.items(),
                                         key=lambda x: (x[0][1], x[0][0]))
            ],
            "audit": audit,
            "unmatched": [{"course_raw": c, "term": t, "video_id": v}
                          for c, t, v in unmatched],
        }
        MAP_OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote audit: {MAP_OUTPUT}")
        print("(Each lecture's metadata.json now has a course_canonical field.)")


if __name__ == "__main__":
    main()
