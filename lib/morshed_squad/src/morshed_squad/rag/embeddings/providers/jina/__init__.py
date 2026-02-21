"""Jina embedding providers."""

from morshed_squad.rag.embeddings.providers.jina.jina_provider import JinaProvider
from morshed_squad.rag.embeddings.providers.jina.types import (
    JinaProviderConfig,
    JinaProviderSpec,
)


__all__ = [
    "JinaProvider",
    "JinaProviderConfig",
    "JinaProviderSpec",
]
