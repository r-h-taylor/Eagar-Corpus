#!/usr/bin/env python3
"""
reconcile_canon.py — find brief mentions of canonical cases that the
per-lecture case_index extraction missed.

Two-pass reconciliation:
  Pass 1 (keyword): for each unreferenced canonical cluster (and each
    PROPOSED cluster), tokenize the cluster_id into 2-3 distinctive
    keywords, scan all layer3.md files for paragraphs containing those
    keywords. Produces candidate matches with paragraph anchors.

  Pass 2 (verification): for each candidate, send the cluster_id + the
    candidate paragraph(s) + a small window of context to the model.
    Ask: "Is Tom referring to THIS specific case in this passage?"
    Only commit confident yes-matches; skip ambiguous and no-matches.

Outputs (per lecture):
    output/v1/lectures/<vid>/extended_case_references.md
        Supplements case_index.md with brief-mention canonical-cluster
        references. Each entry includes the paragraph anchor and a
        verbatim quote.

Outputs (corpus-wide):
    output/v1/reconciliation_report.json
        Per-cluster summary: keywords used, candidate count, confirmed
        matches, skipped (ambiguous) candidates. For editorial audit.

    output/v1/proposed_merge_suggestions.json
        For each PROPOSED cluster, suggested merge target in the canon
        (if confident match found). Human editor decides.

Usage:
    python3 reconcile_canon.py --dry-run         # see plan, no API calls
    python3 reconcile_canon.py --limit 10        # test on first 10 clusters
    python3 reconcile_canon.py                   # full run (~$15-40 API)
    python3 reconcile_canon.py --proposed-only   # just merge PROPOSED
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    sys.exit(1)


MODEL = "claude-opus-4-7"
MAX_TOKENS = 1024  # verification calls are tiny

CANON_PATH = Path("cases_aggregate_v2.json")
OUTPUT_DIR = Path("output/v1/lectures")
REPORT_PATH = Path("output/v1/reconciliation_report.json")
MERGE_SUGGESTIONS_PATH = Path("output/v1/proposed_merge_suggestions.json")


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

STOPWORDS = {
    # English function words
    "a", "an", "and", "the", "or", "of", "in", "on", "at", "to", "for",
    "with", "by", "from", "as", "is", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "this", "that", "these",
    "those", "it", "its", "his", "her", "their", "our", "your", "my",
    # Generic engineering noise words
    "case", "issue", "problem", "study", "failure", "incident",
    "investigation", "analysis", "research", "experiment", "experiments",
    "studies", "history", "story", "example", "approach", "method",
    "technique", "process", "system", "systems", "project",
    "development", "design", "lecture", "topic",
    # Tom-specific noise
    "tom", "eagar", "consulting",
}


# Distinctive proper nouns + technical terms in 1.65M words of Eagar corpus
# threshold: word must appear in <40% of lectures to be considered "distinctive"
DISTINCTIVENESS_THRESHOLD = 0.40


def tokenize_cluster_id(cluster_id: str) -> list[str]:
    """Tokenize a cluster_id into candidate keywords, lowercased, filtered."""
    # Strip "PROPOSED:" prefix if present
    if cluster_id.startswith("PROPOSED:"):
        cluster_id = cluster_id[len("PROPOSED:"):].strip()
    # Normalize: lowercase, strip parentheticals/dashes
    text = cluster_id.lower()
    text = re.sub(r"\(.*?\)", " ", text)  # drop parentheticals
    text = re.sub(r"[\u2013\u2014\u2015\-]", " ", text)  # dashes to spaces
    text = re.sub(r"[^a-z0-9 ]", " ", text)  # punctuation to spaces
    tokens = text.split()
    # Drop stopwords and 1-char tokens
    return [t for t in tokens if t not in STOPWORDS and len(t) >= 2]


def build_corpus_index(layer3_texts: dict[str, str]) -> dict[str, int]:
    """Count how many lectures contain each word (for distinctiveness scoring)."""
    word_doc_count = Counter()
    for vid, text in layer3_texts.items():
        seen = set()
        for word in re.findall(r"\b[a-z]+\b", text.lower()):
            if word in STOPWORDS or len(word) < 3:
                continue
            if word not in seen:
                word_doc_count[word] += 1
                seen.add(word)
    return word_doc_count


def select_keywords(cluster_id: str, doc_count: dict[str, int], n_lectures: int,
                    max_keywords: int = 3) -> list[str]:
    """Pick the 2-3 most distinctive keywords from a cluster_id."""
    tokens = tokenize_cluster_id(cluster_id)
    if not tokens:
        return []
    # Rank by document-frequency (lower = more distinctive)
    # Treat unknown tokens (not in doc_count) as very distinctive (proper nouns rare in corpus)
    scored = []
    for tok in tokens:
        df = doc_count.get(tok, 0)
        # Skip if word appears in too many lectures (not distinctive)
        if df / n_lectures > DISTINCTIVENESS_THRESHOLD:
            continue
        scored.append((df, tok))
    # Sort ascending (rarer first)
    scored.sort()
    keywords = [tok for _, tok in scored[:max_keywords]]
    # Always include at least one keyword if any token survives
    if not keywords and tokens:
        keywords = tokens[:1]
    return keywords


# ---------------------------------------------------------------------------
# Candidate finding (Pass 1)
# ---------------------------------------------------------------------------

PARA_RE = re.compile(r"`§(\d+)\.p(\d+)`[^\n]*", re.MULTILINE)


def split_layer3_paragraphs(text: str) -> list[tuple[str, str]]:
    """Return [(anchor, paragraph_text), ...] from a layer 3 file."""
    # Find all anchor positions
    matches = list(re.finditer(r"`§(\d+)\.p(\d+)`", text))
    if not matches:
        return []
    paragraphs = []
    for i, m in enumerate(matches):
        anchor = f"§{m.group(1)}.p{m.group(2)}"
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        paragraphs.append((anchor, text[start:end].strip()))
    return paragraphs


def find_candidates(
    cluster_id: str,
    keywords: list[str],
    layer3_paragraphs_per_lec: dict[str, list[tuple[str, str]]],
    case_indexed_per_lec: dict[str, set[str]],
) -> list[dict]:
    """For one cluster + its keywords, find candidate paragraphs across all
    lectures where ALL keywords appear in the paragraph. Skip paragraphs in
    lectures that already have the cluster in their case_index.md."""
    if not keywords:
        return []
    candidates = []
    for vid, paragraphs in layer3_paragraphs_per_lec.items():
        # Skip if this lecture already has the cluster substantively indexed
        if cluster_id in case_indexed_per_lec.get(vid, set()):
            continue
        for anchor, para_text in paragraphs:
            para_lower = para_text.lower()
            if all(kw in para_lower for kw in keywords):
                candidates.append({
                    "vid": vid,
                    "anchor": anchor,
                    "paragraph": para_text,
                })
    return candidates


# ---------------------------------------------------------------------------
# Verification (Pass 2)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_VERIFY = """You verify whether a passage from a transcript of Prof. Thomas W.
Eagar's MIT lectures contains a brief reference to a specific named
case.

You will be given:
  - the canonical name of a case from the corpus's case ontology
  - a short passage from one of Tom's lectures

Respond in exactly this JSON format, with no other text:

  {"match": "yes"}    if Tom is clearly referring to THIS specific case in this passage
  {"match": "no"}     if the passage is about something different
  {"match": "unsure"} if the keywords overlap but you cannot tell whether Tom is referring to
                      this specific case or a different but related one

Be strict. "yes" should mean the passage is clearly about this case, even if briefly. If you
have to reach to make the match work, say "unsure"."""


def verify_match(client: Anthropic, cluster_id: str, paragraph: str) -> str:
    """Returns 'yes', 'no', or 'unsure'."""
    # Truncate paragraph if very long (rare; layer 3 paragraphs are usually <500 words)
    if len(paragraph) > 3000:
        paragraph = paragraph[:3000] + " [...]"
    display_id = cluster_id[len("PROPOSED:"):].strip() if cluster_id.startswith("PROPOSED:") else cluster_id
    user_message = f"""Canonical case name: "{display_id}"

Passage from Tom's lecture:
\"\"\"
{paragraph}
\"\"\"

Is Tom referring to this specific case in this passage? Respond with JSON: {{"match": "yes"|"no"|"unsure"}}."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT_VERIFY,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        # Extract the JSON
        m = re.search(r'\{[^}]*"match"\s*:\s*"(yes|no|unsure)"[^}]*\}', text)
        if m:
            return m.group(1)
        return "unsure"
    except Exception as e:
        print(f"      verify error: {type(e).__name__}: {str(e)[:80]}")
        return "unsure"


# ---------------------------------------------------------------------------
# PROPOSED cluster merge suggestion
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_MERGE = """You compare a "PROPOSED" cluster id (a new case identified during
editorial review) to a list of candidate canonical clusters and decide
whether the PROPOSED is a duplicate of any canonical, or genuinely new.

Respond in this JSON format only:

  {"merge_into": "<canonical_cluster_id>"}    if PROPOSED is clearly a duplicate
  {"merge_into": null, "reason": "new"}       if PROPOSED is genuinely a new case
  {"merge_into": null, "reason": "unsure"}    if you cannot decide confidently

Be strict. Only say "merge" when the canonical and PROPOSED are clearly the same underlying case."""


def suggest_merge(client: Anthropic, proposed: str, candidates: list[str]) -> dict:
    """Returns dict with merge_into (cluster_id or null) and reason."""
    cand_block = "\n".join(f"  - {c}" for c in candidates)
    display = proposed[len("PROPOSED:"):].strip() if proposed.startswith("PROPOSED:") else proposed
    user_message = f"""PROPOSED cluster id: "{display}"

Candidate canonical clusters that share keywords with the PROPOSED:
{cand_block}

Is the PROPOSED a duplicate of any of these, or is it genuinely new?
Respond with the JSON format above."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT_MERGE,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        # Extract JSON
        m = re.search(r'\{[^}]*"merge_into"\s*:\s*(?:"([^"]+)"|null)[^}]*\}', text)
        if m:
            merge_into = m.group(1)
            if merge_into:
                return {"merge_into": merge_into, "reason": "duplicate"}
            else:
                return {"merge_into": None, "reason": "new_or_unsure"}
        return {"merge_into": None, "reason": "parse_failure", "raw": text}
    except Exception as e:
        return {"merge_into": None, "reason": f"error: {type(e).__name__}"}


# ---------------------------------------------------------------------------
# Per-lecture file writing
# ---------------------------------------------------------------------------

def write_extended_case_references(vid: str, confirmed: list[dict]):
    """Write/update output/v1/lectures/<vid>/extended_case_references.md."""
    out_path = OUTPUT_DIR / vid / "extended_case_references.md"
    if not confirmed:
        return
    lines = []
    lines.append(f"# Extended Case References — Lecture {vid}")
    lines.append("")
    lines.append("*Brief mentions of canonical cases that did not warrant a full "
                 "`case_index.md` entry. Generated by reconciliation pass against "
                 "the 1,676-cluster canon. Substantive treatments are in `case_index.md`.*")
    lines.append("")
    lines.append("## Cases mentioned in passing")
    lines.append("")
    # Group by anchor for stable ordering
    confirmed_sorted = sorted(confirmed, key=lambda c: (
        int(re.match(r"§(\d+)\.", c["anchor"]).group(1)) if re.match(r"§(\d+)\.", c["anchor"]) else 0,
        int(re.match(r"§\d+\.p(\d+)", c["anchor"]).group(1)) if re.match(r"§\d+\.p(\d+)", c["anchor"]) else 0,
    ))
    for entry in confirmed_sorted:
        cid_display = entry["cluster_id"]
        if cid_display.startswith("PROPOSED:"):
            cid_display = cid_display[len("PROPOSED:"):].strip()
        lines.append(f"### {cid_display}")
        lines.append(f"- **canonical_cluster_id:** \"{entry['cluster_id']}\"")
        lines.append(f"- **Anchor:** `{entry['anchor']}`")
        # Trim quote to ~400 chars for the file
        quote = entry["paragraph"]
        # Strip the leading `§N.pM` anchor + space
        quote = re.sub(r"^`§\d+\.p\d+`\s*", "", quote).strip()
        if len(quote) > 600:
            quote = quote[:600].rsplit(" ", 1)[0] + "..."
        lines.append(f"- **Quote (layer 3):** \"{quote}\"")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Plan only, no API calls")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N unreferenced clusters (testing)")
    parser.add_argument("--proposed-only", action="store_true", help="Only run PROPOSED-merge pass")
    parser.add_argument("--max-candidates", type=int, default=8,
                        help="Max keyword-candidate paragraphs to verify per cluster (default 8)")
    args = parser.parse_args()

    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = None if args.dry_run else Anthropic()

    # --- Load canon ---
    canon_data = json.loads(CANON_PATH.read_text(encoding="utf-8"))
    all_clusters = sorted({r["cluster_id"] for r in canon_data if r.get("cluster_id")})
    print(f"Canon clusters: {len(all_clusters)}")

    # --- Load per-lecture layer3 + case_index ---
    layer3_per_lec = {}
    case_indexed_per_lec = defaultdict(set)
    proposed_clusters_per_lec = defaultdict(list)
    for lec_dir in sorted(OUTPUT_DIR.iterdir()):
        if not lec_dir.is_dir():
            continue
        l3 = lec_dir / "layer3.md"
        ci = lec_dir / "case_index.md"
        if l3.exists():
            layer3_per_lec[lec_dir.name] = l3.read_text(encoding="utf-8")
        if ci.exists():
            text = ci.read_text(encoding="utf-8")
            for m in re.finditer(r'canonical_cluster_id:\s*\*?\*?\s*"([^"]+)"', text):
                cid = m.group(1)
                if cid.startswith("PROPOSED:"):
                    proposed_clusters_per_lec[lec_dir.name].append(cid)
                else:
                    case_indexed_per_lec[lec_dir.name].add(cid)
    print(f"Lectures with layer3: {len(layer3_per_lec)}")

    referenced = set()
    for s in case_indexed_per_lec.values():
        referenced.update(s)
    unreferenced = sorted(set(all_clusters) - referenced)
    print(f"Unreferenced canonical clusters: {len(unreferenced)}")
    all_proposed = sorted({p for plist in proposed_clusters_per_lec.values() for p in plist})
    print(f"Unique PROPOSED clusters: {len(all_proposed)}")

    # --- Pre-split layer 3 into paragraphs per lecture (once) ---
    print("Splitting layer 3 into paragraphs...")
    layer3_paragraphs_per_lec = {
        vid: split_layer3_paragraphs(text) for vid, text in layer3_per_lec.items()
    }
    total_paragraphs = sum(len(p) for p in layer3_paragraphs_per_lec.values())
    print(f"  total paragraphs: {total_paragraphs:,}")

    # --- Build distinctiveness index ---
    print("Building corpus distinctiveness index...")
    doc_count = build_corpus_index(layer3_per_lec)
    n_lectures = len(layer3_per_lec)
    print(f"  vocabulary: {len(doc_count):,} unique words")

    # ==========================================================
    # PASS A: unreferenced canonical clusters
    # ==========================================================
    confirmed_per_lec = defaultdict(list)  # vid -> [{cluster_id, anchor, paragraph}, ...]
    report = {
        "unreferenced": [],
        "proposed_merges": [],
        "stats": {},
    }

    if not args.proposed_only:
        targets = unreferenced if args.limit is None else unreferenced[:args.limit]
        print(f"\n=== PASS A: reconcile {len(targets)} unreferenced canonical clusters ===\n")

        total_verifies = 0
        confirmed_count = 0
        skipped_count = 0

        for i, cluster_id in enumerate(targets, 1):
            keywords = select_keywords(cluster_id, doc_count, n_lectures)
            candidates = find_candidates(
                cluster_id, keywords,
                layer3_paragraphs_per_lec, case_indexed_per_lec,
            )
            # Cap candidates per cluster to keep cost bounded
            candidates = candidates[:args.max_candidates]

            cluster_report = {
                "cluster_id": cluster_id,
                "keywords": keywords,
                "candidate_count": len(candidates),
                "confirmed": [],
                "skipped": [],
            }

            if not keywords or not candidates:
                cluster_report["status"] = "no_candidates"
                report["unreferenced"].append(cluster_report)
                if args.dry_run:
                    reason = "no keywords" if not keywords else "no paragraph matches"
                    print(f"  [{i}/{len(targets)}] {cluster_id[:55]:55s}  -- {reason}")
                continue

            if args.dry_run:
                preview = ""
                if candidates:
                    first = candidates[0]
                    # Take ~100 chars of paragraph text, post-anchor
                    para = re.sub(r"^`§\d+\.p\d+`\s*", "", first["paragraph"]).strip()
                    preview = para[:120].replace("\n", " ")
                    if len(para) > 120:
                        preview += "..."
                    preview = f"\n         e.g. {first['vid']} {first['anchor']}: \"{preview}\""
                print(f"  [{i}/{len(targets)}] {cluster_id[:55]:55s}  kw={keywords}  cands={len(candidates)}{preview}")
                cluster_report["status"] = "dry_run"
                report["unreferenced"].append(cluster_report)
                continue

            for cand in candidates:
                total_verifies += 1
                verdict = verify_match(client, cluster_id, cand["paragraph"])
                if verdict == "yes":
                    confirmed_per_lec[cand["vid"]].append({
                        "cluster_id": cluster_id,
                        "anchor": cand["anchor"],
                        "paragraph": cand["paragraph"],
                    })
                    cluster_report["confirmed"].append({"vid": cand["vid"], "anchor": cand["anchor"]})
                    confirmed_count += 1
                else:
                    cluster_report["skipped"].append({
                        "vid": cand["vid"], "anchor": cand["anchor"], "verdict": verdict,
                    })
                    skipped_count += 1

            report["unreferenced"].append(cluster_report)
            if i % 25 == 0:
                print(f"  [{i}/{len(targets)}] verifies={total_verifies}, "
                      f"confirmed={confirmed_count}, skipped={skipped_count}")

        report["stats"]["pass_a_clusters_processed"] = len(targets)
        report["stats"]["pass_a_verify_calls"] = total_verifies
        report["stats"]["pass_a_confirmed_matches"] = confirmed_count
        report["stats"]["pass_a_skipped"] = skipped_count

        # Write per-lecture extended_case_references.md files
        if not args.dry_run:
            print(f"\nWriting per-lecture extended_case_references.md files...")
            for vid, entries in confirmed_per_lec.items():
                write_extended_case_references(vid, entries)
                print(f"  {vid}: {len(entries)} extended references")

    # ==========================================================
    # PASS B: PROPOSED cluster merge suggestions
    # ==========================================================
    print(f"\n=== PASS B: suggest merges for {len(all_proposed)} PROPOSED clusters ===\n")

    # Build canon-token index with distinctiveness filtering.
    # A token that appears in >15% of canon clusters is too common to
    # narrow merge candidates usefully (e.g., "steel", "MIT", "weld").
    canon_token_doc_count = Counter()
    canon_tokens_per_cluster = {}
    for cid in all_clusters:
        toks = set(tokenize_cluster_id(cid))
        canon_tokens_per_cluster[cid] = toks
        for tok in toks:
            canon_token_doc_count[tok] += 1

    canon_distinct_threshold = max(1, int(len(all_clusters) * 0.15))
    distinctive_canon_tokens = {
        tok for tok, count in canon_token_doc_count.items()
        if count <= canon_distinct_threshold
    }
    print(f"  canon-token distinctiveness: keeping {len(distinctive_canon_tokens):,} of "
          f"{len(canon_token_doc_count):,} tokens (threshold: appears in <={canon_distinct_threshold} clusters)")

    canon_keyword_index = defaultdict(list)
    for cid, toks in canon_tokens_per_cluster.items():
        for tok in toks:
            if tok in distinctive_canon_tokens:
                canon_keyword_index[tok].append(cid)

    proposed_results = []
    for i, prop in enumerate(all_proposed, 1):
        tokens = tokenize_cluster_id(prop)
        candidate_canons = set()
        for tok in tokens:
            for c in canon_keyword_index.get(tok, [])[:5]:
                candidate_canons.add(c)
        candidate_canons = list(candidate_canons)[:6]  # cap

        prop_report = {
            "proposed_cluster_id": prop,
            "candidate_canons": candidate_canons,
        }

        if not candidate_canons:
            prop_report["decision"] = {"merge_into": None, "reason": "no_candidates"}
            proposed_results.append(prop_report)
            print(f"  [{i}/{len(all_proposed)}] {prop[:60]:60s}  no candidates")
            continue

        if args.dry_run:
            print(f"  [{i}/{len(all_proposed)}] {prop[:60]:60s}  cands={len(candidate_canons)}")
            prop_report["decision"] = {"merge_into": None, "reason": "dry_run"}
            proposed_results.append(prop_report)
            continue

        decision = suggest_merge(client, prop, candidate_canons)
        prop_report["decision"] = decision
        proposed_results.append(prop_report)
        if decision.get("merge_into"):
            print(f"  [{i}/{len(all_proposed)}] MERGE: {prop[:50]} -> {decision['merge_into'][:50]}")
        else:
            print(f"  [{i}/{len(all_proposed)}] {decision.get('reason', '?')}: {prop[:55]}")

    report["proposed_merges"] = proposed_results
    report["stats"]["pass_b_proposed_processed"] = len(all_proposed)

    # Write reports
    if not args.dry_run:
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote report: {REPORT_PATH}")
        MERGE_SUGGESTIONS_PATH.write_text(
            json.dumps(proposed_results, indent=2), encoding="utf-8"
        )
        print(f"Wrote merge suggestions: {MERGE_SUGGESTIONS_PATH}")

    print("\n=== DONE ===")
    print(f"Pass A: {report['stats'].get('pass_a_confirmed_matches', '?')} confirmed brief mentions")
    print(f"Pass B: {sum(1 for p in proposed_results if p['decision'].get('merge_into'))} suggested merges")


if __name__ == "__main__":
    main()
