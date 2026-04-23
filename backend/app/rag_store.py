from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi


_word_re = re.compile(r"[A-Za-z0-9']+")

_stopwords = {
        "capital",
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "i",
    "in",
    "is",
    "it",
    "its",
    "me",
    "not",
    "of",
    "on",
    "or",
    "our",
    "she",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "you",
    "your",
}


def _tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _word_re.finditer(text)]


def _chunk_text(text: str, *, chunk_size_words: int = 220, overlap_words: int = 40) -> list[str]:
    words = _tokenize(text)
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size_words)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start = max(0, end - overlap_words)
    return chunks


@dataclass(frozen=True)
class Chunk:
    id: int
    text: str
    source: str


class RAGStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._chunks: list[Chunk] = []
        self._tokenized: list[list[str]] = []
        self._bm25: BM25Okapi | None = None
        self._next_id = 1

    async def clear(self) -> None:
        async with self._lock:
            self._chunks = []
            self._tokenized = []
            self._bm25 = None
            self._next_id = 1

    async def ingest_text(self, text: str, *, source: str) -> tuple[int, int]:
        new_chunks = _chunk_text(text)
        if not new_chunks:
            return 0, await self.total_chunks()

        async with self._lock:
            added = 0
            for c in new_chunks:
                chunk = Chunk(id=self._next_id, text=c, source=source)
                self._next_id += 1
                self._chunks.append(chunk)
                self._tokenized.append(_tokenize(c))
                added += 1
            self._bm25 = BM25Okapi(self._tokenized) if self._tokenized else None
            return added, len(self._chunks)

    async def total_chunks(self) -> int:
        async with self._lock:
            return len(self._chunks)

    async def search(self, query: str, *, top_k: int) -> list[tuple[Chunk, float]]:
        tokens = _tokenize(query)
        query_tokens = [t for t in tokens if t not in _stopwords]
        if not query_tokens:
            query_tokens = tokens
        async with self._lock:
            if not query_tokens or not self._bm25:
                return []
            scores = self._bm25.get_scores(query_tokens)
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

            results: list[tuple[Chunk, float]] = []
            for idx, score in ranked:
                # rank-bm25 can yield negative scores in small corpora; use token overlap
                # as the relevance gate instead of filtering by score sign.
                chunk_tokens = [t for t in self._tokenized[idx] if t not in _stopwords]
                if not chunk_tokens:
                    chunk_tokens = self._tokenized[idx]
                if not (set(query_tokens) & set(chunk_tokens)):
                    continue
                results.append((self._chunks[idx], float(score)))
            return results
