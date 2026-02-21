"""Microsoft embedding providers."""

from morshed_squad.rag.embeddings.providers.microsoft.azure import (
    AzureProvider,
)
from morshed_squad.rag.embeddings.providers.microsoft.types import (
    AzureProviderConfig,
    AzureProviderSpec,
)


__all__ = [
    "AzureProvider",
    "AzureProviderConfig",
    "AzureProviderSpec",
]
