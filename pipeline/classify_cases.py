#!/usr/bin/env python3
"""
classify_cases.py — assign function tags to every canonical case cluster
in the corpus via model-assisted classification.

Schema:
  - industrial-historical : Named industrial actors, business decisions,
                            manufacturing-economics narratives
  - forensic              : Failure analysis, accident investigation,
                            technical autopsy
  - biographical          : Tom's first-person professional history
  - technical-narrative   : Science-to-engineering arc with physics as
                            the storyline
  - mixed                 : Case meaningfully spans 2+ tags

The classifier is conservative: if the case primarily fits one category,
it picks that. If it genuinely spans multiple, it returns "mixed."

For each cluster, the classifier sees:
  - canonical_cluster_id
  - one or two "Frame in this lecture" descriptions from case_index.md
    entries where the case appears (best evidence for how Tom uses it)

Output:
  output/v1/case_function_tags.json   {cluster_id: tag, ...}
  output/v1/case_classification_audit.json   detailed audit log

Usage:
  python3 classify_cases.py --dry-run
  python3 classify_cases.py --limit 20    # test
  python3 classify_cases.py               # full run
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    sys.exit(1)


MODEL = "claude-opus-4-7"
MAX_TOKENS = 256  # classification responses are tiny

LECTURES_DIR = Path("output/v1/lectures")
OUT_TAGS = Path("output/v1/case_function_tags.json")
OUT_AUDIT = Path("output/v1/case_classification_audit.json")

# Seed tags from Table 1 of the JME paper. These won't be reclassified;
# we accept them as ground truth.
SEED_TAGS = {
    "industrial-historical": [
        "Saugus Ironworks",
        "1973 Arab oil embargo",
        "Bethlehem Steel Burns Harbor",
        "Watertown Arsenal titanium development",
        "Basic oxygen furnace introduction in Austria",
        "Continuous casting and steel industry capacity collapse",
        "Wright brothers' aircraft engine",
        "British Welding Institute founding",
        "Andrew Mellon all-aluminum Pierce Arrow automobile",
        "Clayton Christensen innovator's dilemma research—steel mill cost data",
        "Air Force Buy-to-Fly Ratio in Aircraft Manufacturing",
        "Lakshmi Mittal steel mill acquisition strategy",
    ],
    "forensic": [
        "Liberty ships and SS Schenectady",
        "World Trade Center collapse",
        "V-22 Osprey aircraft",
        "Soviet Alpha-class submarine",
        "Space Shuttle Challenger",
        "Space Shuttle cost overrun",
    ],
    "biographical": [
        "Tom Eagar's steel company experience",
    ],
    "technical-narrative": [
        "Iron whiskers (1950s screw dislocation studies)",
    ],
}


SYSTEM_PROMPT = """You classify a recurring case from Prof. Thomas W. Eagar's MIT teaching
corpus into one of five pedagogical function tags. Tom Eagar (MIT
Materials Science, 1976–2022) taught through recurring industrial
cases. Each case has a primary pedagogical function.

The five tags:

  industrial-historical : Named industrial actors, business decisions,
                          manufacturing-economics narratives. Examples:
                          Bethlehem Steel Burns Harbor, the 1973 oil
                          embargo, Wright brothers' engine. Tom uses
                          these to teach about industrial structure,
                          productivity, and historical engineering decisions.

  forensic              : Failure analysis, accident investigation,
                          technical autopsy. Examples: Liberty ship
                          brittle fracture, WTC collapse, Space Shuttle
                          Challenger O-ring failure. Tom uses these to
                          teach engineering judgment under uncertainty,
                          why things fail.

  biographical          : Tom's first-person professional history.
                          Examples: his Bethlehem Steel apprenticeship,
                          his MIT lab anecdotes, his consulting cases
                          told as "I was there, I saw it, this is what
                          happened to me." First-person testimony.

  technical-narrative   : Science-to-engineering arc where the physics
                          IS the story. Examples: iron whiskers and
                          screw dislocations, the development of an
                          alloy where the technical evolution is the
                          narrative. Tom traces the technical concepts
                          themselves as a story.

  mixed                 : The case genuinely spans two or more of the
                          above and cannot be classified as one primary
                          frame.

Be decisive but honest. Most cases have one dominant frame; pick it.
Only use "mixed" when two frames are equally primary.

Output exactly one JSON object: {"tag": "<one of the five tags>", "confidence": "high"|"medium"|"low"}.
No other text."""


def parse_case_anchors_with_frames(case_index_path: Path) -> list[dict]:
    """Parse case_index.md, return list of {cluster_id, frame_text}."""
    if not case_index_path.exists():
        return []
    text = case_index_path.read_text(encoding="utf-8")
    out = []
    for block in re.split(r"\n(?=### )", text):
        if not block.startswith("### "):
            continue
        cid_m = re.search(r'canonical_cluster_id:\s*\*?\*?\s*"([^"]+)"', block)
        if not cid_m:
            continue
        cluster_id = cid_m.group(1)
        if cluster_id.startswith("PROPOSED:"):
            continue
        frame_m = re.search(r"\*\*Frame in this lecture:\*\*\s*([^\n]+(?:\n(?!- )[^\n]+)*)", block)
        frame_text = frame_m.group(1).strip() if frame_m else ""
        out.append({"cluster_id": cluster_id, "frame_text": frame_text})
    return out


def collect_frames_per_cluster() -> dict[str, list[str]]:
    """For each canonical cluster, gather the 'Frame in this lecture' text
    from up to 2 of its case_index.md occurrences (for variety)."""
    frames = defaultdict(list)
    for lec_dir in sorted(LECTURES_DIR.iterdir()):
        if not lec_dir.is_dir():
            continue
        ci = lec_dir / "case_index.md"
        for entry in parse_case_anchors_with_frames(ci):
            cid = entry["cluster_id"]
            if len(frames[cid]) < 2 and entry["frame_text"]:
                frames[cid].append(entry["frame_text"])
    return frames


def classify_case(client: Anthropic, cluster_id: str, frame_texts: list[str]) -> dict:
    """Returns {tag, confidence, raw_response}."""
    frames_block = "\n\n".join(f"  Frame {i+1}: {ft}" for i, ft in enumerate(frame_texts))
    if not frames_block:
        frames_block = "  (no frame text available; classify from cluster name alone)"

    user_message = f"""Classify this case from Tom Eagar's teaching corpus.

Canonical cluster id: "{cluster_id}"

How Tom frames it in lectures:
{frames_block}

Return {{"tag": "<one of: industrial-historical | forensic | biographical | technical-narrative | mixed>", "confidence": "high"|"medium"|"low"}}."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        m = re.search(
            r'\{\s*"tag"\s*:\s*"(industrial-historical|forensic|biographical|technical-narrative|mixed)"\s*,\s*"confidence"\s*:\s*"(high|medium|low)"\s*\}',
            text,
        )
        if m:
            return {"tag": m.group(1), "confidence": m.group(2), "raw": text}
        return {"tag": "mixed", "confidence": "low", "raw": text, "parse_failed": True}
    except Exception as e:
        return {"tag": "mixed", "confidence": "low", "error": f"{type(e).__name__}: {e}"}


def load_existing_tags() -> dict:
    """Resume support: if previous tags exist, skip those cases."""
    if OUT_TAGS.exists():
        try:
            return json.loads(OUT_TAGS.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Test on first N cases")
    parser.add_argument("--resume", action="store_true",
                        help="Skip cases already classified in output/case_function_tags.json")
    args = parser.parse_args()

    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = None if args.dry_run else Anthropic()

    # Collect every canonical cluster referenced in the corpus + frame texts
    print("Collecting cases and frame descriptions...")
    frames_per_cluster = collect_frames_per_cluster()
    all_clusters = sorted(frames_per_cluster.keys())
    print(f"  found {len(all_clusters)} canonical clusters referenced in case_index files")

    # Apply seeds (and never reclassify them)
    tags = {}
    audit = []
    for tag, cluster_list in SEED_TAGS.items():
        for cid in cluster_list:
            tags[cid] = tag
            audit.append({"cluster_id": cid, "tag": tag, "confidence": "seeded",
                          "source": "table_1_seed"})

    # Resume support
    if args.resume:
        prior = load_existing_tags()
        for cid, tag in prior.items():
            if cid not in tags:
                tags[cid] = tag

    # Decide what to classify
    targets = [c for c in all_clusters if c not in tags]
    if args.limit:
        targets = targets[:args.limit]
    print(f"  classifying {len(targets)} unclassified clusters "
          f"({len(tags)} already seeded/resumed)")

    if args.dry_run:
        print("\n[DRY RUN: first 5 sample inputs]")
        for cid in targets[:5]:
            fts = frames_per_cluster[cid]
            print(f"\n  cluster: {cid}")
            for i, ft in enumerate(fts, 1):
                preview = ft[:120].replace("\n", " ")
                print(f"    frame {i}: {preview}...")
        return

    # Live classification
    counts = defaultdict(int)
    for i, cid in enumerate(targets, 1):
        frame_texts = frames_per_cluster[cid]
        result = classify_case(client, cid, frame_texts)
        tags[cid] = result["tag"]
        counts[result["tag"]] += 1
        audit.append({
            "cluster_id": cid,
            "tag": result["tag"],
            "confidence": result["confidence"],
            "frame_count": len(frame_texts),
            "source": "model",
            **({"error": result["error"]} if "error" in result else {}),
            **({"parse_failed": True} if result.get("parse_failed") else {}),
        })

        if i % 25 == 0:
            print(f"  [{i:>4}/{len(targets)}]  " +
                  ", ".join(f"{t}={n}" for t, n in counts.items()))
            # Checkpoint every 25
            OUT_TAGS.write_text(json.dumps(tags, indent=2, sort_keys=True), encoding="utf-8")

        time.sleep(0.05)  # gentle pacing

    # Final save
    OUT_TAGS.write_text(json.dumps(tags, indent=2, sort_keys=True), encoding="utf-8")
    OUT_AUDIT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_TAGS}")
    print(f"Wrote {OUT_AUDIT}")

    # Final summary
    all_tag_counts = defaultdict(int)
    for tag in tags.values():
        all_tag_counts[tag] += 1
    print("\n=== Final classification ===")
    for tag in ["industrial-historical", "forensic", "biographical",
                "technical-narrative", "mixed"]:
        print(f"  {tag:25s} {all_tag_counts[tag]:>4}")
    print(f"  {'TOTAL':25s} {sum(all_tag_counts.values()):>4}")


if __name__ == "__main__":
    main()
