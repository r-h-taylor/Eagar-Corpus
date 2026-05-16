#!/usr/bin/env python3
"""
chunk_lecture.py — split a long Eagar lecture transcript into N chunks.

For lectures whose layer 2 / layer 3 output exceeds the API's effective
token ceiling, split the SOURCE transcript into N chunks before passing
to the pipeline. Each chunk runs through the pipeline independently;
process_chunked_lecture.py orchestrates the per-chunk processing and
stitch_chunks.py merges the outputs back into canonical lecture-level
files.

Usage:
    python3 chunk_lecture.py --vid WhWf_cgsv0I --chunks 4
    python3 chunk_lecture.py --vid TOum2TQZu_M --chunks 4

Each chunk includes a 30-second overlap with the next chunk's start, so
the model has continuity context when processing chunk 2+ without the
opening of the lecture.

Output goes to chunks/<vid>/chunk_N/raw.txt, plus a chunks/<vid>/manifest.json
describing the chunk boundaries.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

CORPUS_DIR = Path("eagar_corpus")
CHUNK_DIR = Path("chunks")

# Timestamp regex — matches [mm:ss] or [h:mm:ss] at start of line
TIMESTAMP_RE = re.compile(r"^\[(\d{1,3}):(\d{2})(?::(\d{2}))?\]", re.MULTILINE)


def find_source_transcript(vid: str) -> Path:
    matches = list(CORPUS_DIR.rglob(f"*{vid}*.txt"))
    matches = [p for p in matches if not p.name.endswith(".bak")]
    if not matches:
        raise FileNotFoundError(f"No source transcript found for {vid}")
    return matches[0]


def timestamp_to_seconds(match: re.Match) -> int:
    h_or_m = int(match.group(1))
    m_or_s = int(match.group(2))
    s = match.group(3)
    if s is not None:
        return h_or_m * 3600 + m_or_s * 60 + int(s)
    return h_or_m * 60 + m_or_s


def chunk_transcript(text: str, n_chunks: int, overlap_seconds: int = 30) -> list[dict]:
    """Split transcript text into N chunks at timestamp boundaries.

    Each chunk dict contains:
      - chunk_id (1-indexed)
      - n_chunks
      - start_seconds, end_seconds (real timestamps from the source)
      - overlap_seconds (how much the chunk starts BEFORE the nominal boundary)
      - text (the raw chunk text, starting with a timestamp marker)
      - line_count, word_count
    """
    # Find all timestamp positions in the text
    timestamps = []
    for m in TIMESTAMP_RE.finditer(text):
        timestamps.append({
            "match_start": m.start(),
            "seconds": timestamp_to_seconds(m),
        })

    if len(timestamps) < n_chunks * 2:
        raise ValueError(
            f"Transcript has only {len(timestamps)} timestamps; "
            f"too few for {n_chunks} chunks."
        )

    total_seconds = timestamps[-1]["seconds"]
    chunk_duration = total_seconds / n_chunks

    chunks = []
    for i in range(n_chunks):
        nominal_start_sec = i * chunk_duration
        nominal_end_sec = (i + 1) * chunk_duration

        # Apply overlap (chunk N+1 starts overlap_seconds before chunk N ends)
        if i == 0:
            actual_start_sec = 0
        else:
            actual_start_sec = max(0, nominal_start_sec - overlap_seconds)

        actual_end_sec = nominal_end_sec if i < n_chunks - 1 else total_seconds + 1

        # Find the first timestamp >= actual_start_sec
        start_idx = next(
            (j for j, ts in enumerate(timestamps) if ts["seconds"] >= actual_start_sec),
            0
        )
        # Find the last timestamp < actual_end_sec
        end_idx = len(timestamps) - 1
        for j in range(start_idx, len(timestamps)):
            if timestamps[j]["seconds"] >= actual_end_sec:
                end_idx = j - 1
                break

        start_pos = timestamps[start_idx]["match_start"]
        if end_idx + 1 < len(timestamps):
            end_pos = timestamps[end_idx + 1]["match_start"]
        else:
            end_pos = len(text)

        chunk_text = text[start_pos:end_pos]
        chunks.append({
            "chunk_id": i + 1,
            "n_chunks": n_chunks,
            "start_seconds": timestamps[start_idx]["seconds"],
            "end_seconds": timestamps[end_idx]["seconds"] if end_idx < len(timestamps) else total_seconds,
            "overlap_with_previous_seconds": overlap_seconds if i > 0 else 0,
            "text": chunk_text,
            "line_count": chunk_text.count("\n"),
            "word_count": len(chunk_text.split()),
        })

    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vid", required=True, help="Video ID")
    parser.add_argument("--chunks", type=int, default=4, help="Number of chunks (default 4)")
    parser.add_argument("--overlap", type=int, default=30, help="Overlap seconds between chunks (default 30)")
    args = parser.parse_args()

    transcript_path = find_source_transcript(args.vid)
    raw_text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    raw_sha = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    print(f"Source: {transcript_path}")
    print(f"  total lines: {raw_text.count(chr(10))}")
    print(f"  total words: {len(raw_text.split())}")
    print(f"  sha256: {raw_sha}")

    chunks = chunk_transcript(raw_text, n_chunks=args.chunks, overlap_seconds=args.overlap)

    out_dir = CHUNK_DIR / args.vid
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "video_id": args.vid,
        "source_transcript": str(transcript_path),
        "raw_transcript_sha256": raw_sha,
        "raw_transcript_word_count": len(raw_text.split()),
        "raw_transcript_line_count": raw_text.count("\n"),
        "n_chunks": args.chunks,
        "overlap_seconds": args.overlap,
        "chunks": [],
    }

    for chunk in chunks:
        chunk_dir = out_dir / f"chunk_{chunk['chunk_id']}"
        chunk_dir.mkdir(exist_ok=True)
        raw_path = chunk_dir / "raw.txt"
        raw_path.write_text(chunk["text"], encoding="utf-8")
        print(f"  chunk {chunk['chunk_id']}/{chunk['n_chunks']}: "
              f"{chunk['word_count']} words, "
              f"{chunk['start_seconds']}s -> {chunk['end_seconds']}s")
        manifest["chunks"].append({
            "chunk_id": chunk["chunk_id"],
            "n_chunks": chunk["n_chunks"],
            "start_seconds": chunk["start_seconds"],
            "end_seconds": chunk["end_seconds"],
            "overlap_with_previous_seconds": chunk["overlap_with_previous_seconds"],
            "word_count": chunk["word_count"],
            "line_count": chunk["line_count"],
            "raw_path": str(raw_path),
        })

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nWrote manifest: {manifest_path}")


if __name__ == "__main__":
    main()
