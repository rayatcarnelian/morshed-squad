"""IBM embedding providers."""

from morshed_squad.rag.embeddings.providers.ibm.types import (
    WatsonXProviderConfig,
    WatsonXProviderSpec,
)
from morshed_squad.rag.embeddings.providers.ibm.watsonx import (
    WatsonXProvider,
)


__all__ = [
    "WatsonXProvider",
    "WatsonXProviderConfig",
    "WatsonXProviderSpec",
]
