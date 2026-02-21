"""AWS embedding providers."""

from morshed_squad.rag.embeddings.providers.aws.bedrock import BedrockProvider
from morshed_squad.rag.embeddings.providers.aws.types import (
    BedrockProviderConfig,
    BedrockProviderSpec,
)


__all__ = [
    "BedrockProvider",
    "BedrockProviderConfig",
    "BedrockProviderSpec",
]
