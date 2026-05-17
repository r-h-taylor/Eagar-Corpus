#!/usr/bin/env python3
"""
build_wordclouds.py — generate Figure 2 word clouds for the JME manuscript.

Approach:
  1. Load the top-20 cases from Table 1 of the manuscript, grouped by
     Function tag (Indust.-hist., Forensic, Biographical, Technical narrative).
  2. For each case, find all lectures referencing it via case_index.md.
  3. Extract the anchored Layer 2 paragraphs for those case references.
  4. Group paragraphs by Function family.
  5. Render four word clouds (one per family), saved as a 2x2 composite PDF.
  6. Print top-30 words per panel for sanity-check against manuscript claims.

Output:
  release/figure2_wordclouds.pdf       composite figure
  release/figure2_top_words_per_panel.txt   audit of top words

Usage:
  python3 build_wordclouds.py
  python3 build_wordclouds.py --dry-run   # show plan, don't render
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: requires `pip install wordcloud matplotlib`")
    sys.exit(1)


LECTURES_DIR = Path("output/v1/lectures")
OUTPUT_PDF = Path("figure2_wordclouds.pdf")
OUTPUT_AUDIT = Path("figure2_top_words_per_panel.txt")


# Top-20 cases from Table 1 of the manuscript, grouped by Function.
# Cluster names must match the canonical_cluster_id strings in case_index.md files.
TOP_20_BY_FAMILY = {
    "Industrial-historical": [
        "Saugus Ironworks",
        "1973 Arab oil embargo",
        "Bethlehem Steel Burns Harbor",
        "Tom Eagar's steel company experience",
        "Watertown Arsenal titanium development",
        "Basic oxygen furnace introduction in Austria",
        "Continuous casting and steel industry capacity collapse",
        "Wright brothers' aircraft engine",
        "British Welding Institute founding",
        "Andrew Mellon all-aluminum Pierce Arrow automobile",
        # Judgment under industrial constraint (B2) - grouped here as industrial
        "Clayton Christensen innovator's dilemma research—steel mill cost data",
        "Air Force Buy-to-Fly Ratio in Aircraft Manufacturing",
        "Lakshmi Mittal steel mill acquisition strategy",
    ],
    "Forensic": [
        "Liberty ships and SS Schenectady",
        "World Trade Center collapse",
        "V-22 Osprey aircraft",
        "Soviet Alpha-class submarine",
        "Space Shuttle Challenger",
        "Space Shuttle cost overrun",
    ],
    "Biographical": [
        # Tom's own self-narrative material
        "Tom Eagar's steel company experience",
    ],
    "Technical narrative": [
        # Cases Tom frames primarily as science-to-engineering arcs
        "Iron whiskers (1950s screw dislocation studies)",
    ],
}


# Stopwords — standard English plus Eagar-specific discourse markers.
ENGLISH_STOPWORDS = {
    # Articles, pronouns, common verbs
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at",
    "for", "with", "by", "from", "as", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "done",
    "this", "that", "these", "those", "there", "here", "where", "when",
    "what", "which", "who", "whom", "whose", "why", "how",
    "it", "its", "he", "she", "they", "them", "their", "his", "her", "hers",
    "him", "you", "your", "yours", "we", "our", "us", "i", "me", "my", "mine",
    "will", "would", "could", "should", "shall", "may", "might", "must",
    "can", "cannot", "not", "no", "yes",
    "so", "than", "then", "if", "while", "because", "though", "although",
    "into", "onto", "upon", "out", "over", "under", "between", "through",
    "before", "after", "during", "since", "until",
    "very", "too", "also", "only", "just", "even", "still",
    "any", "all", "some", "every", "each", "few", "more", "most", "least",
    "other", "another", "such", "same", "different",
    "about", "around", "above", "below",
    "off", "down", "up",
    "again", "always", "ever", "never",
    "yet", "yet",
    "either", "neither", "nor", "both",
    "where", "whether",
    "own",
    "lot", "lots", "more", "less",
    # Contraction stems (after apostrophe-stripping)
    "didn", "don", "won", "couldn", "wouldn", "shouldn",
    "wasn", "isn", "aren", "weren", "haven", "hasn", "hadn",
    "doesn", "ain", "mightn", "needn", "mustn", "shan",
    "ve", "ll", "re", "ll",
}
EAGAR_STOPWORDS = {
    "okay", "right", "kind", "sort", "well", "now", "ok", "yeah",
    "youre", "im", "weve", "thats", "dont", "didnt", "wasnt", "couldnt",
    "wouldnt", "isnt", "youll", "youve", "hes", "shes", "theyll",
    "id", "ive", "wed", "youd", "actually", "basically", "really", "like",
    "going", "got", "get", "lot", "lots", "things", "thing", "stuff",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "first", "second", "third",
    "guy", "guys", "people", "person",
    "good", "great", "fine", "nice",
    "back", "way", "use", "used", "using",
    "say", "said", "says", "saying", "told", "talk", "talked", "talking",
    "see", "saw", "seen", "look", "looked", "looking", "watch",
    "know", "knew", "known", "think", "thought", "thinking",
    "want", "wanted", "wanting", "need", "needed", "needing",
    "make", "made", "making", "do", "doing", "done", "did",
    "go", "goes", "went", "gone",
    "come", "comes", "came", "coming",
    "put", "putting", "take", "took", "taken", "taking",
    "give", "gave", "given", "giving",
    "let", "letting", "lets",
    "much", "many", "little", "big", "small", "long", "short",
    "high", "higher", "highest", "low", "lower", "lowest",
    "new", "old", "year", "years", "time", "times", "day", "days", "week",
    "today", "yesterday", "tomorrow", "now", "then",
    "always", "never", "sometimes", "often", "usually",
    "case", "cases", "example", "examples",
    # Words that bleed across panels and don't characterize one
    "tom", "eagar",
    # Names of universities/places that appear everywhere
    "mit", "harvard",
}

STOPWORDS = ENGLISH_STOPWORDS | EAGAR_STOPWORDS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_case_anchors(case_index_path: Path) -> list[tuple[str, list[str]]]:
    """Parse case_index.md, return list of (cluster_id, [anchor strings]).

    Handles three Anchor field formats:
      `§3.p2`                                 single
      `§2.p2–§2.p7`                           range inside one backtick span
      `§2.p5`, `§4.p1`                        multiple separate spans
      `§2.p2–§2.p7`, `§4.p2–§4.p4`            multiple ranges
    """
    if not case_index_path.exists():
        return []
    text = case_index_path.read_text(encoding="utf-8")
    out = []
    for block in re.split(r"\n(?=### )", text):
        if not block.startswith("### "):
            continue
        cid_match = re.search(r'canonical_cluster_id:\s*\*?\*?\s*"([^"]+)"', block)
        if not cid_match:
            continue
        cluster_id = cid_match.group(1)
        anchor_match = re.search(r"\*\*Anchor:\*\*\s*([^\n]+)", block)
        if not anchor_match:
            continue
        anchor_field = anchor_match.group(1)

        anchors = []
        # Match each backticked span: `§N.pM` or `§N.pM–§N.pM` (en-dash, em-dash, or hyphen)
        for span_match in re.finditer(
            r"`§(\d+)\.p(\d+)(?:\s*[\-–—]\s*§(\d+)\.p(\d+))?`",
            anchor_field
        ):
            sec_a, para_a = int(span_match.group(1)), int(span_match.group(2))
            if span_match.group(3):
                # Range
                sec_b, para_b = int(span_match.group(3)), int(span_match.group(4))
                if sec_a == sec_b:
                    for p in range(para_a, para_b + 1):
                        anchors.append(f"§{sec_a}.p{p}")
                else:
                    # Cross-section range — include endpoints; rare case
                    anchors.append(f"§{sec_a}.p{para_a}")
                    anchors.append(f"§{sec_b}.p{para_b}")
            else:
                anchors.append(f"§{sec_a}.p{para_a}")

        if anchors:
            out.append((cluster_id, anchors))
    return out


def extract_paragraph_text(layer3_path: Path, anchor: str) -> str:
    """Find a paragraph in layer3.md by its `§N.pM` anchor and return its text.

    Layer 3 paragraphs are formatted as:
      `§N.pM` <paragraph text>

    The paragraph runs until the next `§N.pM` anchor or the next ## §N section header.
    """
    if not layer3_path.exists():
        return ""
    text = layer3_path.read_text(encoding="utf-8")
    # Locate the anchor (with backticks around §N.pM)
    pattern = rf"`{re.escape(anchor)}`"
    m = re.search(pattern, text)
    if not m:
        return ""
    start = m.end()
    # Paragraph ends at the next anchor or a ## §N section heading
    end_match = re.search(r"\n(?:`§\d+\.p\d+`|## §|---\s*$)", text[start:])
    if end_match:
        return text[start:start + end_match.start()].strip()
    return text[start:].strip()


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, return word list."""
    text = text.lower()
    # Drop markdown / latex / brackets
    text = re.sub(r"\[.*?\]", " ", text)
    text = re.sub(r"\*+", " ", text)
    text = re.sub(r"[^a-zA-Z\s\-]", " ", text)
    words = text.split()
    return [w for w in words if len(w) >= 3 and w not in STOPWORDS]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Plan only, no figure rendered")
    args = parser.parse_args()

    # Index: cluster_id -> list of (lecture_vid, anchor)
    cluster_to_refs = defaultdict(list)

    print("Scanning case_index.md across 231 lectures...")
    for lec_dir in sorted(LECTURES_DIR.iterdir()):
        if not lec_dir.is_dir():
            continue
        ci = lec_dir / "case_index.md"
        for cluster_id, anchors in extract_case_anchors(ci):
            for anchor in anchors:
                cluster_to_refs[cluster_id].append((lec_dir.name, anchor))

    # Group paragraph texts by family
    family_paragraphs = defaultdict(list)
    family_clusters_found = defaultdict(list)
    family_clusters_missing = defaultdict(list)

    for family, cluster_list in TOP_20_BY_FAMILY.items():
        for cluster_id in cluster_list:
            refs = cluster_to_refs.get(cluster_id, [])
            if not refs:
                family_clusters_missing[family].append(cluster_id)
                continue
            family_clusters_found[family].append((cluster_id, len(refs)))
            for vid, anchor in refs:
                layer3_path = LECTURES_DIR / vid / "layer3.md"
                para = extract_paragraph_text(layer3_path, anchor)
                if para:
                    family_paragraphs[family].append(para)

    # Report what we found
    print("\nCase-to-paragraph mapping summary:")
    for family in TOP_20_BY_FAMILY:
        found = family_clusters_found[family]
        missing = family_clusters_missing[family]
        n_paras = len(family_paragraphs[family])
        print(f"\n  {family}:")
        print(f"    clusters found: {len(found)}/{len(TOP_20_BY_FAMILY[family])}")
        for cid, n_refs in found:
            print(f"      {n_refs:>3} refs  {cid}")
        if missing:
            print(f"    clusters NOT found (cluster_id mismatch):")
            for cid in missing:
                print(f"      MISSING:  {cid}")
        print(f"    total paragraphs extracted: {n_paras}")

    # Tokenize + count per family
    family_word_counts = {}
    for family, paras in family_paragraphs.items():
        combined = " ".join(paras)
        tokens = tokenize(combined)
        family_word_counts[family] = Counter(tokens)

    # Print top-30 audit
    audit_lines = ["# Figure 2 word cloud — top words per panel\n"]
    print("\nTop 30 words per panel:")
    for family, counts in family_word_counts.items():
        audit_lines.append(f"\n## {family}\n")
        print(f"\n  {family}:")
        top30 = counts.most_common(30)
        for word, n in top30:
            audit_lines.append(f"  {n:>4}  {word}\n")
        # Print top 15 for shell brevity
        for word, n in top30[:15]:
            print(f"    {n:>4}  {word}")

    if args.dry_run:
        print("\n[DRY RUN: skipping figure rendering]")
        return

    OUTPUT_AUDIT.write_text("".join(audit_lines), encoding="utf-8")
    print(f"\nWrote audit: {OUTPUT_AUDIT}")

    # Render 2x2 composite figure
    print("\nRendering word clouds...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    panel_labels = {
        "Industrial-historical": ("(a) Industrial-historical", axes[0, 0]),
        "Forensic": ("(b) Forensic", axes[0, 1]),
        "Biographical": ("(c) Biographical / What-is-Engineering", axes[1, 0]),
        "Technical narrative": ("(d) Technical (welding / metallurgy)", axes[1, 1]),
    }

    for family, (label, ax) in panel_labels.items():
        counts = family_word_counts.get(family, Counter())
        if not counts:
            ax.text(0.5, 0.5, f"No data for {family}", ha="center", va="center")
            ax.set_title(label, fontsize=14)
            ax.axis("off")
            continue
        wc = WordCloud(
            width=1200, height=900,
            background_color="white",
            max_words=120,
            relative_scaling=0.5,
            colormap="Greys",
            prefer_horizontal=0.85,
            min_font_size=10,
        ).generate_from_frequencies(counts)
        ax.imshow(wc, interpolation="bilinear")
        ax.set_title(label, fontsize=14)
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT_PDF, format="pdf", dpi=300, bbox_inches="tight")
    print(f"Wrote figure: {OUTPUT_PDF}")
    print(f"\nDone.")


if __name__ == "__main__":
    main()
