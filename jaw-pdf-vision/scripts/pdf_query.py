#!/usr/bin/env python3
"""pdf_query.py — 벡터 JSON에서 시맨틱 검색 + grep 키워드 검색.

Usage:
  # 시맨틱 검색 (API 임베딩 1회)
  python3 pdf_query.py "투자를 잘하는 법" --file 경제학_거시_204

  # grep 키워드 검색 (API 호출 없음, 무료)
  python3 pdf_query.py "NPV" --file 경제학_거시_204 --grep

  # 전체 검색 (모든 .vectors.json 순회)
  python3 pdf_query.py "의제배당" --grep
"""
import argparse
import glob
import json
import math
import os
import sys

# sys.path 보정: _embedding.py 가 같은 디렉토리에 있으므로
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cosine_similarity(a: list, b: list) -> float:
    """stdlib-only 코사인 유사도."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def load_vectors(path: str) -> dict:
    """Load a .vectors.json file."""
    with open(path) as f:
        return json.load(f)


def search_in_doc(query_vec: list, doc: dict, n: int) -> list:
    """시맨틱 검색: 코사인 유사도."""
    scored = []
    for chunk in doc.get("chunks", []):
        score = cosine_similarity(query_vec, chunk["vector"])
        scored.append({
            "score": round(score, 4),
            "page": chunk.get("page", 0),
            "text": chunk["text"],
            "source": doc.get("name", "unknown"),
            "source_file": doc.get("source", ""),
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:n]


def grep_in_doc(keyword: str, doc: dict, n: int) -> list:
    """키워드 검색: 대소문자 무시 텍스트 매칭. API 호출 없음."""
    kw_lower = keyword.lower()
    results = []
    for chunk in doc.get("chunks", []):
        text = chunk["text"]
        count = text.lower().count(kw_lower)
        if count > 0:
            results.append({
                "matches": count,
                "page": chunk.get("page", 0),
                "text": text,
                "source": doc.get("name", "unknown"),
                "source_file": doc.get("source", ""),
            })
    results.sort(key=lambda x: x["matches"], reverse=True)
    return results[:n]


def get_doc_files(vectors_dir: str, file_name: str = None) -> list:
    """검색 대상 문서 파일 목록."""
    if file_name:
        path = os.path.join(vectors_dir, f"{file_name}.vectors.json")
        if not os.path.exists(path):
            return []
        return [path]
    return glob.glob(os.path.join(vectors_dir, "*.vectors.json"))


def search(query: str, vectors_dir: str, file_name: str = None, n: int = 5, grep: bool = False):
    """메인 검색 함수. grep=True면 키워드 검색, False면 시맨틱 검색."""
    files = get_doc_files(vectors_dir, file_name)
    if not files:
        target = file_name or vectors_dir
        print(json.dumps({"status": "error", "message": f"Not found: {target}"}))
        return

    if not file_name:
        print(f"Searching {len(files)} documents...", file=sys.stderr)

    all_results = []

    if grep:
        # grep 모드: API 호출 없음
        for fpath in files:
            doc = load_vectors(fpath)
            all_results.extend(grep_in_doc(query, doc, n))
        all_results.sort(key=lambda x: x["matches"], reverse=True)
    else:
        # 시맨틱 모드: 쿼리 임베딩 (API 1회)
        from _embedding import embed_texts
        query_vec = embed_texts([query])[0]
        for fpath in files:
            doc = load_vectors(fpath)
            all_results.extend(search_in_doc(query_vec, doc, n))
        all_results.sort(key=lambda x: x["score"], reverse=True)

    all_results = all_results[:n]

    print(json.dumps({
        "query": query,
        "mode": "grep" if grep else "semantic",
        "results": all_results,
        "total_results": len(all_results),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF semantic + grep search")
    parser.add_argument("query", help="Search query (semantic) or keyword (grep)")
    parser.add_argument("--file", default=None, help="Search specific document")
    parser.add_argument("--vectors-dir", default=os.path.expanduser("~/.cli-jaw/vectors"))
    parser.add_argument("--n", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--grep", action="store_true", help="Keyword search (no API call, free)")
    args = parser.parse_args()
    search(args.query, args.vectors_dir, args.file, args.n, args.grep)

