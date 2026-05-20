#!/usr/bin/env python3
"""
generate_corpus_ids.py — assign each lecture a corpus_id of the form
<CODE>_<TERM><YEAR>_<NN>, where:
  - CODE     : canonical course abbreviation (SMS, WM, CAS, etc.)
  - TERM     : S | Su | F
  - YEAR     : 4-digit calendar year
  - NN       : 2-digit zero-padded sequence within the course-term

Sequence sources, in priority order:
  1. metadata.json has lecture_number_in_series  (manual patches like the
     two chunked lectures we restored)
  2. Source filename has playlist series tag [N/M]  (281 of 425 files)
  3. Source filename has upload date YYYY_MM_DD     (113 of 425 files)
  4. Fallback: alphabetical-by-video-id within (course, term)

Within a (course, term) group, lectures with explicit numbering (1 or 2)
take their stated positions; lectures using fallback (3 or 4) fill in
the remaining slots in order, never colliding with explicit numbers.

Writes:
  - corpus_id added to each output/v1/lectures/<vid>/metadata.json
  - output/v1/corpus_id_index.json : {video_id: corpus_id, ...}
  - output/v1/corpus_id_audit.csv  : human-readable preview

Idempotent. Writes .bak before overwriting each metadata.json.

Usage:
  python3 generate_corpus_ids.py --preview        # dry-run, print CSV
  python3 generate_corpus_ids.py --apply          # write
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date as date_type
from pathlib import Path


# ============================================================
# Canonical course → CODE mapping
# ============================================================

COURSE_CODES = {
    "Additive Manufacturing": "AM",
    "Casting": "CAS",
    "Codes and Standards": "CS",
    "Corrosion": "COR",
    "Corrosion Cracking and More": "CCM",
    "Deformation Processing": "DP",
    "Fusion Welding": "FW",
    "How to be a Successful Engineer": "SE",
    "Materials Selection": "MS",
    "Materials Selection and Economics": "MSE",
    "Recitations": "REC",
    "Solid State Welding": "SSW",
    "Structural Materials Selection": "SMS",
    "Total Quality Improvement": "TQI",
    "Welding Metallurgy": "WM",
    "Welding Quality": "WQ",
    "What is Engineering": "WIE",
}


# ============================================================
# Term parsing → short code
# ============================================================

TERM_PREFIX = {"spring": "S", "summer": "Su", "fall": "F"}


def parse_term(t: str):
    """'Fall 2013' -> ('F', '2013'). Returns (None, None) if unparseable."""
    if not t:
        return None, None
    m = re.match(r"^(Spring|Summer|Fall)\s+(\d{4})$", t.strip(), re.IGNORECASE)
    if not m:
        return None, None
    return TERM_PREFIX[m.group(1).lower()], m.group(2)


# ============================================================
# Source filename parsing
# ============================================================

EAGAR_CORPUS_DIR = Path("eagar_corpus")
LECTURES_DIR = Path("output/v1/lectures")

P_SEQ = re.compile(r'^\d+__.+?__(\d+)_(\d+)__([A-Za-z0-9_-]+)$')
P_DATE = re.compile(r'^\d+__(\d{4})_(\d{2})_(\d{2})__([A-Za-z0-9_-]+)$')
P_PLAIN = re.compile(r'^\d+__.+__([A-Za-z0-9_-]+)$')


def parse_source_filename(name: str):
    """Returns dict with keys: video_id (always present), and one of
    {seq: int, total: int} or {date: str} if applicable."""
    out = {}
    m = P_SEQ.match(name)
    if m:
        out["video_id"] = m.group(3)
        out["seq"] = int(m.group(1))
        out["total"] = int(m.group(2))
        return out
    m = P_DATE.match(name)
    if m:
        out["video_id"] = m.group(4)
        out["date"] = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        return out
    m = P_PLAIN.match(name)
    if m:
        out["video_id"] = m.group(1)
        return out
    return None


def build_source_index():
    """Walk eagar_corpus/ and build {video_id: {seq?, total?, date?, source_file}}."""
    index = {}
    for f in EAGAR_CORPUS_DIR.rglob("*.txt"):
        if f.name.endswith(".bak"):
            continue
        parsed = parse_source_filename(f.stem)
        if parsed is None:
            continue
        vid = parsed["video_id"]
        if vid in index:
            # Duplicate filenames for same video_id — shouldn't happen but skip
            continue
        parsed["source_file"] = f.name
        index[vid] = parsed
    return index


# ============================================================
# Main: assign corpus_ids
# ============================================================

def assign_corpus_ids():
    """Returns list of (video_id, corpus_id, audit_dict) sorted by corpus_id."""

    source_index = build_source_index()

    # Step 1: load all lecture metadata
    lectures = []
    for meta_path in LECTURES_DIR.glob("*/metadata.json"):
        vid = meta_path.parent.name
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        course = m.get("course_module") or m.get("course_canonical") or m.get("course") or ""
        if isinstance(course, list):
            course = course[0] if course else ""
        term = m.get("term", "")
        if isinstance(term, list):
            term = term[0] if term else ""
        explicit_seq = m.get("lecture_number_in_series")
        source = source_index.get(vid, {})
        lectures.append({
            "video_id": vid,
            "meta_path": meta_path,
            "course": course,
            "term": term,
            "explicit_seq": explicit_seq,
            "source_seq": source.get("seq"),
            "source_total": source.get("total"),
            "source_date": source.get("date"),
        })

    # Step 2: group by (course, term)
    groups = defaultdict(list)
    for lec in lectures:
        groups[(lec["course"], lec["term"])].append(lec)

    # Step 3: within each group, assign sequence numbers
    assignments = []  # list of (video_id, corpus_id, audit)
    for (course, term), lecs in sorted(groups.items()):
        code = COURSE_CODES.get(course)
        term_prefix, year = parse_term(term)

        if code is None or term_prefix is None:
            # Can't build a corpus_id for this group; mark unassignable
            for lec in lecs:
                assignments.append((
                    lec["video_id"],
                    None,
                    {
                        "video_id": lec["video_id"],
                        "course": course,
                        "term": term,
                        "corpus_id": None,
                        "seq_source": "ERROR: unmapped course or term",
                    }
                ))
            continue

        # Priority for sequence:
        # 1. explicit lecture_number_in_series
        # 2. source_seq from filename
        # 3. source_date (rank within group by date)
        # 4. alphabetical by video_id

        # First pass: lectures with explicit or source_seq numbers — these claim their slots
        used_slots = set()
        explicit_assignments = []
        date_pending = []
        fallback_pending = []

        for lec in lecs:
            raw_seq = lec["explicit_seq"] or lec["source_seq"]
            seq = None
            if raw_seq is not None:
                try:
                    seq = int(raw_seq)
                except (TypeError, ValueError):
                    seq = None
            if seq is not None:
                if seq in used_slots:
                    # Collision — bump to fallback (shouldn't happen with clean data)
                    fallback_pending.append(lec)
                else:
                    used_slots.add(seq)
                    explicit_assignments.append((lec, seq, "explicit" if lec["explicit_seq"] else "source_seq"))
            elif lec["source_date"]:
                date_pending.append(lec)
            else:
                fallback_pending.append(lec)

        # Second pass: lectures with dates get sorted by date and given the
        # next available slots
        date_pending.sort(key=lambda l: l["source_date"])
        next_slot = 1
        date_assignments = []
        for lec in date_pending:
            while next_slot in used_slots:
                next_slot += 1
            used_slots.add(next_slot)
            date_assignments.append((lec, next_slot, "source_date"))
            next_slot += 1

        # Third pass: fallback (alphabetical by video_id)
        fallback_pending.sort(key=lambda l: l["video_id"])
        next_slot = 1
        fallback_assignments = []
        for lec in fallback_pending:
            while next_slot in used_slots:
                next_slot += 1
            used_slots.add(next_slot)
            fallback_assignments.append((lec, next_slot, "fallback"))
            next_slot += 1

        # Build corpus_id strings
        for lec, slot, source in (explicit_assignments + date_assignments + fallback_assignments):
            cid = f"{code}_{term_prefix}{year}_{int(slot):02d}"
            assignments.append((
                lec["video_id"],
                cid,
                {
                    "video_id": lec["video_id"],
                    "course": course,
                    "term": term,
                    "corpus_id": cid,
                    "seq_source": source,
                }
            ))

    return assignments


# ============================================================
# Write
# ============================================================

def write_audit(assignments, path):
    """Write CSV-style audit file."""
    lines = ["video_id,corpus_id,course,term,seq_source"]
    for vid, cid, audit in sorted(assignments, key=lambda x: x[1] or "zzz"):
        c = audit["course"].replace(",", ";")
        t = audit["term"].replace(",", ";")
        lines.append(f"{vid},{cid or ''},{c},{t},{audit['seq_source']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index(assignments, path):
    """Write JSON index mapping video_id <-> corpus_id."""
    index = {
        "video_id_to_corpus_id": {vid: cid for vid, cid, _ in assignments if cid},
        "corpus_id_to_video_id": {cid: vid for vid, cid, _ in assignments if cid},
        "generated_at": date_type.today().isoformat(),
    }
    path.write_text(json.dumps(index, indent=2), encoding="utf-8")


def write_metadata_fields(assignments):
    """Write corpus_id into each lecture's metadata.json with backup."""
    n_written = 0
    n_skipped = 0
    for vid, cid, _ in assignments:
        if cid is None:
            n_skipped += 1
            continue
        meta_path = LECTURES_DIR / vid / "metadata.json"
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        if m.get("corpus_id") == cid:
            continue  # idempotent: already correct
        Path(str(meta_path) + ".bak").write_text(
            meta_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        m["corpus_id"] = cid
        meta_path.write_text(json.dumps(m, indent=2), encoding="utf-8")
        n_written += 1
    return n_written, n_skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Print preview, don't write")
    parser.add_argument("--apply", action="store_true", help="Write to metadata + index")
    args = parser.parse_args()

    if not args.preview and not args.apply:
        print("ERROR: must specify --preview or --apply")
        sys.exit(1)

    assignments = assign_corpus_ids()

    # Summary
    total = len(assignments)
    assigned = sum(1 for _, c, _ in assignments if c)
    unassigned = total - assigned

    seq_source_counts = defaultdict(int)
    for _, _, audit in assignments:
        seq_source_counts[audit["seq_source"]] += 1

    print(f"=== Summary ===")
    print(f"  Total lectures: {total}")
    print(f"  Assigned corpus_id: {assigned}")
    if unassigned:
        print(f"  Unassigned (unmapped course/term): {unassigned}")
    print(f"\nSequence sources:")
    for src, n in sorted(seq_source_counts.items()):
        print(f"  {src:20s} {n:>3}")

    # Preview a sample
    print(f"\nFirst 20 assignments (sorted by corpus_id):")
    for vid, cid, audit in sorted(assignments, key=lambda x: x[1] or "zzz")[:20]:
        print(f"  {cid or '(unassigned)':25s} ← {vid:15s} ({audit['seq_source']})")

    audit_path = Path("output/v1/corpus_id_audit.csv")
    index_path = Path("output/v1/corpus_id_index.json")

    if args.preview:
        # Always write the audit so reviewer can scrutinize
        write_audit(assignments, audit_path)
        print(f"\n[PREVIEW]")
        print(f"  Audit written to {audit_path}")
        print(f"  No metadata.json files modified.")
        print(f"  Review the audit, then run with --apply to write.")
        return

    # --apply
    write_audit(assignments, audit_path)
    write_index(assignments, index_path)
    n_written, n_skipped = write_metadata_fields(assignments)
    print(f"\n=== Applied ===")
    print(f"  Audit: {audit_path}")
    print(f"  Index: {index_path}")
    print(f"  metadata.json files updated: {n_written}")
    if n_skipped:
        print(f"  metadata.json files skipped (unassignable): {n_skipped}")
    print(f"\n  Backups at <metadata.json>.bak alongside each modified file.")
    print(f"\nNext: rebuild the site to surface corpus_ids in the browse table.")
    print(f"  python3 site_build/build_site.py")


if __name__ == "__main__":
    main()
