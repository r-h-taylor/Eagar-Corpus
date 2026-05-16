# The Eagar Corpus

A three-layer searchable archive of the recorded teaching of
Prof. Thomas W. Eagar (MIT, Department of Materials Science and
Engineering, 1976–2022).

**Version:** 1.0.0
**Released:** 2026-05-16
**Zenodo DOI:** [10.5281/zenodo.20226049](https://doi.org/10.5281/zenodo.20226049)
**License:** code under MIT (see [LICENSE](LICENSE)); corpus data under
CC-BY-4.0 (see [LICENSE-DATA](LICENSE-DATA))

## What this is

Thomas W. Eagar (1949–2022) was Professor of Materials Engineering at
MIT, where he taught from 1976 until his death. Beginning in 2011 he
self-recorded his classroom lectures and posted them publicly on
YouTube under the channel `eagar.mit.edu`. The recordings span eleven
years and 23 distinct course modules, totaling approximately 170 hours
and 231 lectures.

This repository is a scholarly edition of those lectures. For each
lecture, the corpus provides:

- a **cleaned middle layer** (`layer2.md`) — YouTube auto-captions
  consolidated into paragraphed prose, with line-break artifacts and
  pure captioner errors mechanically corrected;
- an **editorial layer** (`layer3.md`) — paragraph-anchored, smoothed
  for citability, with self-corrections rendered to their corrected
  form and physical-object teaching moves rendered as italicized stage
  directions;
- a **case index** (`case_index.md`) — substantively developed cases
  mapped to a canonical clustering of the corpus;
- an **extended case-reference file** (`extended_case_references.md`)
  where applicable — brief mentions of canonical cases surfaced by a
  reconciliation pass against the canon;
- an **editorial register** documenting layer-3 editorial decisions;
- a **transformation log** documenting layer-1 → layer-2 mechanical
  rules;
- a paragraph-level **anchors file** (`anchors.json`) mapping layer-3
  citations to layer-2 paragraphs;
- a **metadata file** (`metadata.json`).

The corpus contains 1,676 deduplicated canonical case clusters
(`ontology/cases_aggregate_v2.json`), of which approximately 1,190 are
referenced in the lectures — 935 substantively (anchored in
`case_index.md` files) and an additional 255 as brief mentions
(anchored in `extended_case_references.md` files).

## Repository structure

```
eagar-corpus/
├── README.md                          this file
├── LICENSE                            MIT, for the pipeline code
├── LICENSE-DATA                       CC-BY-4.0, for the corpus
├── CITATION.cff                       machine-readable citation
├── corpus/                            the 231 lectures
│   └── lectures/<video_id>/           per-lecture files
├── ontology/                          canon and reconciliation outputs
├── pipeline/                          scripts that built the corpus
│   └── pipeline_refs/                 conventions + worked example
└── docs/                              methodology and schema docs
```

## What is not in this repository

**Source captions (Layer 1).** The corpus is derived from YouTube
auto-captions for the publicly-posted lectures on the
`eagar.mit.edu` channel. The raw caption text is not redistributed
here; YouTube's terms of service govern the captions themselves.
Researchers wishing to reconstruct Layer 1 may fetch the captions
directly from YouTube using the video IDs in `metadata.json`. The
`metadata.json` files include a `raw_transcript_sha256` field for each
lecture so reconstructed captions can be verified against the source
text the pipeline processed.

## How to cite

For the corpus as a whole:

> Taylor, R. H. (2026). *The Eagar Corpus: a three-layer archive of
> the recorded teaching of Thomas W. Eagar (MIT, 2011–2022),*
> version 1.0.0. Zenodo. [10.5281/zenodo.20226049](https://doi.org/10.5281/zenodo.20226049).

For a specific passage, cite the canonical lecture record and
paragraph anchor:

> *Eagar Corpus*, lecture `-6n9y2szRqo` (3.371 Structural Materials
> Selection, Fall 2014, lecture 11/13), §5.p8.

For more on citation conventions, see [`docs/citation.md`](docs/citation.md).

## Companion paper

R. H. Taylor, "Teaching Engineering as Practice and Science: A
Case-Pedagogy Corpus," *Journal of Materials Education* (forthcoming
2026). The corpus is the empirical basis of that paper.

## Reproducing the build

The full pipeline that produced this corpus is in `pipeline/`.
Documentation in [`docs/methods.md`](docs/methods.md). To rebuild
locally, fetch the source captions for the 231 video IDs listed in
`corpus/lectures/*/metadata.json` and run `pipeline/run_pipeline.py`
against the canonical worked-example reference in
`pipeline/pipeline_refs/`.

## Contact

Richard H. Taylor, PhD — `r_taylor@outlook.com`

Repository issues, ontology corrections, and editorial-pass
contributions are welcome via the GitHub Issues tracker.
