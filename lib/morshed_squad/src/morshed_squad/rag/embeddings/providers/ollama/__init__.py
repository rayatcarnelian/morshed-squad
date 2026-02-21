"""Ollama embedding providers."""

from morshed_squad.rag.embeddings.providers.ollama.ollama_provider import (
    OllamaProvider,
)
from morshed_squad.rag.embeddings.providers.ollama.types import (
    OllamaProviderConfig,
    OllamaProviderSpec,
)


__all__ = [
    "OllamaProvider",
    "OllamaProviderConfig",
    "OllamaProviderSpec",
]
