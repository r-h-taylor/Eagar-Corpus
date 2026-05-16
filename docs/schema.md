# File-format schema

Per-lecture and corpus-wide file formats.

## Per-lecture directory: `corpus/lectures/<video_id>/`

Each lecture is identified by its YouTube `video_id`. Lectures contain
7 canonical files plus 1 optional file:

### `layer2.md`

Cleaned middle layer. Plain markdown. Each paragraph is prefixed with
an anchor of the form `` `§N.pM` `` (e.g., `` `§3.p4` ``) referring
to section N, paragraph M. Section headers are `## §N. <title> [mm:ss]`.

### `layer3.md`

Editorial layer. Same paragraph-anchor format as Layer 2. Self-
corrections are smoothed; discourse fillers cut; physical-object
teaching moves rendered as italicized stage directions in brackets;
captioner slips bracketed (`Gordon Ford [Forward]`).

### `case_index.md`

Substantive cases developed in the lecture, in the format:

```
### <Case name>
- **Anchor:** `§N.pM`–`§N.pM`
- **canonical_cluster_id:** "<cluster_id>"   or "PROPOSED: <name>"
- **Frame in this lecture:** <2-4 sentence narrative summary>
- **Materials/systems:** <list>
- **Era:** <when the case is historically situated>
- **Related clusters in canon:** <optional cross-references>
```

### `extended_case_references.md` (optional)

Brief mentions of canonical cases that did not warrant a full
`case_index.md` entry, identified by reconciliation pass against the
canon. Same field structure as `case_index.md` plus a `Quote (layer 3)`
field with verbatim text from the relevant Layer 3 paragraph.

### `editorial_register.md`

Per-section Layer 2 → Layer 3 editorial decisions. Documents every
soft reordering, every captioner correction flagged for review, every
factual gloss, every flagged-for-review item. For chunked lectures,
the register concatenates per-chunk entries with visible chunk
boundary markers.

### `transformation_log.md`

Per-paragraph Layer 1 → Layer 2 mechanical transformations: captioner
errors corrected silently, proper nouns capitalized, line breaks
joined, em-dashes inserted for false starts, cuts.

### `anchors.json`

Mapping from Layer 3 paragraph anchors to Layer 2 paragraph anchors,
typically a JSON object of the form:

```json
{
  "§N.pM": {"layer2_anchor": "§N.pM", "layer2_text_excerpt": "..."}
}
```

(Format may vary slightly for chunked lectures, where the
`anchors.json` reflects merged global anchors.)

### `metadata.json`

Per-lecture metadata. Required fields:

- `video_id` (string) — YouTube video ID
- `course` (string) — course name
- `course_number` (string, optional) — e.g., "3.371"
- `term` (string) — e.g., "Fall 2014"
- `video_title` (string) — full title from YouTube
- `lecture_number` (int, optional) — lecture N in sequence
- `lecture_total` (int, optional) — total lectures in series
- `raw_transcript_sha256` (string) — SHA-256 of source caption file
- `raw_transcript_word_count` (int)
- `raw_transcript_line_count` (int)
- `pipeline_version` (string) — e.g., "2.0" or "2.0-chunked"
- `model` (string) — model used for Layer 2/3 generation
- `generated_at` (ISO 8601 timestamp)
- `layer2_paragraph_count` (int)
- `cases_mentioned` (array of objects) — case extractions

Chunked-lecture metadata includes:

- `chunked: true`
- `n_chunks` (int)
- `chunk_overlap_seconds` (int)
- `chunks_summary` (array) — per-chunk metadata

## Corpus-wide files: `ontology/`

### `cases_aggregate_v2.json`

The canonical case canon. Array of objects, each with at minimum a
`cluster_id` field. Additional descriptive fields vary by entry.

### `reconciliation_report.json`

Audit log of the reconciliation pass. Includes per-cluster information:
keywords used for candidate generation, candidate count, confirmed
matches (with anchor and lecture), and skipped (ambiguous) candidates.

### `proposed_merge_suggestions.json`

Pass B output of reconciliation: for each PROPOSED cluster, the
candidate canonical clusters considered, and the model's merge
decision (merge target, "new_or_unsure," or "no_candidates").

## Citation conventions

See `docs/citation.md`.
