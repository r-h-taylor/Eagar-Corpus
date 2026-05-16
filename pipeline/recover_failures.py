#!/usr/bin/env python3
"""
Eagar Corpus Pipeline — Failure Recovery

Recovers the 9 failed lectures from the v2.0 pipeline run by making
focused, single-file API calls instead of the four-file Call 2 and
three-file Call 1 batches. Single-file outputs are well under any
effective token ceiling.

Modes:
  case-index    Regenerate ONLY case_index.md for a lecture that has
                layer3.md + editorial_register.md but no case_index.md
                (7 affected lectures).

  call1-finish  Regenerate metadata.json + transformation_log.md for
                a lecture whose Call 1 truncated after layer2.md
                (2 affected lectures). Each file is produced in its
                own focused API call.

Usage:
  python3 recover_failures.py --mode case-index --vid pq7RLDw6ijk
  python3 recover_failures.py --mode call1-finish --vid TRSZrx4_vPQ
  python3 recover_failures.py --mode all  # runs all 9 recoveries

  Add --dry-run to see what would be done without making API calls.
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
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-7"
MAX_TOKENS = 16000  # well under the ~22K effective ceiling
PIPELINE_VERSION = "2.0"

REFS_DIR = Path("pipeline_refs")
OUTPUT_DIR = Path("output/v1/lectures")
CORPUS_DIR = Path("eagar_corpus")

CASE_INDEX_LECTURES = [
    "TRSZrx4_vPQ",
    "pq7RLDw6ijk",
]

# Lectures that need editorial_register.md regenerated
# (truncation hit early enough that the register was never produced).
EDITORIAL_REGISTER_LECTURES = [
    "TRSZrx4_vPQ",
    "pq7RLDw6ijk",
]

CALL1_FINISH_LECTURES = [
    "TRSZrx4_vPQ",
    "WhWf_cgsv0I",
]


# ---------------------------------------------------------------------------
# File marker parsing (same as pipeline)
# ---------------------------------------------------------------------------

FILE_MARKER_RE = re.compile(
    r"<<<FILE:\s*(?P<name>[^>]+?)>>>\s*\n(?P<content>.*?)\n<<<END FILE>>>",
    re.DOTALL,
)


def parse_response(text: str) -> dict[str, str]:
    files = {}
    for m in FILE_MARKER_RE.finditer(text):
        files[m.group("name").strip()] = m.group("content")
    return files


# ---------------------------------------------------------------------------
# Reference loading
# ---------------------------------------------------------------------------

def load_cluster_names() -> list[str]:
    p = REFS_DIR / "cases_aggregate_v2.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return sorted({rec["cluster_id"] for rec in data if rec.get("cluster_id")})


def load_conventions() -> str:
    return (REFS_DIR / "conventions.md").read_text(encoding="utf-8")


def find_source_transcript(vid: str) -> Path:
    """Locate the source transcript file for a video id."""
    matches = list(CORPUS_DIR.rglob(f"*{vid}.txt"))
    matches = [p for p in matches if not p.name.endswith(".bak")]
    if not matches:
        raise FileNotFoundError(f"No source transcript found for {vid}")
    if len(matches) > 1:
        print(f"  WARN: multiple matches for {vid}, using {matches[0]}")
    return matches[0]


# ---------------------------------------------------------------------------
# API call
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


# ---------------------------------------------------------------------------
# case_index.md recovery
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_CASE_INDEX = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce ONLY the case_index.md file for one
lecture. The layer 3 markdown and editorial register have already been
generated; you are completing the case index that was truncated in the
original pipeline run.

Output exactly one file block: <<<FILE: case_index.md>>> ... <<<END FILE>>>
No other text before, between, or after."""


def build_case_index_message(
    vid: str,
    layer3_text: str,
    editorial_register_text: str,
    cluster_names: list[str],
    metadata: dict,
) -> str:
    cluster_block = "\n".join(f"- {name}" for name in cluster_names)

    course = metadata.get("course") or metadata.get("course_title_on_tape") or "unknown"
    term = metadata.get("term", "unknown")
    title = metadata.get("video_title", "unknown")
    lecture_num = metadata.get("lecture_number") or metadata.get("lecture_number_in_series")
    lecture_total = metadata.get("lecture_total") or metadata.get("lectures_in_series")

    return f"""Produce ONLY case_index.md for this Eagar lecture. The layer 3 and
editorial register are below for context; do not regenerate them.

LECTURE METADATA:
- video_id: {vid}
- course: {course}
- term: {term}
- video_title: {title}
- lecture number: {lecture_num} of {lecture_total}

CANONICAL CASE CLUSTERS (use these names when a case matches; prefix
with "PROPOSED:" if you need to introduce a new case):

{cluster_block}

LAYER 3 (already generated; reference only):

{layer3_text}

EDITORIAL REGISTER (already generated; reference only):

{editorial_register_text}

Produce ONLY case_index.md following the established format:

# Case Index — Lecture {vid} ({course}, {term}, session {lecture_num}/{lecture_total})

*Citation format: layer 3 paragraph anchor (e.g. `§1.p3`). Click-through reveals the corresponding layer 2 passage with timestamp range.*

[one or two sentence center-of-gravity statement identifying dominant cases]

## Major case: <name>   (if there is a clearly dominant case)

### <case name>
- **Anchor:** `§N.pM`–`§N.pM`
- **canonical_cluster_id:** "..." (match against the canonical list above, or prefix with PROPOSED: if new)
- **Frame in this lecture:** [2-4 sentence narrative summary]
- **Materials/systems:** [...]
- **Era:** [...]
- **Related clusters in canon:** [optional, only if applicable]

## Cases referenced in passing   (if applicable)

[same per-case structure as above]

## Figures referenced
- [pedagogically load-bearing numbers, dates, dollar amounts, percentages]

## Open questions
- [editorial notes for reconciliation, if any]

Output the case_index.md file in a single <<<FILE: case_index.md>>>
... <<<END FILE>>> block, with no other text."""


def recover_case_index(client: Anthropic, vid: str, dry_run: bool = False) -> bool:
    out_dir = OUTPUT_DIR / vid
    case_index_path = out_dir / "case_index.md"

    if case_index_path.exists():
        print(f"  SKIP {vid}: case_index.md already exists")
        return True

    layer3_path = out_dir / "layer3.md"
    register_path = out_dir / "editorial_register.md"
    metadata_path = out_dir / "metadata.json"

    for p in (layer3_path, register_path, metadata_path):
        if not p.exists():
            print(f"  FAIL {vid}: prerequisite missing: {p.name}")
            return False

    layer3_text = layer3_path.read_text(encoding="utf-8")
    register_text = register_path.read_text(encoding="utf-8")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    cluster_names = load_cluster_names()

    user_message = build_case_index_message(
        vid=vid,
        layer3_text=layer3_text,
        editorial_register_text=register_text,
        cluster_names=cluster_names,
        metadata=metadata,
    )

    print(f"  prompt size: {len(user_message):,} chars")

    if dry_run:
        print(f"  DRY RUN: would call API for {vid}")
        return True

    try:
        response = streamed_call(client, SYSTEM_PROMPT_CASE_INDEX, user_message)
    except Exception as e:
        print(f"  FAIL {vid}: API error: {e}")
        return False

    files = parse_response(response)
    if "case_index.md" not in files:
        print(f"  FAIL {vid}: case_index.md not in response (got: {list(files.keys())})")
        debug_path = out_dir / "_recovery_response.txt"
        debug_path.write_text(response, encoding="utf-8")
        print(f"  raw response saved to {debug_path}")
        return False

    content = files["case_index.md"]
    case_index_path.write_text(content, encoding="utf-8")
    print(f"  OK {vid}: wrote case_index.md ({len(content):,} chars)")
    return True


# ---------------------------------------------------------------------------
# editorial_register.md recovery (retrospective)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_EDITORIAL_REGISTER = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce ONLY editorial_register.md
RETROSPECTIVELY by comparing the existing layer 2 (cleaned middle
layer) to the existing layer 3 (editorial layer). The original
pipeline call truncated before this file was generated. Document the
editorial moves visible in the layer 3 by diffing against layer 2.

Output exactly one file block: <<<FILE: editorial_register.md>>>
... <<<END FILE>>>. No other text before, between, or after.

Important caveat: this register is generated retrospectively, not
contemporaneously with the editing decisions. Note this in the
register's preamble so readers understand the file's provenance."""


# ---------------------------------------------------------------------------
# layer3-only: generate just layer3.md from layer2.md
# anchors-only: generate just anchors.json from layer3.md
#
# These two replace the earlier call2-start mode (which produced both in
# one call). Splitting them halves each call's expected output and stays
# well under the truncation ceiling, even for long lectures.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_LAYER3 = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce ONLY layer3.md for one lecture. The
anchors.json, editorial_register.md, and case_index.md will be produced
in separate focused calls.

Output exactly one file block: <<<FILE: layer3.md>>> ... <<<END FILE>>>
No other text before, between, or after."""


SYSTEM_PROMPT_ANCHORS = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce ONLY anchors.json for one lecture.
Given the layer 3 markdown with §N.pM paragraph anchors, generate the
anchors.json file mapping each anchor to its corresponding layer 2
paragraph.

Output exactly one file block: <<<FILE: anchors.json>>> ... <<<END FILE>>>
No other text before, between, or after."""


def build_layer3_message(
    vid: str,
    layer2_text: str,
    worked_example_layer3: str,
    conventions: str,
    metadata: dict,
) -> str:
    course = metadata.get("course") or metadata.get("course_title_on_tape") or "unknown"
    term = metadata.get("term", "unknown")
    title = metadata.get("video_title", "unknown")

    return f"""Produce ONLY layer3.md for this Eagar lecture. The anchors,
editorial_register, and case_index will be produced in separate focused
calls; do not produce them here.

LECTURE METADATA:
- video_id: {vid}
- course: {course}
- term: {term}
- video_title: {title}

CONVENTION CATALOG:

{conventions}

WORKED EXAMPLE (lec11_s1 layer3.md only):

{worked_example_layer3}

LAYER 2 INPUT (produced in previous pipeline step; may be partial if
the source Call 1 itself truncated):

{layer2_text}

Note: if the layer 2 above ends abruptly (mid-sentence or mid-section),
that reflects truncation in the upstream pipeline run. Produce layer3
for whatever content is in layer 2; do not invent material not present
in layer 2. If the lecture ends mid-thought, end the layer 3
accordingly and add a brief editorial note in the closing paragraph
flagging the truncation.

Output one file (layer3.md). No other text."""


def build_anchors_message(
    vid: str,
    layer2_text: str,
    layer3_text: str,
    worked_example_anchors: str,
) -> str:
    return f"""Produce ONLY anchors.json for this Eagar lecture. The file maps
each §N.pM paragraph anchor in layer 3 to its corresponding layer 2
paragraph.

LECTURE: {vid}

WORKED EXAMPLE (lec11_s1 anchors.json):

{worked_example_anchors}

LAYER 2 INPUT:

{layer2_text}

LAYER 3 INPUT (the file we are anchoring against):

{layer3_text}

Output one file (anchors.json). No other text."""


def _load_worked_example_part(filename: str) -> str:
    """Load a single file from pipeline_refs/worked_example/ and return it
    formatted as a <<<FILE: ...>>> block."""
    we_dir = REFS_DIR / "worked_example"
    file_map = {
        "lec11_s1_layer3.md": "layer3.md",
        "lec11_s1_anchors.json": "anchors.json",
        "lec11_s1_editorial_register.md": "editorial_register.md",
        "lec11_s1_case_index.md": "case_index.md",
    }
    p = we_dir / filename
    if not p.exists():
        return ""
    display_name = file_map.get(filename, filename)
    return f"<<<FILE: {display_name}>>>\n{p.read_text(encoding='utf-8')}\n<<<END FILE>>>\n"


def recover_layer3(client: Anthropic, vid: str, dry_run: bool = False) -> bool:
    out_dir = OUTPUT_DIR / vid
    layer3_path = out_dir / "layer3.md"

    if layer3_path.exists():
        print(f"  SKIP {vid}: layer3.md already exists")
        return True

    layer2_path = out_dir / "layer2.md"
    metadata_path = out_dir / "metadata.json"

    for p in (layer2_path, metadata_path):
        if not p.exists():
            print(f"  FAIL {vid}: prerequisite missing: {p.name}")
            return False

    layer2_text = layer2_path.read_text(encoding="utf-8")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    worked_example = _load_worked_example_part("lec11_s1_layer3.md")
    conventions = load_conventions()

    user_message = build_layer3_message(
        vid=vid,
        layer2_text=layer2_text,
        worked_example_layer3=worked_example,
        conventions=conventions,
        metadata=metadata,
    )

    print(f"  prompt size: {len(user_message):,} chars")

    if dry_run:
        print(f"  DRY RUN: would call API for {vid} layer3")
        return True

    try:
        response = streamed_call(client, SYSTEM_PROMPT_LAYER3, user_message)
    except Exception as e:
        print(f"  FAIL {vid}: API error: {e}")
        return False

    files = parse_response(response)
    if "layer3.md" not in files:
        print(f"  FAIL {vid}: layer3.md not in response (got: {list(files.keys())})")
        (out_dir / "_recovery_response_layer3.txt").write_text(response, encoding="utf-8")
        return False

    content = files["layer3.md"]
    layer3_path.write_text(content, encoding="utf-8")
    print(f"  OK wrote layer3.md ({len(content):,} chars)")
    return True


def recover_anchors(client: Anthropic, vid: str, dry_run: bool = False) -> bool:
    out_dir = OUTPUT_DIR / vid
    anchors_path = out_dir / "anchors.json"

    if anchors_path.exists():
        print(f"  SKIP {vid}: anchors.json already exists")
        return True

    layer2_path = out_dir / "layer2.md"
    layer3_path = out_dir / "layer3.md"

    for p in (layer2_path, layer3_path):
        if not p.exists():
            print(f"  FAIL {vid}: prerequisite missing: {p.name}")
            return False

    layer2_text = layer2_path.read_text(encoding="utf-8")
    layer3_text = layer3_path.read_text(encoding="utf-8")
    worked_example = _load_worked_example_part("lec11_s1_anchors.json")

    user_message = build_anchors_message(
        vid=vid,
        layer2_text=layer2_text,
        layer3_text=layer3_text,
        worked_example_anchors=worked_example,
    )

    print(f"  prompt size: {len(user_message):,} chars")

    if dry_run:
        print(f"  DRY RUN: would call API for {vid} anchors")
        return True

    try:
        response = streamed_call(client, SYSTEM_PROMPT_ANCHORS, user_message)
    except Exception as e:
        print(f"  FAIL {vid}: API error: {e}")
        return False

    files = parse_response(response)
    if "anchors.json" not in files:
        print(f"  FAIL {vid}: anchors.json not in response (got: {list(files.keys())})")
        (out_dir / "_recovery_response_anchors.txt").write_text(response, encoding="utf-8")
        return False

    content = files["anchors.json"]
    anchors_path.write_text(content, encoding="utf-8")
    print(f"  OK wrote anchors.json ({len(content):,} chars)")
    return True


def build_editorial_register_message(
    vid: str,
    layer2_text: str,
    layer3_text: str,
    conventions: str,
    metadata: dict,
) -> str:
    course = metadata.get("course") or metadata.get("course_title_on_tape") or "unknown"
    term = metadata.get("term", "unknown")
    title = metadata.get("video_title", "unknown")
    lecture_num = metadata.get("lecture_number") or metadata.get("lecture_number_in_series")

    return f"""Produce ONLY editorial_register.md for this Eagar lecture by
retrospectively comparing layer 3 to layer 2.

LECTURE METADATA:
- video_id: {vid}
- course: {course}
- term: {term}
- video_title: {title}
- lecture number: {lecture_num}

CONVENTIONS (Layer 2 -> Layer 3 editorial rules):

{conventions}

LAYER 2 (cleaned middle layer; input to Layer 3 editing):

{layer2_text}

LAYER 3 (editorial layer; what was produced):

{layer3_text}

Produce editorial_register.md following the established format for
the corpus. The register documents:

1. **Preamble:** state that this register is generated RETROSPECTIVELY
   because the original pipeline run truncated before producing it.
   The editorial moves logged here are reconstructed from diffing
   layer 3 against layer 2, not recorded contemporaneously.

2. **Conventions applied** — the layer-3 conventions (numbered list,
   same as the worked example).

3. **Per-section notes** — for each §N in layer 3, list the editorial
   moves observable by comparing to layer 2:
   - Student turns labeled
   - Self-corrections smoothed
   - Discourse fillers cut
   - Stage directions inserted
   - Captioner errors corrected silently
   - Tom's slips bracketed
   - Soft reorderings (within paragraph or section)

4. **Soft reorderings logged** — table of any across-paragraph moves.

5. **Flags for human review** — borderline editorial choices or
   factual issues.

6. **Decisions NOT permitted at layer 3 (constitutional constraint)**
   — standard closing block (see worked example).

Output as one <<<FILE: editorial_register.md>>> ... <<<END FILE>>> block."""


def recover_editorial_register(client: Anthropic, vid: str, dry_run: bool = False) -> bool:
    out_dir = OUTPUT_DIR / vid
    register_path = out_dir / "editorial_register.md"

    if register_path.exists():
        print(f"  SKIP {vid}: editorial_register.md already exists")
        return True

    layer2_path = out_dir / "layer2.md"
    layer3_path = out_dir / "layer3.md"
    metadata_path = out_dir / "metadata.json"

    for p in (layer2_path, layer3_path, metadata_path):
        if not p.exists():
            print(f"  FAIL {vid}: prerequisite missing: {p.name}")
            return False

    layer2_text = layer2_path.read_text(encoding="utf-8")
    layer3_text = layer3_path.read_text(encoding="utf-8")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    conventions = load_conventions()

    user_message = build_editorial_register_message(
        vid=vid,
        layer2_text=layer2_text,
        layer3_text=layer3_text,
        conventions=conventions,
        metadata=metadata,
    )

    print(f"  prompt size: {len(user_message):,} chars")

    if dry_run:
        print(f"  DRY RUN: would call API for {vid} editorial_register.md")
        return True

    try:
        response = streamed_call(client, SYSTEM_PROMPT_EDITORIAL_REGISTER, user_message)
    except Exception as e:
        print(f"  FAIL {vid}: API error: {e}")
        return False

    files = parse_response(response)
    if "editorial_register.md" not in files:
        print(f"  FAIL {vid}: editorial_register.md not in response (got: {list(files.keys())})")
        (out_dir / "_recovery_response_register.txt").write_text(response, encoding="utf-8")
        return False

    content = files["editorial_register.md"]
    register_path.write_text(content, encoding="utf-8")
    print(f"  OK {vid}: wrote editorial_register.md ({len(content):,} chars)")
    return True


# ---------------------------------------------------------------------------
# Call 1 finish (metadata.json + transformation_log.md)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_METADATA = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce ONLY the metadata.json file for one
lecture. The layer 2 markdown has already been generated (possibly
truncated). You are filling in the missing metadata that was lost when
the original Call 1 hit its output ceiling.

Output exactly one file block: <<<FILE: metadata.json>>> ... <<<END FILE>>>
No other text before, between, or after."""


SYSTEM_PROMPT_TRANSFORMATION_LOG = """You are the editorial assistant for a three-layer searchable archive of
Prof. Thomas W. Eagar's recorded lectures, MIT (2011-2022). Tom Eagar
died Oct 9, 2022. The editor is his former postdoc Richard H. Taylor.

YOUR TASK ON THIS CALL: produce ONLY the transformation_log.md file
documenting the Layer 1 -> Layer 2 transformations applied to one
lecture. The layer 2 has already been generated; document its
editorial decisions retrospectively from comparing it to the raw
transcript provided.

Output exactly one file block: <<<FILE: transformation_log.md>>>
... <<<END FILE>>>. No other text before, between, or after."""


def lecture_title_from_filename(transcript_path: Path) -> dict:
    """Parse course/term/lecture-number info from the transcript filename.

    Filename format example:
      02__3.371_Materials_Processing_and_Casting_-_Summer_2011__2_7__TRSZrx4_vPQ.txt
    Parent dir example:
      Eagar__Casting__Summer_2011
    """
    stem = transcript_path.stem  # without .txt
    parent_name = transcript_path.parent.name

    # Parse parent: Eagar__<Course>__<Term>
    course = "unknown"
    term = "unknown"
    parent_parts = parent_name.split("__")
    if len(parent_parts) >= 3:
        course = parent_parts[1].replace("_", " ")
        term = parent_parts[2].replace("_", " ")

    # Parse stem for lecture number and total
    # Looking for pattern like __N_M__ where N is lecture, M is total
    lec_num = None
    lec_total = None
    m = re.search(r"__(\d+)_(\d+)__", stem)
    if m:
        lec_num = int(m.group(1))
        lec_total = int(m.group(2))

    # Extract the human-readable video title (between the leading NN__ and the trailing __vid)
    # Example stem: 02__3.371_Materials_Processing_and_Casting_-_Summer_2011__2_7__TRSZrx4_vPQ
    video_title = stem
    # Drop leading "NN__"
    video_title = re.sub(r"^\d+__", "", video_title)
    # Drop trailing "__<videoid>"
    video_title = re.sub(r"__[A-Za-z0-9_-]+$", "", video_title)
    video_title = video_title.replace("_", " ")

    return {
        "course": course,
        "term": term,
        "lecture_number": lec_num,
        "lecture_total": lec_total,
        "video_title": video_title,
    }


def raw_transcript_stats(transcript_path: Path) -> tuple[str, int, int, str]:
    """Return (raw_text, line_count, word_count, sha256)."""
    text = transcript_path.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    word_count = len(text.split())
    return text, line_count, word_count, sha


def build_metadata_message(
    vid: str,
    layer2_text: str,
    raw_text: str,
    raw_stats: dict,
    parsed_title: dict,
) -> str:
    return f"""Produce ONLY metadata.json for this Eagar lecture. The layer 2 markdown
and raw transcript are provided below; produce a structured metadata
record summarizing what is in them.

LECTURE BASICS (extracted from filename — refine as needed):
- video_id: {vid}
- course: {parsed_title['course']}
- term: {parsed_title['term']}
- lecture_number: {parsed_title['lecture_number']}
- lecture_total: {parsed_title['lecture_total']}
- video_title: {parsed_title['video_title']}

RAW TRANSCRIPT STATS:
- sha256: {raw_stats['sha256']}
- line_count: {raw_stats['line_count']}
- word_count: {raw_stats['word_count']}

NOTE: The original Call 1 truncated. The layer 2 below may be partial —
in particular, the *end* of the lecture may not appear in layer 2 even
though the raw transcript has it. Use the raw transcript for the
authoritative count of paragraphs / time / cases, and note in
metadata.json that layer2 is partial.

RAW TRANSCRIPT (truncated to last 8000 chars for context):

{raw_text[-8000:]}

LAYER 2 (possibly truncated):

{layer2_text}

Output metadata.json with these required fields:
- video_id
- course
- course_number (if known; "3.371" for most)
- course_title_on_tape (the official MIT course title)
- term
- video_title
- lecture_number
- lecture_total
- lecture_role (e.g. "session 2 of 7", "opening lecture", "final session")
- raw_transcript_sha256
- raw_transcript_line_count
- raw_transcript_word_count
- raw_transcript_duration_approx_seconds (estimate from raw, if timestamps available)
- pipeline_version: "2.0"
- model: "claude-opus-4-7"
- generated_at (ISO 8601 timestamp, UTC, current time)
- layer2_paragraph_count (count the §N.pM markers in the layer 2 above)
- layer2_partial (boolean — true if layer2 looks truncated)
- layer2_starts_at (timestamp from first paragraph)
- layer2_ends_at (timestamp from last paragraph)
- cases_mentioned (array of case objects: {{name, type, people, institutions, moral}})
- flags_for_editor (array; include note that layer2 is partial due to original Call 1 truncation)
- section_count_estimate_for_layer3 (your best guess from the layer 2 content)
- notes (one sentence summary of the lecture)

Output as one <<<FILE: metadata.json>>> ... <<<END FILE>>> block."""


def build_transformation_log_message(
    vid: str,
    layer2_text: str,
    raw_text: str,
    conventions: str,
) -> str:
    return f"""Produce ONLY transformation_log.md for this Eagar lecture. Document
the Layer 1 -> Layer 2 mechanical transformations retrospectively by
comparing the raw transcript to the layer 2 markdown.

LECTURE: {vid}

CONVENTIONS (Layer 1 -> Layer 2 rules):

{conventions}

RAW TRANSCRIPT (first 12000 chars):

{raw_text[:12000]}

LAYER 2 (cleaned middle layer; may be partial):

{layer2_text}

Produce transformation_log.md documenting:
- Global rules applied (line-break joining, sentence boundary insertion,
  captioner errors corrected silently, paragraph break logic, what was
  preserved as-is)
- Per-paragraph notes (per §N.pM in layer 2) listing specific
  captioner corrections, proper-noun capitalizations, em-dash insertions
  for false starts, etc. — drawn from comparing raw to layer 2.
- Cut entirely (anything from raw that was dropped in layer 2)
- Captioner errors flagged for review (anything ambiguous, marked [sic] in layer 2)
- Tom's spoken slips of memory (factual errors Tom made; preserved per
  Convention §10)
- Note on lecture structure (if layer 2 is partial, document that the
  original Call 1 truncated and the layer 2 ends mid-lecture)

Use the same format as a typical pipeline transformation_log.md.
Output as one <<<FILE: transformation_log.md>>> ... <<<END FILE>>> block."""


def recover_call1_finish(client: Anthropic, vid: str, dry_run: bool = False) -> bool:
    """Generate metadata.json and transformation_log.md for a Call 1 truncation."""
    out_dir = OUTPUT_DIR / vid

    # The truncated layer2 is in _failed_call1_layer2.md
    failed_layer2 = out_dir / "_failed_call1_layer2.md"
    canonical_layer2 = out_dir / "layer2.md"

    if canonical_layer2.exists():
        layer2_path = canonical_layer2
    elif failed_layer2.exists():
        layer2_path = failed_layer2
        print(f"  using _failed_call1_layer2.md as layer 2 input")
    else:
        print(f"  FAIL {vid}: no layer 2 source found")
        return False

    layer2_text = layer2_path.read_text(encoding="utf-8")

    # Promote layer2 to canonical if not already
    if not canonical_layer2.exists():
        canonical_layer2.write_text(layer2_text, encoding="utf-8")
        print(f"  promoted _failed_call1_layer2.md -> layer2.md")

    try:
        transcript_path = find_source_transcript(vid)
    except FileNotFoundError as e:
        print(f"  FAIL {vid}: {e}")
        return False

    raw_text, line_count, word_count, sha = raw_transcript_stats(transcript_path)
    raw_stats = {
        "sha256": sha,
        "line_count": line_count,
        "word_count": word_count,
    }
    parsed_title = lecture_title_from_filename(transcript_path)

    success = True

    # --- metadata.json ---
    metadata_path = out_dir / "metadata.json"
    if metadata_path.exists():
        print(f"  SKIP metadata.json (already exists)")
    else:
        user_message = build_metadata_message(
            vid=vid,
            layer2_text=layer2_text,
            raw_text=raw_text,
            raw_stats=raw_stats,
            parsed_title=parsed_title,
        )
        print(f"  metadata prompt size: {len(user_message):,} chars")
        if dry_run:
            print(f"  DRY RUN: would call API for metadata.json")
        else:
            try:
                response = streamed_call(client, SYSTEM_PROMPT_METADATA, user_message)
            except Exception as e:
                print(f"  FAIL metadata.json: API error: {e}")
                success = False
                response = None
            if response is not None:
                files = parse_response(response)
                if "metadata.json" not in files:
                    print(f"  FAIL metadata.json: not in response (got: {list(files.keys())})")
                    (out_dir / "_recovery_response_metadata.txt").write_text(response, encoding="utf-8")
                    success = False
                else:
                    metadata_path.write_text(files["metadata.json"], encoding="utf-8")
                    print(f"  OK wrote metadata.json ({len(files['metadata.json']):,} chars)")

    # --- transformation_log.md ---
    log_path = out_dir / "transformation_log.md"
    if log_path.exists():
        print(f"  SKIP transformation_log.md (already exists)")
    else:
        conventions = load_conventions()
        user_message = build_transformation_log_message(
            vid=vid,
            layer2_text=layer2_text,
            raw_text=raw_text,
            conventions=conventions,
        )
        print(f"  transformation_log prompt size: {len(user_message):,} chars")
        if dry_run:
            print(f"  DRY RUN: would call API for transformation_log.md")
        else:
            try:
                response = streamed_call(client, SYSTEM_PROMPT_TRANSFORMATION_LOG, user_message)
            except Exception as e:
                print(f"  FAIL transformation_log.md: API error: {e}")
                success = False
                response = None
            if response is not None:
                files = parse_response(response)
                if "transformation_log.md" not in files:
                    print(f"  FAIL transformation_log.md: not in response (got: {list(files.keys())})")
                    (out_dir / "_recovery_response_log.txt").write_text(response, encoding="utf-8")
                    success = False
                else:
                    log_path.write_text(files["transformation_log.md"], encoding="utf-8")
                    print(f"  OK wrote transformation_log.md ({len(files['transformation_log.md']):,} chars)")

    return success


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode",
        choices=["case-index", "editorial-register", "layer3-only", "anchors-only", "call1-finish", "all"],
        required=True)
    parser.add_argument("--vid", help="Video ID (omit for --mode all)")
    parser.add_argument("--dry-run", action="store_true", help="Don't call the API")
    args = parser.parse_args()

    if args.mode != "all" and not args.vid:
        print("ERROR: --vid required for individual modes")
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY") and not args.dry_run:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = None if args.dry_run else Anthropic()

    if args.mode == "case-index":
        print(f"\nRecovering case_index.md for {args.vid}")
        recover_case_index(client, args.vid, dry_run=args.dry_run)

    elif args.mode == "editorial-register":
        print(f"\nRecovering editorial_register.md for {args.vid}")
        recover_editorial_register(client, args.vid, dry_run=args.dry_run)

    elif args.mode == "layer3-only":
        print(f"\nRecovering layer3.md for {args.vid}")
        recover_layer3(client, args.vid, dry_run=args.dry_run)

    elif args.mode == "anchors-only":
        print(f"\nRecovering anchors.json for {args.vid}")
        recover_anchors(client, args.vid, dry_run=args.dry_run)

    elif args.mode == "call1-finish":
        print(f"\nRecovering Call 1 files for {args.vid}")
        recover_call1_finish(client, args.vid, dry_run=args.dry_run)

    elif args.mode == "all":
        print(f"\n=== EDITORIAL-REGISTER RECOVERIES ({len(EDITORIAL_REGISTER_LECTURES)} lectures) ===\n")
        for vid in EDITORIAL_REGISTER_LECTURES:
            print(f"\n[{vid}]")
            recover_editorial_register(client, vid, dry_run=args.dry_run)
            time.sleep(1)

        print(f"\n=== CASE-INDEX RECOVERIES ({len(CASE_INDEX_LECTURES)} lectures) ===\n")
        for vid in CASE_INDEX_LECTURES:
            print(f"\n[{vid}]")
            recover_case_index(client, vid, dry_run=args.dry_run)
            time.sleep(1)  # gentle pacing

        print(f"\n=== CALL-1 FINISH RECOVERIES ({len(CALL1_FINISH_LECTURES)} lectures) ===\n")
        for vid in CALL1_FINISH_LECTURES:
            print(f"\n[{vid}]")
            recover_call1_finish(client, vid, dry_run=args.dry_run)
            time.sleep(1)

        print("\n=== DONE ===")


if __name__ == "__main__":
    main()
