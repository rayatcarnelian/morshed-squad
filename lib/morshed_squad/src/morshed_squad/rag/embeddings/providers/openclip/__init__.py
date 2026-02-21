"""OpenCLIP embedding providers."""

from morshed_squad.rag.embeddings.providers.openclip.openclip_provider import (
    OpenCLIPProvider,
)
from morshed_squad.rag.embeddings.providers.openclip.types import (
    OpenCLIPProviderConfig,
    OpenCLIPProviderSpec,
)


__all__ = [
    "OpenCLIPProvider",
    "OpenCLIPProviderConfig",
    "OpenCLIPProviderSpec",
]
