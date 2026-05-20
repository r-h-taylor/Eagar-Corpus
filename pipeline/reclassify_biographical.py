#!/usr/bin/env python3
"""
reclassify_biographical.py — second-pass cleanup of cases tagged
"biographical" in case_function_tags.json.

The first-pass classifier over-tagged biographical: anything where Tom's
name appears in the frame text tended to get biographical, even when the
case content was primarily forensic (failure) or industrial-historical
(program/decision). This script re-asks with a sharper definition.

Approach:
  1. Load case_function_tags.json
  2. For each "biographical"-tagged case, ask the model with a stricter
     prompt to recategorize as:
       - keep-biographical (case IS Tom's career story)
       - industrial-historical (case is a program/decision Tom narrates)
       - forensic (case is a failure Tom narrates)
       - technical-narrative (case is a technical development Tom narrates)
       - mixed (genuinely spans)
  3. Update case_function_tags.json with corrections
  4. Write audit of changes to case_reclassification_audit.json

Usage:
  python3 reclassify_biographical.py --dry-run
  python3 reclassify_biographical.py
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
MAX_TOKENS = 300

LECTURES_DIR = Path("output/v1/lectures")
TAGS_PATH = Path("output/v1/case_function_tags.json")
AUDIT_PATH = Path("output/v1/case_reclassification_audit.json")


SHARPER_PROMPT = """You re-examine a case from Prof. Thomas W. Eagar's MIT teaching
corpus that was tentatively tagged "biographical" in a first pass. The
first pass tended to over-classify as biographical: whenever Tom's name
or first-person involvement appeared in the frame text, it tagged
biographical even when the case content was primarily about something
else.

The strict definition:

  biographical : The case IS Tom's career story. Examples:
                 - Tom's Bethlehem Steel apprenticeship
                 - Tom's MIT lab anecdotes about his own work
                 - Tom's consulting cases told as "what happened to me"
                 - An event in Tom's professional life
                 The case is ABOUT Tom's experience, not just narrated by Tom.

If Tom is narrating someone else's program, failure, or development,
re-classify based on the case content:

  industrial-historical : Named industrial actors, business decisions,
                          manufacturing-economics narratives. A company's
                          program, a market decision, an industry trend.

  forensic              : Failure analysis, accident investigation,
                          technical autopsy. A crack, a collapse, a
                          contamination, a litigated failure.

  technical-narrative   : Science-to-engineering arc where the physics
                          or process IS the story. A development cycle,
                          a discovery, a technical evolution.

  mixed                 : Case genuinely spans 2+ above categories. Use
                          sparingly.

Output exactly one JSON object:
{"tag": "<biographical | industrial-historical | forensic | technical-narrative | mixed>", "confidence": "high"|"medium"|"low", "reason": "<one short clause>"}.

The "reason" field should be a brief justification (under 20 words)
explaining why this tag fits the case content.

No other text."""


def parse_case_anchors_with_frames(case_index_path: Path) -> list[dict]:
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
    frames = defaultdict(list)
    for lec_dir in sorted(LECTURES_DIR.iterdir()):
        if not lec_dir.is_dir():
            continue
        ci = lec_dir / "case_index.md"
        for entry in parse_case_anchors_with_frames(ci):
            cid = entry["cluster_id"]
            if len(frames[cid]) < 3 and entry["frame_text"]:  # 3 frames for this pass
                frames[cid].append(entry["frame_text"])
    return frames


def reclassify(client: Anthropic, cluster_id: str, frame_texts: list[str]) -> dict:
    frames_block = "\n\n".join(f"  Frame {i+1}: {ft}" for i, ft in enumerate(frame_texts))
    if not frames_block:
        frames_block = "  (no frame text available)"

    user_message = f"""Re-examine this case, which was tentatively tagged "biographical".

Canonical cluster id: "{cluster_id}"

Frame descriptions of how Tom uses it in lectures:
{frames_block}

Re-classify per the strict definition. Return:
{{"tag": "<one of: biographical | industrial-historical | forensic | technical-narrative | mixed>", "confidence": "high"|"medium"|"low", "reason": "<short clause>"}}."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SHARPER_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        m = re.search(
            r'\{\s*"tag"\s*:\s*"(biographical|industrial-historical|forensic|technical-narrative|mixed)"\s*,'
            r'\s*"confidence"\s*:\s*"(high|medium|low)"\s*,'
            r'\s*"reason"\s*:\s*"([^"]+)"\s*\}',
            text,
        )
        if m:
            return {"tag": m.group(1), "confidence": m.group(2),
                    "reason": m.group(3), "raw": text}
        return {"tag": "biographical", "confidence": "low",
                "reason": "parse failed; kept original", "raw": text,
                "parse_failed": True}
    except Exception as e:
        return {"tag": "biographical", "confidence": "low",
                "reason": f"error: {type(e).__name__}", "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    tags = json.loads(TAGS_PATH.read_text(encoding="utf-8"))
    biographical = [cid for cid, tag in tags.items() if tag == "biographical"]
    print(f"Found {len(biographical)} cases tagged 'biographical'")

    if args.limit:
        biographical = biographical[:args.limit]
        print(f"  limiting to first {len(biographical)}")

    frames_per_cluster = collect_frames_per_cluster()

    if args.dry_run:
        print(f"\n[DRY RUN] First 5 cases that would be re-examined:")
        for cid in biographical[:5]:
            print(f"\n  cluster: {cid}")
            for i, ft in enumerate(frames_per_cluster.get(cid, []), 1):
                preview = ft[:150].replace("\n", " ")
                print(f"    frame {i}: {preview}...")
        return

    client = Anthropic()
    changes = []
    new_tags = dict(tags)
    counts = defaultdict(int)

    for i, cid in enumerate(biographical, 1):
        result = reclassify(client, cid, frames_per_cluster.get(cid, []))
        new_tag = result["tag"]
        new_tags[cid] = new_tag
        counts[new_tag] += 1
        if new_tag != "biographical":
            changes.append({
                "cluster_id": cid,
                "old_tag": "biographical",
                "new_tag": new_tag,
                "confidence": result["confidence"],
                "reason": result["reason"],
            })

        if i % 25 == 0:
            print(f"  [{i:>3}/{len(biographical)}]  changed so far: {len(changes)}")
            # Checkpoint
            TAGS_PATH.write_text(json.dumps(new_tags, indent=2, sort_keys=True),
                                  encoding="utf-8")
        time.sleep(0.05)

    # Final save
    TAGS_PATH.write_text(json.dumps(new_tags, indent=2, sort_keys=True), encoding="utf-8")
    AUDIT_PATH.write_text(json.dumps({
        "total_reviewed": len(biographical),
        "kept_biographical": counts["biographical"],
        "reclassified": len(changes),
        "by_new_tag": dict(counts),
        "changes": changes,
    }, indent=2), encoding="utf-8")

    print(f"\n=== Reclassification summary ===")
    print(f"  reviewed:          {len(biographical)}")
    print(f"  kept biographical: {counts['biographical']}")
    print(f"  reclassified:      {len(changes)}")
    print(f"\n  new distribution of the reviewed set:")
    for tag, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {tag:25s} {n:>4}")

    print(f"\nWrote updated {TAGS_PATH}")
    print(f"Wrote {AUDIT_PATH}")
    print(f"\nSample of reclassifications:")
    for c in changes[:10]:
        print(f"  {c['old_tag']:15s} → {c['new_tag']:25s}  {c['cluster_id'][:60]}")
        print(f"    reason: {c['reason']}")


if __name__ == "__main__":
    main()
