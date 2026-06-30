"""Embedding and vector store for hook retrieval."""

import logging
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from config.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    DEFAULT_TOP_K,
    EMBEDDING_MODEL_NAME,
)
from ingestion.schemas import RetrievalResult

logger = logging.getLogger(__name__)


class HookVectorStore:
    """Embeds hooks and stores/retrieves them via Chroma."""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL_NAME,
        collection_name: str = CHROMA_COLLECTION_NAME,
        persist_dir: Optional[str] = CHROMA_PERSIST_DIR,
    ):
        self.model = SentenceTransformer(model_name)

        if persist_dir:
            self.client = chromadb.PersistentClient(path=persist_dir)
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(collection_name)

    def embed_and_store(self, hooks: list[dict]) -> int:
        """Embed hook texts and upsert into Chroma. Returns count stored."""
        if not hooks:
            return 0

        texts = [h["hook_text"] for h in hooks]
        ids = [h["hook_id"] for h in hooks]
        embeddings = self.model.encode(texts).tolist()

        metadatas = [
            {
                "label": h.get("label", ""),
                "engagement_ratio": h.get("engagement_ratio", 0.0),
            }
            for h in hooks
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            # pyrefly: ignore [bad-argument-type]
            metadatas=metadatas,
        )

        logger.info(f"Stored {len(hooks)} hooks in Chroma")
        return len(hooks)

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievalResult]:
        """Find the top-k most similar hooks to a query string."""
        query_embedding = self.model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        retrieval_results = []
        for i in range(len(results["documents"][0])):
            retrieval_results.append(
                RetrievalResult(
                    hook_id=results["ids"][0][i],
                    hook_text=results["documents"][0][i],
                    label=results["metadatas"][0][i].get("label"),
                    engagement_ratio=results["metadatas"][0][i].get("engagement_ratio", 0.0),
                    distance=results["distances"][0][i],
                )
            )

        return retrieval_results

    def get_embeddings(self, hook_ids: list[str]) -> dict:
        """Fetch stored embeddings from Chroma by ID.

        Returns dict mapping hook_id -> embedding vector (list[float]).
        Used by Phase 3 classifier to get features without re-encoding.
        """
        result = self.collection.get(ids=hook_ids, include=["embeddings"])
        embeddings = result["embeddings"] if result["embeddings"] is not None else []
        return {
            hook_id: embedding
            for hook_id, embedding in zip(result["ids"], embeddings)
        }
