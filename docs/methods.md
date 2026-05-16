# Methods

This document describes the build pipeline that produced the Eagar
Corpus from the source YouTube auto-captions.

## The three-layer architecture

The corpus is organized as three increasingly edited views of the same
lecture:

**Layer 1 — raw transcript.** YouTube's auto-generated captions,
fetched from the public lectures on `eagar.mit.edu`. Each line is a
captioner-decided fragment, prefixed with a timestamp marker like
`[mm:ss]`. Layer 1 is *not redistributed* with this corpus (see
README); its SHA-256 hash is recorded in each lecture's `metadata.json`
so a reconstructed Layer 1 can be verified.

**Layer 2 — cleaned middle layer.** Auto-captioner line breaks joined
into continuous sentences; sentence boundaries and capitalization
inserted; proper nouns capitalized; captioner-misrecognized words
corrected silently where unambiguous (e.g., "hat roll" → "hot roll");
captioner-stutters collapsed. Layer 2 is the *citable, machine-readable
substrate* of the corpus and is the layer to which Layer 3's editorial
anchors point.

**Layer 3 — editorial layer.** Paragraph-anchored (`§N.pM` citation
form), Tom's self-corrections smoothed to corrected form, physical-
object teaching moves rendered as italicized stage directions (e.g.,
*[Tom passes a galvanized reinforcing bar.]*), discourse fillers
removed except where they invoke shared context, soft reorderings
within paragraph permitted where they aid readability, captioner
slip-of-the-tongue moments bracketed (e.g., "Gordon Ford [Forward]")
on first occurrence per section.

Editorial constraints at Layer 3 (constitutional, never violated):

- No new sentences added in Tom's voice.
- No reordering of content across section boundaries.
- No merging of cases Tom kept separate, nor splitting of cases he
  handled as one.
- No removal of factual errors Tom made on tape. (Captioner errors are
  silently corrected; Tom's slips of the tongue are bracketed; Tom's
  genuine misstatements are preserved and footnoted in Layer 3 only
  when they would actively mislead a reader.)

## The build pipeline

The pipeline is implemented in `pipeline/run_pipeline.py` and uses
Anthropic Claude Opus 4.7 to produce Layers 2 and 3 from the raw
captions. The pipeline is anchored to a hand-edited worked example —
the first section of lecture `-6n9y2szRqo` (3.371 Structural Materials
Selection, Fall 2014, lecture 11/13) — which defines the editorial
standard the model is instructed to match. The convention catalog
(`pipeline/pipeline_refs/conventions.md`) specifies the mechanical
rules; the worked example serves as the curatorial reference.

Each lecture passes through two API calls:

**Call 1 — produces:** `layer2.md`, `transformation_log.md`,
`metadata.json`. The transformation log records every captioner-error
correction made during the Layer 1 → Layer 2 cleanup.

**Call 2 — produces:** `layer3.md`, `editorial_register.md`,
`anchors.json`, `case_index.md`. The editorial register records every
Layer 2 → Layer 3 decision that was *not* purely mechanical, with the
specific rationale for any soft reordering or contextual gloss.

## Recovery and chunking for long lectures

The model's effective output ceiling caused two failure modes for
unusually long lectures.

**Recovery of partial Call 2 output.** When Call 2 hit its output
limit before producing all four files, the recovery pipeline
(`pipeline/recover_failures.py`) generates the missing files via
focused single-file API calls, each consuming only what is needed for
that file (e.g., layer 3 + register as input for `case_index.md`).
Eight lectures in v1.0.0 were recovered this way.

**Chunk-and-stitch for very long lectures.** Two lectures
(`WhWf_cgsv0I` and `TOum2TQZu_M`, both Casting Summer 2011) exceeded
the output ceiling at multiple pipeline stages. These were processed
via `pipeline/chunk_lecture.py` → `process_chunked_lecture.py` →
`stitch_chunks.py`: the source transcripts were split into four chunks
each (30-second overlaps), each chunk independently run through Calls
1 and 2 with chunk-aware prompts, then the stitcher merged outputs
back into canonical lecture-level files (global section
renumbering, anchor remapping, case-index deduplication, editorial-
register concatenation with visible chunk boundaries for human
editorial review). The `metadata.json` for chunked lectures records
the chunk structure under a `chunked: true` flag and lists
chunk-boundary section ranges.

## Case ontology and reconciliation

Each `case_index.md` maps the substantively developed cases in its
lecture to entries in a canonical case canon
(`ontology/cases_aggregate_v2.json`, 1,676 deduplicated cluster
entries). Cases the editorial pass identified as not matching any
canonical entry are flagged with the prefix `PROPOSED:` for later
canonicalization.

A reconciliation pass (`pipeline/reconcile_canon.py`) addresses two
follow-up concerns:

1. **Brief mentions.** Canonical clusters that Tom mentions briefly
   but does not develop substantively in a lecture were not captured
   by per-lecture case extraction. The reconciliation pass identifies
   these by keyword candidate generation against Layer 3 paragraphs,
   followed by model-based verification with conservative
   skip-on-ambiguity (the model must confidently affirm a match
   before a reference is committed). Confirmed brief mentions are
   written to per-lecture `extended_case_references.md` files. In
   v1.0.0 this recovered 255 additional canonical-cluster references
   across 158 lectures.

2. **Proposed-cluster merge suggestions.** Each PROPOSED cluster
   surfaced during editorial review is compared against canonical
   candidates that share keywords. The model suggests merges for clear
   duplicates and flags genuinely-new clusters for editorial triage.
   In v1.0.0 this produced 5 merge suggestions and flagged 46
   proposed-new clusters for editorial triage; merge suggestions are
   in `ontology/proposed_merge_suggestions.json`.

## What the corpus does *not* cleanly recover

- The reconciliation pass has bounded recall. About 486 canonical
  clusters remain unreferenced after reconciliation, primarily because
  their cluster_ids use descriptive language (e.g., "1980s American
  steel industry restructuring") that does not yield distinctive
  search keywords. Future revisions may employ semantic search to
  close this gap.

- The 2 chunked lectures contain visible chunk-boundary markers in
  their editorial register and case index. These flag locations where
  a human editor should review for boundary-smoothing and cross-chunk
  case-frame consolidation.

- The canon itself contains some duplicate cluster entries (e.g., a
  case appearing under two near-synonymous cluster_ids). Ontology
  reconciliation in future revisions will collapse these. The 1,676
  figure should be read as "1,676 entries in the working canon" rather
  than "1,676 fully-distinct cases."

## Reproducibility

The complete build (pipeline + reference materials + canon) is in
`pipeline/` and `ontology/`. A researcher with the source captions
(downloadable from the YouTube channel) can reproduce the corpus by
running `pipeline/run_pipeline.py` against the references in
`pipeline/pipeline_refs/`. Per-lecture `metadata.json` files include
`raw_transcript_sha256` so any rebuild can be verified against the
exact caption text v1.0.0 was built from.
