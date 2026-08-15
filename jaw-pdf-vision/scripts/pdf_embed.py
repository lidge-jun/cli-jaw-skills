#!/usr/bin/env python3
"""pdf_embed.py — 텍스트 청킹 → API 임베딩 → {name}.vectors.json 저장.

Usage:
  python3 pdf_embed.py <merged_json> <name> [--output-dir DIR]

Input: pdf_check + ocr.swift 결과를 병합한 JSON (page/text 배열)
Output: {name}.vectors.json (벡터 + 텍스트 + 메타데이터)
"""
import argparse
import json
import math
import os
import sys
import time

# sys.path 보정: _embedding.py 가 같은 디렉토리에 있으므로
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _embedding import embed_texts

TARGET_CHUNK_SIZE = 500  # 한글 5~8문장 ≈ 1단락, gemini-embedding-001 한도(2048tok) 내 여유


def chunk_page(text: str) -> list:
    """페이지 균등 분할. ≤500자면 그대로, 초과 시 equal-split (찌꺼기 없음)."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= TARGET_CHUNK_SIZE:
        return [text]
    n_chunks = math.ceil(len(text) / TARGET_CHUNK_SIZE)
    chunk_size = math.ceil(len(text) / n_chunks)
    return [text[i : i + chunk_size].strip() for i in range(0, len(text), chunk_size) if text[i : i + chunk_size].strip()]


def format_table(table: list) -> str:
    """pdfplumber 표 → '헤더: 값' 형태 텍스트로 변환."""
    if not table or len(table) < 2:
        return ""
    headers = [str(h or "").strip() for h in table[0]]
    rows = []
    for row in table[1:]:
        cells = [str(c or "").strip() for c in row]
        pairs = [f"{h}: {v}" for h, v in zip(headers, cells) if v]
        if pairs:
            rows.append(" | ".join(pairs))
    return "\n".join(rows)


def embed_and_save(json_input: str, name: str, output_dir: str):
    """메인 파이프라인: JSON 로드 → 청킹 → 임베딩 → 저장."""
    # 이미 존재하면 스킵 (PDF는 정적 문서 → 증분 불필요)
    out_path = os.path.join(output_dir, f"{name}.vectors.json")
    if os.path.exists(out_path):
        print(json.dumps({
            "status": "skipped",
            "message": f"Already exists: {out_path}",
            "path": out_path,
        }, ensure_ascii=False))
        return

    os.makedirs(output_dir, exist_ok=True)

    # 1. Load merged JSON
    with open(json_input) as f:
        pages = json.load(f)
    print(f"Loaded {len(pages)} pages", file=sys.stderr)

    # 2. Chunk (페이지 기반 균등 분할 + 표 별도 청크)
    all_chunks = []
    for p in pages:
        page_num = p.get("page", 0)
        # 표 청크 (tables 필드가 있으면)
        for tbl in p.get("tables", []):
            tbl_text = format_table(tbl)
            if tbl_text:
                all_chunks.append({"page": page_num, "text": tbl_text, "type": "table"})
        # 텍스트 청크
        page_text = p.get("text", "")
        for c in chunk_page(page_text):
            all_chunks.append({"page": page_num, "text": c, "type": "text"})

    if not all_chunks:
        print(json.dumps({"status": "error", "message": "No text to embed"}))
        return

    print(f"Chunked into {len(all_chunks)} chunks", file=sys.stderr)

    # 3. Embed
    t0 = time.time()
    texts = [c["text"] for c in all_chunks]
    vectors = embed_texts(texts)
    embed_time = time.time() - t0
    print(
        f"Embedded {len(vectors)} chunks in {embed_time:.1f}s "
        f"(dim={len(vectors[0])})",
        file=sys.stderr,
    )

    # 4. Save
    source = pages[0].get("source", json_input) if pages else json_input
    output = {
        "name": name,
        "source": source,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "gemini"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        "total_chunks": len(all_chunks),
        "chunks": [
            {
                "page": all_chunks[i]["page"],
                "text": all_chunks[i]["text"],
                "vector": vectors[i],
            }
            for i in range(len(all_chunks))
        ],
    }
    with open(out_path, "w") as f:
        json.dump(output, f, ensure_ascii=False)

    file_kb = os.path.getsize(out_path) / 1024
    print(json.dumps({
        "status": "ok",
        "path": out_path,
        "total_chunks": len(all_chunks),
        "embed_time_seconds": round(embed_time, 1),
        "file_size_kb": round(file_kb),
    }, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF text → vector embedding → JSON")
    parser.add_argument("json_input", help="Merged JSON from pdf_check + ocr.swift")
    parser.add_argument("name", help="Document name for the output file")
    parser.add_argument(
        "--output-dir",
        default=os.path.expanduser("~/.cli-jaw/vectors"),
        help="Output directory (default: ~/.cli-jaw/vectors)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-embedding even if vectors.json exists",
    )
    args = parser.parse_args()

    if args.force:
        out = os.path.join(args.output_dir, f"{args.name}.vectors.json")
        if os.path.exists(out):
            os.remove(out)

    embed_and_save(args.json_input, args.name, args.output_dir)
