# Convention Catalog — Eagar Corpus Pipeline v1

Conventions established by the §1 worked example. Apply consistently across the corpus. If a case arises that none of these conventions clearly covers, apply the closest existing convention and flag the case in the editorial register so the editor can decide whether the catalog needs extending. Do not silently invent new conventions.

## 1. Student attribution
Student turns labeled `**Student:**` at the start of the paragraph. Attribution is inferred from context (Tom invites questions; a different voice asks; Tom repeats the question back). Where attribution is uncertain, flag in editorial register.

## 2. Stage directions
Physical-object teaching moves rendered as italicized brackets:
- `*[Tom produces a pair of surgical scissors.]*`
- `*[Tom holds up a continuous-cast steel beam section.]*`
- `*[Tom hands a sample around the class.]*`

The pocket-patting, item-locating, and physical-search speech that surrounds these moves is cut from layer 3. Preserved in layer 2.

## 3. Numerals
- Monetary values: `$150`, `$500`, `$50,000`.
- Years: `1990`, `1975`, `2014`.
- Rhetorical numbers spelled out: `fifty-thousand-dollar watches`, `ninety-eight, ninety-nine percent`, `a hundred and fifty years ago`.
- Productivity figures with units kept as decimals: `0.3 person-hours/ton`, `50 ksi yield`.
- Hyphenation in compound adjectives: `twenty-thousand-dollar-a-pound spacecraft`, `mile-long building`.
- Percent: numerals + word ("thirty percent"), not "30%", in prose passages where Tom is speaking rhetorically. Use "30%" only in technical/datum contexts.

## 4. Self-corrections
Layer 2 preserves the false-start-and-correction sequence verbatim. Layer 3 reads the corrected form, dropping the false start. Example:
- L2: "five hundred worth of health, and not health insurance, medical malpractice insurance"
- L3: "about five hundred dollars worth of medical malpractice insurance"

## 5. Backward-references to prior sessions
Phrases like "we talked about this last time", "remember from Tuesday", "as I said last week" are cut from layer 3. The section must read self-sufficiently. Layer 2 preserves them.

Exception: where the backward-reference carries actual content (Tom is summarizing or pointing to a specific prior case), preserve and rephrase to be self-sufficient if possible.

## 6. "Okay" handling
- Preserved where it closes a thought rhetorically: "...and that could cost fifty thousand dollars, okay."
- Cut where it's mid-clause filler: "we're talking about, okay, steel" → "we're talking about steel"
- Preserved as discourse marker between teaching units: "Okay, so what makes beer expensive?"

## 7. "You know" / "I mean" handling
- Cut except where they invoke shared classroom context that a reader needs.
- "you know, for a pipeline" → "for a pipeline"
- "you know, the way Bessemer did it" → preserve if Bessemer was just mentioned and "you know" is anchoring shared reference; cut if it's pure filler.

## 8. Soft reordering
Permitted *within* a section, never *across* sections. Every use logged in editorial_register.md with the layer 3 anchor and a one-sentence justification.

Examples of permitted reordering:
- Moving Tom's clearest statement of an answer earlier in a section, when he gave a fragmentary first attempt and then developed it properly.
- Moving a summary line to the end of a section where Tom delivered it mid-section.

Examples of NOT permitted reordering:
- Moving content between sections.
- Reordering teaching cases (if Tom taught Burns Harbor before Chaparral, layer 3 keeps that order).
- Reordering Q&A sequences.

## 9. Bracketed corrections of Tom's spoken slips
Tom occasionally misnames a person or thing (e.g., "Gordon Ford" for "Gordon Forward", which is a real recurring slip — Gordon E. Forward, MIT PhD, CEO of Chaparral Steel).

Convention:
- First occurrence in a section: `Ford [Forward]`
- Subsequent occurrences in the same section: `[Forward]` alone
- Logged in transformation_log.md (not editorial_register.md, because the correction is captured by the bracket — no editorial judgment beyond identifying the slip).

Captioner errors on proper nouns (e.g., "sango ban" for "Saint-Gobain") are corrected silently. The distinction: bracketed corrections are for things Tom actually said; silent corrections are for things the captioner mis-transcribed.

## 10. Captioner garbling fixed when unambiguous
Where the captioner produced clearly wrong text and the corrected reading is unambiguous from context, fix in both layer 2 and layer 3. Logged in transformation_log.md per occurrence with the raw line number.

Example:
- L1: "the big cost is medical math the application"
- L2 / L3: "the big cost is the medical application" ("math" was a misrecognition of Tom's mid-word hesitation)

If the corrected reading is *not* unambiguous (multiple plausible readings), preserve the captioner's text in layer 2 with a `[?]` marker, and flag in the editorial register for human review.

## 11. Sectioning
Layer 3 is divided into sections of roughly 3–8 minutes of audio each. Section breaks fall at natural teaching transitions:
- New case introduced
- Pivot from one topic to another ("okay so let's talk about glass")
- Resumption after Q&A interlude
- New slide / visual aid

Each section has:
- An anchor ID: `s1`, `s2`, ..., `sN`
- A title (a short noun phrase, not a sentence): "What makes something expensive?", "Chaparral and the productivity revolution", "Glass as a structural material"
- A starting timestamp from the raw transcript

Number of sections per lecture: typically 4–8 for a 50-minute lecture. Fewer if the lecture is structurally simple; more if Tom moves through many distinct teaching units.

## 12. Layer 2 paragraph breaks
Layer 2 paragraphs break at natural pauses in delivery — typically 30 seconds to 2 minutes of speech per paragraph. Use timestamps from the raw transcript. Each paragraph starts with a `[MM:SS]` anchor and a `pN` identifier (in markdown, written as `` `pN` `` followed by the timestamp).

## 13. Layer 3 paragraph IDs
Layer 3 paragraphs are addressed as `§N.pM` where N is the section number and M is the paragraph number within the section (1-indexed). These appear at the start of each paragraph as `` `§N.pM` `` in markdown.

## 14. Front matter
Both layer 2 and layer 3 carry YAML front matter (see spec §3.1 and §3.2). Front matter is canonical metadata; treat as machine-readable.

## 15. Case index
Per-lecture case index appears as `case_index.md`. Each case mentioned in the lecture gets one entry:

```markdown
### {canonical_case_name}
- **Anchor:** `§N.pM`
- **canonical_cluster_id:** "{from aggregate v2, or 'PROPOSED: {name}' if new}"
- **Frame in this lecture:** {one sentence}
- **Materials/systems:** {list, if applicable}
- **Era:** {if applicable}
```

If the case isn't in `aggregate_v2.json`, prefix the cluster_id with `PROPOSED:`. Post-pipeline reconciliation will collapse proposals into the canon.

A "Figures referenced" section lists recurring numeric anchors (e.g., the 1990 → 0.3 person-hours/ton steel productivity figure) — these are framing statistics, not cases.

## 16. Decisions NOT permitted at layer 3 (constitutional constraint)

- Adding new sentences in Tom's voice (Feynman/Leighton/Sands could because Feynman was alive to ratify; we cannot).
- Reordering content across section boundaries.
- Merging cases Tom kept separate, or splitting cases he handled as one.
- Removing factual errors Tom made on tape. (Captioner errors are corrected silently; Tom's slips are bracketed; Tom's genuine misstatements are preserved and footnoted in layer 3 only when they would actively mislead a reader.)

This constraint is the project's safeguard against drift into reconstruction. Include it verbatim at the end of every `editorial_register.md` produced.
