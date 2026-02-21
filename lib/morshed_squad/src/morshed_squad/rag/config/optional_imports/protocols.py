"""Protocol definitions for RAG factory modules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    from morshed_squad.rag.chromadb.client import ChromaDBClient
    from morshed_squad.rag.chromadb.config import ChromaDBConfig
    from morshed_squad.rag.qdrant.client import QdrantClient
    from morshed_squad.rag.qdrant.config import QdrantConfig


class ChromaFactoryModule(Protocol):
    """Protocol for ChromaDB factory module."""

    def create_client(self, config: ChromaDBConfig) -> ChromaDBClient:
        """Creates a ChromaDB client from configuration."""
        ...


class QdrantFactoryModule(Protocol):
    """Protocol for Qdrant factory module."""

    def create_client(self, config: QdrantConfig) -> QdrantClient:
        """Creates a Qdrant client from configuration."""
        ...
