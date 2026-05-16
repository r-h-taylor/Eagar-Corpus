#!/usr/bin/env python3
"""
Eagar Corpus Pipeline Runner — v2 (two-call architecture)

Produces a three-layer searchable archive output for each Eagar lecture.
Reuses Lecture / load_corpus from analyze_eagar_corpus.py.

Architecture: two API calls per lecture.
  Call 1: layer2.md + transformation_log.md + metadata.json (mechanical cleanup)
  Call 2: layer3.md + anchors.json + editorial_register.md + case_index.md
          (editorial work; takes layer 2 as input)

If call 1 succeeds and call 2 fails, call 1's output is preserved on disk
and call 2 can be re-run. The script automatically resumes from wherever
each lecture left off.

Usage:
    # Test batch (5 lectures, sequential):
    python3 run_pipeline.py --mode test

    # Sequential full run (resumable):
    python3 run_pipeline.py --mode sequential --resume

Requires:
    pip install anthropic
    Env var: ANTHROPIC_API_KEY
    pipeline_refs/
        worked_example/   (six lec11_s1_*.{md,json} files)
        conventions.md
        cases_aggregate_v2.json
"""

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from analyze_eagar_corpus import Lecture, load_corpus

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-7"
MAX_TOKENS = 32000
PIPELINE_VERSION = "2.0"

CALL1_FILES = ["layer2.md", "transformation_log.md", "metadata.json"]
CALL2_FILES = ["layer3.md", "anchors.json", "editorial_register.md", "case_index.md"]
ALL_FILES = CALL1_FILES + CALL2_FILES

FILE_MARKER_RE = re.compile(
    r"<<<FILE:\s*(?P<name>[^>]+?)>>>\s*\n(?P<content>.*?)\n<<<END FILE>>>",
    re.DOTALL,
)

HTTP_TIMEOUT_SECONDS = 1800  # 30 min — accommodates long Opus streams


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_CALL1 = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce LAYER 2 (cleanup edit), the
transformation log, and the lecture metadata. Three files only.

Layer 2 is the cleaned middle layer: captioner errors corrected,
sentence boundaries inserted, paragraphs broken at natural pauses,
filler words lightly thinned, Tom's spoken slips of memory bracketed
(e.g. "Ford [Forward]"). NO editorial restructuring. NO removal of
self-corrections. NO cutting of pocket-patting or other in-the-moment
speech business. Layer 2 is allowed to read as Tom-thinking-aloud.

Each paragraph in layer 2 starts with a paragraph ID (`p1`, `p2`, ...)
and a timestamp anchor [MM:SS]. Paragraphs break at natural pauses
(typically 30 seconds to 2 minutes of speech).

You have been given a worked example: lecture -6n9y2szRqo §1. The
layer2.md in that example defines the standard. Match its dial.

OUTPUT FORMAT: three files delimited by markers. No text outside the
markers. No preambles or summaries.

<<<FILE: layer2.md>>>
...content...
<<<END FILE>>>

<<<FILE: transformation_log.md>>>
...
<<<END FILE>>>

<<<FILE: metadata.json>>>
...
<<<END FILE>>>"""


SYSTEM_PROMPT_CALL2 = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: take the LAYER 2 cleanup edit produced in the
previous step, and produce LAYER 3 (editorial edit), the anchors JSON,
the editorial register, and the per-lecture case index. Four files only.

Layer 3 is the readable edition. Section the lecture (typically 4-8
sections per 50-minute lecture — divide at natural teaching transitions:
new case introduced, topic pivot, resumption after Q&A, new visual aid).
Each section gets a title and a starting timestamp.

Within sections, paragraphs are anchored §N.pM. Student turns labeled
**Student:**. Physical-object teaching moves rendered as italicized
stage directions in brackets: *[Tom produces a pair of surgical
scissors.]*. Filler removed. Self-corrections smoothed. Pocket-patting
cut.

CRITICAL CONSTRAINTS (do not violate):
1. Do not add new sentences in Tom's voice. We cannot ratify them.
2. Do not reorder content across section boundaries. Soft reordering
   within a section is permitted, logged in editorial_register.md.
3. Do not merge cases Tom kept separate, or split cases he handled
   as one.
4. Captioner errors corrected silently. Tom's spoken slips of memory
   bracketed: Ford [Forward] on first occurrence per section,
   [Forward] alone thereafter.

THE PRINCIPLE for what to cut vs preserve:
Cut what Tom said because he was speaking in real time (false starts,
mid-sentence pivots, pocket-patting). Preserve what Tom said because
he was teaching (lateral asides, qualifications, "you knows" that
signal shared context, "okays" that close a thought).

SECTIONING:
Do not under-section. A 50-minute lecture should usually have 4-8
sections. Use the topic structure of the layer 2 to find natural
breaks. Each section should be 3-8 minutes of audio. A single-section
output for a long lecture is almost always wrong — look harder for
the teaching transitions.

ANCHORS.JSON SHAPE:
Use the multi-section shape from the worked example. Wrap in
{"lecture_id": "...", "sections": [{"section_id": "s1",
"section_title": "...", "section_timestamp_start": "MM:SS",
"anchors": [...]}, ...]}. Every §N.pM in layer 3 must appear exactly
once as an l3_id in anchors. Map each to one or more p_K from
layer 2 plus its timestamp range.

CASE INDEX:
Use canonical cluster_id names from the aggregate when matching.
Prefix new clusters with "PROPOSED:" — do not invent fake matches
to existing clusters.

You have been given the worked example: lecture -6n9y2szRqo §1.
Match the editorial dial of its layer3.md, anchors.json,
editorial_register.md, and case_index.md exactly.

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


def build_call1_message(
    lecture: Lecture,
    raw_text: str,
    raw_line_count: int,
    raw_word_count: int,
    raw_sha256: str,
    worked_example_call1: str,
    conventions: str,
) -> str:
    return f"""Produce layer 2, transformation log, and metadata for this Eagar lecture.

LECTURE METADATA:
- video_id: {lecture.video_id}
- course: {lecture.module_name}
- term: {lecture.year_label}
- video_title: {lecture.video_title}
- raw_transcript_sha256: {raw_sha256}
- raw_transcript_line_count: {raw_line_count}
- raw_transcript_word_count: {raw_word_count}
- pipeline_version: {PIPELINE_VERSION}
- model: {MODEL}
- generated_at: {datetime.now(timezone.utc).isoformat()}

CONVENTION CATALOG:

{conventions}

WORKED EXAMPLE (lec11_s1 layer2.md and transformation_log.md):

{worked_example_call1}

RAW TRANSCRIPT FOR THIS LECTURE:

{raw_text}

Produce three files (layer2.md, transformation_log.md, metadata.json).
Output only the file blocks, no other text."""


def build_call2_message(
    lecture: Lecture,
    layer2_text: str,
    worked_example_call2: str,
    conventions: str,
    cluster_names: list[str],
) -> str:
    cluster_block = "\n".join(f"- {name}" for name in cluster_names)
    return f"""Produce layer 3, anchors, editorial register, and case index for this Eagar lecture.

LECTURE METADATA:
- video_id: {lecture.video_id}
- course: {lecture.module_name}
- term: {lecture.year_label}
- video_title: {lecture.video_title}

CANONICAL CASE CLUSTERS (use these names when a case matches; prefix
with "PROPOSED:" if you need to introduce a new case):

{cluster_block}

CONVENTION CATALOG:

{conventions}

WORKED EXAMPLE (lec11_s1 layer3.md, anchors.json, editorial_register.md,
case_index.md):

{worked_example_call2}

LAYER 2 INPUT (produced in previous step):

{layer2_text}

Produce four files (layer3.md, anchors.json, editorial_register.md,
case_index.md). Output only the file blocks, no other text."""


# ---------------------------------------------------------------------------
# Reference loading
# ---------------------------------------------------------------------------

def load_worked_example(refs_dir: Path) -> tuple[str, str]:
    """Return (call1_block, call2_block) — concatenated file markers."""
    we_dir = refs_dir / "worked_example"
    if not we_dir.exists():
        raise FileNotFoundError(f"Missing worked example dir: {we_dir}")

    call1_map = {
        "lec11_s1_layer2.md": "layer2.md",
        "lec11_s1_transformation_log.md": "transformation_log.md",
    }
    call2_map = {
        "lec11_s1_layer3.md": "layer3.md",
        "lec11_s1_anchors.json": "anchors.json",
        "lec11_s1_editorial_register.md": "editorial_register.md",
        "lec11_s1_case_index.md": "case_index.md",
    }

    def build(file_map: dict[str, str]) -> str:
        parts = []
        for src, dst in file_map.items():
            p = we_dir / src
            if not p.exists():
                raise FileNotFoundError(f"Missing worked example file: {p}")
            parts.append(f"<<<FILE: {dst}>>>\n{p.read_text(encoding='utf-8')}\n<<<END FILE>>>")
        return "\n\n".join(parts)

    return build(call1_map), build(call2_map)


def load_conventions(refs_dir: Path) -> str:
    p = refs_dir / "conventions.md"
    if not p.exists():
        raise FileNotFoundError(f"Missing conventions file: {p}")
    return p.read_text(encoding="utf-8")


def load_cluster_names(refs_dir: Path) -> list[str]:
    p = refs_dir / "cases_aggregate_v2.json"
    if not p.exists():
        raise FileNotFoundError(f"Missing aggregate file: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return sorted({rec["cluster_id"] for rec in data if rec.get("cluster_id")})


# ---------------------------------------------------------------------------
# Response parsing and validation
# ---------------------------------------------------------------------------

def parse_response(text: str) -> dict[str, str]:
    files = {}
    for m in FILE_MARKER_RE.finditer(text):
        name = m.group("name").strip()
        content = m.group("content").strip()
        files[name] = content
    return files


def validate_call1(files: dict[str, str]) -> tuple[bool, list[str]]:
    errors = []
    missing = [f for f in CALL1_FILES if f not in files]
    if missing:
        errors.append(f"Missing files: {missing}")
        return False, errors
    try:
        json.loads(files["metadata.json"])
    except json.JSONDecodeError as e:
        errors.append(f"metadata.json invalid: {e}")
    if not re.search(r"`p\d+`", files["layer2.md"]):
        errors.append("layer2.md has no paragraph anchors (`pN`)")
    return len(errors) == 0, errors


def validate_call2(files: dict[str, str]) -> tuple[bool, list[str]]:
    errors = []
    missing = [f for f in CALL2_FILES if f not in files]
    if missing:
        errors.append(f"Missing files: {missing}")
        return False, errors
    try:
        anchors = json.loads(files["anchors.json"])
    except json.JSONDecodeError as e:
        errors.append(f"anchors.json invalid: {e}")
        return False, errors

    anchor_ids = set()
    if "sections" in anchors:
        for sec in anchors.get("sections", []):
            for a in sec.get("anchors", []):
                anchor_ids.add(a.get("l3_id"))
    elif "anchors" in anchors:
        for a in anchors.get("anchors", []):
            anchor_ids.add(a.get("l3_id"))
    l3_ids = set(re.findall(r"§\d+\.p\d+", files["layer3.md"]))
    missing_anchors = l3_ids - anchor_ids
    extra_anchors = anchor_ids - l3_ids
    if missing_anchors:
        errors.append(f"L3 paragraphs missing from anchors: {sorted(missing_anchors)[:5]}")
    if extra_anchors:
        errors.append(f"Anchors not in L3: {sorted(extra_anchors)[:5]}")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def raw_transcript_stats(lecture: Lecture) -> tuple[str, int, int, str]:
    raw_bytes = lecture.transcript_path.read_bytes()
    sha = hashlib.sha256(raw_bytes).hexdigest()
    raw_text = raw_bytes.decode("utf-8")
    line_count = raw_text.count("\n") + 1
    word_count = len(raw_text.split())
    return raw_text, line_count, word_count, sha


def output_dir_for(lecture: Lecture, output_root: Path) -> Path:
    return output_root / "v1" / "lectures" / lecture.video_id


def call1_complete(out_dir: Path) -> bool:
    return out_dir.exists() and all((out_dir / f).exists() for f in CALL1_FILES)


def all_complete(out_dir: Path) -> bool:
    return out_dir.exists() and all((out_dir / f).exists() for f in ALL_FILES)


def write_files(out_dir: Path, files: dict[str, str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (out_dir / name).write_text(content, encoding="utf-8")


def write_debug(out_dir: Path, raw_text: str, files: dict[str, str], stage: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"_raw_response_{stage}.txt").write_text(raw_text, encoding="utf-8")
    for name, content in files.items():
        (out_dir / f"_failed_{stage}_{name}").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def streamed_call(client: Anthropic, system_prompt: str, user_message: str) -> str:
    parts = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
    return "".join(parts)


def run_call1(
    client: Anthropic,
    lecture: Lecture,
    out_dir: Path,
    worked_example: str,
    conventions: str,
) -> tuple[bool, str]:
    try:
        raw_text, line_count, word_count, sha = raw_transcript_stats(lecture)
    except Exception as e:
        return False, f"read error: {e}"
    if not raw_text.strip():
        return False, "empty transcript"

    user_message = build_call1_message(
        lecture=lecture, raw_text=raw_text,
        raw_line_count=line_count, raw_word_count=word_count, raw_sha256=sha,
        worked_example_call1=worked_example, conventions=conventions,
    )
    try:
        text = streamed_call(client, SYSTEM_PROMPT_CALL1, user_message)
    except Exception as e:
        return False, f"call1 API failure: {e}"

    files = parse_response(text)
    ok, errs = validate_call1(files)
    if not ok:
        write_debug(out_dir, text, files, "call1")
        return False, f"call1 validation: {'; '.join(errs)}"
    write_files(out_dir, files)
    return True, ""


def run_call2(
    client: Anthropic,
    lecture: Lecture,
    out_dir: Path,
    worked_example: str,
    conventions: str,
    cluster_names: list[str],
) -> tuple[bool, str]:
    layer2_path = out_dir / "layer2.md"
    if not layer2_path.exists():
        return False, "call2 prerequisite missing: layer2.md"
    layer2_text = layer2_path.read_text(encoding="utf-8")

    user_message = build_call2_message(
        lecture=lecture, layer2_text=layer2_text,
        worked_example_call2=worked_example, conventions=conventions,
        cluster_names=cluster_names,
    )
    try:
        text = streamed_call(client, SYSTEM_PROMPT_CALL2, user_message)
    except Exception as e:
        return False, f"call2 API failure: {e}"

    files = parse_response(text)
    ok, errs = validate_call2(files)
    if not ok:
        write_debug(out_dir, text, files, "call2")
        return False, f"call2 validation: {'; '.join(errs)}"
    write_files(out_dir, files)
    return True, ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-dir", type=Path, default=Path("./eagar_corpus"))
    parser.add_argument("--output-dir", type=Path, default=Path("./output"))
    parser.add_argument("--refs-dir", type=Path, default=Path("./pipeline_refs"))
    parser.add_argument("--mode", choices=["test", "sequential"], default="test")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--test-n", type=int, default=5)
    parser.add_argument("--max-retries", type=int, default=1,
                        help="Retries per failed call (default 1 = up to 2 attempts).")
    args = parser.parse_args()

    print("Loading references...", flush=True)
    we_call1, we_call2 = load_worked_example(args.refs_dir)
    conventions = load_conventions(args.refs_dir)
    cluster_names = load_cluster_names(args.refs_dir)
    print(f"  Call 1 worked example: {len(we_call1):,} chars")
    print(f"  Call 2 worked example: {len(we_call2):,} chars")
    print(f"  Conventions: {len(conventions):,} chars")
    print(f"  Canonical case clusters: {len(cluster_names):,}")

    print("\nLoading corpus...", flush=True)
    lectures = load_corpus(args.corpus_dir, only_instructor="Eagar")
    print(f"  {len(lectures)} Eagar lectures found")

    if args.resume:
        before = len(lectures)
        lectures = [
            lec for lec in lectures
            if not all_complete(output_dir_for(lec, args.output_dir))
        ]
        print(f"  {before - len(lectures)} already fully complete (skipping)")
        print(f"  {len(lectures)} remaining (may include partial call-1-done)")

    if args.mode == "test":
        lectures = lectures[: args.test_n]
        print(f"\nTest mode: processing first {len(lectures)} lectures.")
    else:
        print(f"\nSequential mode: processing all {len(lectures)} lectures.")

    if not lectures:
        print("Nothing to do.")
        return

    client = Anthropic(timeout=HTTP_TIMEOUT_SECONDS)

    successes, partials, failures = 0, 0, []
    started_at = time.time()

    for i, lec in enumerate(lectures, 1):
        out_dir = output_dir_for(lec, args.output_dir)
        elapsed = time.time() - started_at
        print(
            f"\n[{i}/{len(lectures)}] {lec.video_id}  "
            f"({lec.module_name}, {lec.year_label})  "
            f"[elapsed {elapsed/60:.1f}m]",
            flush=True,
        )

        # Call 1 (skip if already done)
        if call1_complete(out_dir):
            print("  call 1: already complete, skipping")
            call1_ok = True
            err = ""
        else:
            call1_ok = False
            err = ""
            for attempt in range(1, args.max_retries + 2):
                ok, err = run_call1(client, lec, out_dir, we_call1, conventions)
                if ok:
                    print(f"  call 1: OK (attempt {attempt})")
                    call1_ok = True
                    break
                print(f"  call 1 attempt {attempt} failed: {err[:200]}")
                if attempt <= args.max_retries:
                    time.sleep(2 ** attempt)
            if not call1_ok:
                failures.append((lec.video_id, f"call1: {err}"))
                continue

        # Call 2
        call2_ok = False
        err = ""
        for attempt in range(1, args.max_retries + 2):
            ok, err = run_call2(
                client, lec, out_dir, we_call2, conventions, cluster_names
            )
            if ok:
                print(f"  call 2: OK (attempt {attempt})")
                call2_ok = True
                break
            print(f"  call 2 attempt {attempt} failed: {err[:200]}")
            if attempt <= args.max_retries:
                time.sleep(2 ** attempt)

        if call2_ok:
            successes += 1
        else:
            partials += 1
            failures.append((lec.video_id, f"call2: {err}"))

    elapsed = time.time() - started_at
    print(f"\n{'='*70}")
    print(f"Run complete in {elapsed/60:.1f} minutes")
    print(f"  Full successes: {successes}/{len(lectures)}")
    print(f"  Partial (call 1 done, call 2 failed): {partials}")
    print(f"  Total failures (no usable output): {len(failures) - partials}")
    if failures:
        log_path = args.output_dir / "v1" / f"failures_{int(time.time())}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            "\n".join(f"{vid}\t{err}" for vid, err in failures), encoding="utf-8"
        )
        print(f"\nFailures logged to: {log_path}")
        print("To retry partials (call 2 only), run again with --resume.")


if __name__ == "__main__":
    main()
