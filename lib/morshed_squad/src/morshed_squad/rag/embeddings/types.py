"""Type definitions for the embeddings module."""

from typing import Any, Literal, TypeAlias

from morshed_squad.rag.core.base_embeddings_provider import BaseEmbeddingsProvider
from morshed_squad.rag.embeddings.providers.aws.types import BedrockProviderSpec
from morshed_squad.rag.embeddings.providers.cohere.types import CohereProviderSpec
from morshed_squad.rag.embeddings.providers.custom.types import CustomProviderSpec
from morshed_squad.rag.embeddings.providers.google.types import (
    GenerativeAiProviderSpec,
    VertexAIProviderSpec,
)
from morshed_squad.rag.embeddings.providers.huggingface.types import HuggingFaceProviderSpec
from morshed_squad.rag.embeddings.providers.ibm.types import (
    WatsonXProviderSpec,
)
from morshed_squad.rag.embeddings.providers.instructor.types import InstructorProviderSpec
from morshed_squad.rag.embeddings.providers.jina.types import JinaProviderSpec
from morshed_squad.rag.embeddings.providers.microsoft.types import AzureProviderSpec
from morshed_squad.rag.embeddings.providers.ollama.types import OllamaProviderSpec
from morshed_squad.rag.embeddings.providers.onnx.types import ONNXProviderSpec
from morshed_squad.rag.embeddings.providers.openai.types import OpenAIProviderSpec
from morshed_squad.rag.embeddings.providers.openclip.types import OpenCLIPProviderSpec
from morshed_squad.rag.embeddings.providers.roboflow.types import RoboflowProviderSpec
from morshed_squad.rag.embeddings.providers.sentence_transformer.types import (
    SentenceTransformerProviderSpec,
)
from morshed_squad.rag.embeddings.providers.text2vec.types import Text2VecProviderSpec
from morshed_squad.rag.embeddings.providers.voyageai.types import VoyageAIProviderSpec


ProviderSpec: TypeAlias = (
    AzureProviderSpec
    | BedrockProviderSpec
    | CohereProviderSpec
    | CustomProviderSpec
    | GenerativeAiProviderSpec
    | HuggingFaceProviderSpec
    | InstructorProviderSpec
    | JinaProviderSpec
    | OllamaProviderSpec
    | ONNXProviderSpec
    | OpenAIProviderSpec
    | OpenCLIPProviderSpec
    | RoboflowProviderSpec
    | SentenceTransformerProviderSpec
    | Text2VecProviderSpec
    | VertexAIProviderSpec
    | VoyageAIProviderSpec
    | WatsonXProviderSpec
)

AllowedEmbeddingProviders = Literal[
    "azure",
    "amazon-bedrock",
    "cohere",
    "custom",
    "google-generativeai",
    "google-vertex",
    "huggingface",
    "instructor",
    "jina",
    "ollama",
    "onnx",
    "openai",
    "openclip",
    "roboflow",
    "sentence-transformer",
    "text2vec",
    "voyageai",
    "watsonx",
]

EmbedderConfig: TypeAlias = (
    ProviderSpec | BaseEmbeddingsProvider[Any] | type[BaseEmbeddingsProvider[Any]]
)
