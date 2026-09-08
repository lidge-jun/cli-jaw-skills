"""Embedding provider abstraction — Gemini / OpenAI / Vertex AI.

Zero heavy dependencies: stdlib urllib for Gemini/OpenAI, google-auth for Vertex only.
Referenced from markdown-fastrag-mcp server.py embedding provider pattern.
"""
import os
import json
import sys
import urllib.request
import urllib.error

PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "50"))


def _openai_compatible(texts, url, api_key, model):
    """OpenAI-compatible embedding API (Gemini, OpenAI 공용)."""
    if not api_key:
        raise ValueError(
            f"API key required for provider '{PROVIDER}'. "
            "Set GEMINI_API_KEY or OPENAI_API_KEY."
        )
    req = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps({"model": model, "input": texts}).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())["data"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"Embedding API error ({e.code}): {detail}"
        ) from e
    # Gemini 응답에는 index 필드가 없음 → .get() fallback
    return [d["embedding"] for d in sorted(data, key=lambda x: x.get("index", 0))]


def _vertex(texts, project, location, model, dimensions):
    """Vertex AI predict endpoint (google-auth ADC 사용)."""
    from google.auth import default
    from google.auth.transport.requests import Request

    credentials, detected_project = default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    project = project or detected_project
    if not project:
        raise ValueError(
            "VERTEX_PROJECT required. Set env or run: gcloud config set project <ID>"
        )
    endpoint = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/"
        f"{project}/locations/{location}/"
        f"publishers/google/models/{model}:predict"
    )
    payload = {"instances": [{"content": t} for t in texts]}
    if dimensions:
        payload["parameters"] = {"outputDimensionality": dimensions}
    req = urllib.request.Request(
        endpoint,
        method="POST",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            predictions = json.loads(resp.read())["predictions"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"Vertex embedding error ({e.code}): {detail}"
        ) from e
    return [p["embeddings"]["values"] for p in predictions]


def embed_texts(texts: list) -> list:
    """Batch embed texts via API. Returns list of float vectors."""
    all_vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        if PROVIDER == "gemini":
            vecs = _openai_compatible(
                batch,
                "https://generativelanguage.googleapis.com/v1beta/openai/embeddings",
                os.getenv("GEMINI_API_KEY"),
                os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
            )
        elif PROVIDER == "openai":
            vecs = _openai_compatible(
                batch,
                "https://api.openai.com/v1/embeddings",
                os.getenv("OPENAI_API_KEY"),
                os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            )
        elif PROVIDER == "vertex":
            vecs = _vertex(
                batch,
                os.getenv("VERTEX_PROJECT"),
                os.getenv("VERTEX_LOCATION", "us-central1"),
                os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
                int(os.getenv("EMBEDDING_DIM", "0")) or None,
            )
        else:
            raise ValueError(f"Unsupported provider: {PROVIDER}")
        all_vectors.extend(vecs)
    return all_vectors
