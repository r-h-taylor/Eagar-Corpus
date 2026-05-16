#!/usr/bin/env python3
"""
process_chunked_lecture.py — process each chunk of a chunked lecture
through Call 1 and Call 2, with chunk-aware prompting.

Reads chunks/<vid>/chunk_N/raw.txt and writes per-chunk pipeline outputs
to chunks/<vid>/chunk_N/. After this script completes, stitch_chunks.py
merges the per-chunk outputs into canonical lecture-level files.

Usage:
    python3 process_chunked_lecture.py --vid WhWf_cgsv0I
    python3 process_chunked_lecture.py --vid WhWf_cgsv0I --only-chunk 2
    python3 process_chunked_lecture.py --vid WhWf_cgsv0I --dry-run

The chunk-aware prompts tell the model:
  - This is chunk N of M of a longer lecture
  - Only chunk 1 should write a title block; chunks 2-M should not
  - Only chunk M should write a closing wrap-up
  - Section numbering should start at §1 in each chunk (the stitcher
    will renumber globally during merging)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    sys.exit(1)


MODEL = "claude-opus-4-7"
MAX_TOKENS = 32000

REFS_DIR = Path("pipeline_refs")
CHUNK_DIR = Path("chunks")

FILE_MARKER_RE = re.compile(
    r"<<<FILE:\s*(?P<name>[^>]+?)>>>\s*\n(?P<content>.*?)\n<<<END FILE>>>",
    re.DOTALL,
)


def parse_response(text: str) -> dict[str, str]:
    files = {}
    for m in FILE_MARKER_RE.finditer(text):
        files[m.group("name").strip()] = m.group("content")
    return files


def streamed_call(client: Anthropic, system_prompt: str, user_message: str) -> tuple[str, str]:
    """Returns (text, stop_reason)."""
    parts = []
    stop_reason = "unknown"
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
        try:
            final = stream.get_final_message()
            stop_reason = final.stop_reason or "unknown"
        except Exception:
            pass
    return "".join(parts), stop_reason


def load_conventions() -> str:
    return (REFS_DIR / "conventions.md").read_text(encoding="utf-8")


def load_cluster_names() -> list[str]:
    data = json.loads((REFS_DIR / "cases_aggregate_v2.json").read_text(encoding="utf-8"))
    return sorted({r["cluster_id"] for r in data if r.get("cluster_id")})


def load_worked_example_call1() -> str:
    we_dir = REFS_DIR / "worked_example"
    parts = []
    for src_name, display_name in [
        ("lec11_s1_layer2.md", "layer2.md"),
        ("lec11_s1_transformation_log.md", "transformation_log.md"),
    ]:
        p = we_dir / src_name
        if p.exists():
            parts.append(f"<<<FILE: {display_name}>>>\n{p.read_text(encoding='utf-8')}\n<<<END FILE>>>\n")
    return "\n".join(parts)


def load_worked_example_call2() -> str:
    we_dir = REFS_DIR / "worked_example"
    parts = []
    for src_name, display_name in [
        ("lec11_s1_layer3.md", "layer3.md"),
        ("lec11_s1_anchors.json", "anchors.json"),
        ("lec11_s1_editorial_register.md", "editorial_register.md"),
        ("lec11_s1_case_index.md", "case_index.md"),
    ]:
        p = we_dir / src_name
        if p.exists():
            parts.append(f"<<<FILE: {display_name}>>>\n{p.read_text(encoding='utf-8')}\n<<<END FILE>>>\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Chunk-aware system prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_CALL1_CHUNK = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

IMPORTANT: This is CHUNK {chunk_id} OF {n_chunks} of a longer lecture
that was split before pipeline processing because the model's effective
output ceiling could not accommodate the full lecture's output in a
single Call 2. Process this chunk as if it were a self-contained
recording, with these caveats:

  - The chunk's raw transcript starts at timestamp {start_seconds}s of
    the full lecture (not 00:00). Preserve the original timestamps;
    do NOT renumber them.
  - If chunk_id > 1, the first ~30 seconds of the chunk overlap with
    the previous chunk's end. Treat this as continuity context — don't
    duplicate content already at the end of the previous chunk's layer 2.
  - Section numbering: within this chunk, number sections starting at §1.
    The stitcher will renumber globally during merging.

OUTPUT FORMAT: three files delimited by markers. No text outside.

<<<FILE: layer2.md>>>
...
<<<END FILE>>>

<<<FILE: transformation_log.md>>>
...
<<<END FILE>>>

<<<FILE: metadata.json>>>
...
<<<END FILE>>>"""


SYSTEM_PROMPT_CALL2_CHUNK = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

IMPORTANT: This is CHUNK {chunk_id} OF {n_chunks} of a longer lecture
that was split before pipeline processing. Produce the four layer-3
files for this chunk only. Caveats:

  - DO NOT write an opening title block unless chunk_id == 1.
  - DO NOT write a closing wrap-up unless chunk_id == {n_chunks}.
  - Section numbering: within this chunk, sections are §1, §2, ...
    starting from §1. The stitcher will renumber globally.
  - The chunk's content may begin mid-thought (because of upstream
    chunking and overlap). Don't try to write an introduction for it.

OUTPUT FORMAT: four files delimited by markers. No text outside.

<<<FILE: layer3.md>>>
...
<<<END FILE>>>

<<<FILE: anchors.json>>>
...
<<<END FILE>>>

<<<FILE: editorial_register.md>>>
...
<<<END FILE>>>

<<<FILE: case_index.md>>>
...
<<<END FILE>>>"""


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------

def build_call1_message_chunk(
    vid: str,
    chunk_id: int,
    n_chunks: int,
    chunk_text: str,
    raw_sha: str,
    raw_line_count: int,
    raw_word_count: int,
    worked_example_call1: str,
    conventions: str,
    chunk_start_seconds: int,
    chunk_end_seconds: int,
) -> str:
    return f"""Produce layer 2, transformation log, and metadata for CHUNK {chunk_id}
of {n_chunks} of this Eagar lecture.

LECTURE METADATA:
- video_id: {vid}_chunk{chunk_id}
- original video_id: {vid}
- chunk: {chunk_id} of {n_chunks}
- chunk start: {chunk_start_seconds} seconds into full lecture
- chunk end: {chunk_end_seconds} seconds into full lecture
- raw_transcript_sha256_of_full_lecture: {raw_sha}
- chunk_raw_line_count: {raw_line_count}
- chunk_raw_word_count: {raw_word_count}
- pipeline_version: 2.0-chunked
- model: {MODEL}
- generated_at: {datetime.now(timezone.utc).isoformat()}

CONVENTION CATALOG:

{conventions}

WORKED EXAMPLE (lec11_s1 layer2.md and transformation_log.md):

{worked_example_call1}

RAW TRANSCRIPT FOR THIS CHUNK:

{chunk_text}

Produce three files (layer2.md, transformation_log.md, metadata.json).
Output only the file blocks, no other text. Note in metadata.json that
this is chunk {chunk_id} of {n_chunks}, with the chunk_id, n_chunks,
chunk_start_seconds, and chunk_end_seconds fields set as given."""


def build_call2_message_chunk(
    vid: str,
    chunk_id: int,
    n_chunks: int,
    layer2_text: str,
    worked_example_call2: str,
    conventions: str,
    cluster_names: list[str],
) -> str:
    cluster_block = "\n".join(f"- {name}" for name in cluster_names)
    return f"""Produce layer 3, anchors, editorial register, and case index for
CHUNK {chunk_id} of {n_chunks} of this Eagar lecture.

LECTURE METADATA:
- video_id: {vid}_chunk{chunk_id}
- original video_id: {vid}
- chunk: {chunk_id} of {n_chunks}

CANONICAL CASE CLUSTERS (use these names when a case matches; prefix
with "PROPOSED:" if you need to introduce a new case):

{cluster_block}

CONVENTION CATALOG:

{conventions}

WORKED EXAMPLE (lec11_s1 layer3.md, anchors.json, editorial_register.md,
case_index.md):

{worked_example_call2}

LAYER 2 INPUT FOR THIS CHUNK:

{layer2_text}

Produce four files. Output only the file blocks, no other text. Recall:
- No title block unless chunk_id == 1
- No closing wrap-up unless chunk_id == {n_chunks}
- Sections within this chunk number from §1"""


# ---------------------------------------------------------------------------
# Process one chunk
# ---------------------------------------------------------------------------

def process_chunk(client: Anthropic, vid: str, chunk_meta: dict, dry_run: bool = False) -> bool:
    chunk_id = chunk_meta["chunk_id"]
    n_chunks = chunk_meta["n_chunks"]
    chunk_dir = CHUNK_DIR / vid / f"chunk_{chunk_id}"
    raw_path = chunk_dir / "raw.txt"

    if not raw_path.exists():
        print(f"  FAIL chunk {chunk_id}: raw.txt missing")
        return False

    chunk_text = raw_path.read_text(encoding="utf-8")
    raw_sha = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
    line_count = chunk_text.count("\n")
    word_count = len(chunk_text.split())

    print(f"\n=== Chunk {chunk_id} of {n_chunks} ({word_count} words) ===")

    # --- Call 1 ---
    call1_files = ["layer2.md", "transformation_log.md", "metadata.json"]
    call1_complete = all((chunk_dir / f).exists() for f in call1_files)

    if call1_complete:
        print(f"  Call 1: already complete, skipping")
    else:
        conventions = load_conventions()
        worked_example_call1 = load_worked_example_call1()
        system_prompt = SYSTEM_PROMPT_CALL1_CHUNK.format(
            chunk_id=chunk_id, n_chunks=n_chunks,
            start_seconds=chunk_meta["start_seconds"],
        )
        user_message = build_call1_message_chunk(
            vid=vid,
            chunk_id=chunk_id,
            n_chunks=n_chunks,
            chunk_text=chunk_text,
            raw_sha=raw_sha,
            raw_line_count=line_count,
            raw_word_count=word_count,
            worked_example_call1=worked_example_call1,
            conventions=conventions,
            chunk_start_seconds=chunk_meta["start_seconds"],
            chunk_end_seconds=chunk_meta["end_seconds"],
        )
        print(f"  Call 1 prompt: {len(user_message):,} chars")

        if dry_run:
            print(f"  DRY RUN: would call API for Call 1")
        else:
            response, stop_reason = streamed_call(client, system_prompt, user_message)
            print(f"  Call 1 response: {len(response):,} chars, stop_reason={stop_reason}")
            files = parse_response(response)
            missing = [f for f in call1_files if f not in files]
            if missing:
                print(f"  Call 1 FAIL: missing {missing}")
                (chunk_dir / "_failed_call1_raw_response.txt").write_text(response, encoding="utf-8")
                return False
            for fname in call1_files:
                (chunk_dir / fname).write_text(files[fname], encoding="utf-8")
                print(f"    wrote {fname} ({len(files[fname]):,} chars)")

    # --- Call 2 ---
    call2_files = ["layer3.md", "anchors.json", "editorial_register.md", "case_index.md"]
    call2_complete = all((chunk_dir / f).exists() for f in call2_files)

    if call2_complete:
        print(f"  Call 2: already complete, skipping")
        return True

    layer2_path = chunk_dir / "layer2.md"
    if not layer2_path.exists():
        if dry_run:
            print(f"  Call 2: DRY RUN — layer2.md doesn't exist yet (would be produced by Call 1); skipping Call 2 dry-run")
            return True
        print(f"  Call 2 FAIL: layer2.md missing (Call 1 may have failed)")
        return False

    layer2_text = layer2_path.read_text(encoding="utf-8")
    cluster_names = load_cluster_names()
    worked_example_call2 = load_worked_example_call2()
    conventions = load_conventions()

    system_prompt = SYSTEM_PROMPT_CALL2_CHUNK.format(chunk_id=chunk_id, n_chunks=n_chunks)
    user_message = build_call2_message_chunk(
        vid=vid,
        chunk_id=chunk_id,
        n_chunks=n_chunks,
        layer2_text=layer2_text,
        worked_example_call2=worked_example_call2,
        conventions=conventions,
        cluster_names=cluster_names,
    )
    print(f"  Call 2 prompt: {len(user_message):,} chars")

    if dry_run:
        print(f"  DRY RUN: would call API for Call 2")
        return True

    response, stop_reason = streamed_call(client, system_prompt, user_message)
    print(f"  Call 2 response: {len(response):,} chars, stop_reason={stop_reason}")
    files = parse_response(response)
    missing = [f for f in call2_files if f not in files]
    if missing:
        print(f"  Call 2 FAIL: missing {missing}")
        (chunk_dir / "_failed_call2_raw_response.txt").write_text(response, encoding="utf-8")
        # Save whatever was parsed
        for fname, content in files.items():
            if fname in call2_files:
                (chunk_dir / fname).write_text(content, encoding="utf-8")
                print(f"    salvaged {fname} ({len(content):,} chars)")
        return False
    for fname in call2_files:
        (chunk_dir / fname).write_text(files[fname], encoding="utf-8")
        print(f"    wrote {fname} ({len(files[fname]):,} chars)")

    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vid", required=True, help="Video ID")
    parser.add_argument("--only-chunk", type=int, default=None, help="Process only chunk N")
    parser.add_argument("--dry-run", action="store_true", help="Don't call the API")
    args = parser.parse_args()

    manifest_path = CHUNK_DIR / args.vid / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} not found. Run chunk_lecture.py first.")
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chunks = manifest["chunks"]

    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = None if args.dry_run else Anthropic()

    target_chunks = chunks if args.only_chunk is None else [c for c in chunks if c["chunk_id"] == args.only_chunk]
    if not target_chunks:
        print(f"ERROR: chunk {args.only_chunk} not in manifest")
        sys.exit(1)

    for chunk_meta in target_chunks:
        ok = process_chunk(client, args.vid, chunk_meta, dry_run=args.dry_run)
        if not ok:
            print(f"\nChunk {chunk_meta['chunk_id']} failed. Investigate before continuing.")
            sys.exit(1)
        if not args.dry_run:
            time.sleep(1)

    print("\nDone. Now run: python3 stitch_chunks.py --vid", args.vid)


if __name__ == "__main__":
    main()
