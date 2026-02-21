"""Factory functions for creating embedding providers and functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, overload

from morshed_squad.rag.core.base_embeddings_callable import EmbeddingFunction
from morshed_squad.rag.core.base_embeddings_provider import BaseEmbeddingsProvider
from morshed_squad.utilities.import_utils import import_and_validate_definition


if TYPE_CHECKING:
    from chromadb.utils.embedding_functions.amazon_bedrock_embedding_function import (
        AmazonBedrockEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.cohere_embedding_function import (
        CohereEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.google_embedding_function import (
        GoogleGenerativeAiEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.huggingface_embedding_function import (
        HuggingFaceEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.instructor_embedding_function import (
        InstructorEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.jina_embedding_function import (
        JinaEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.ollama_embedding_function import (
        OllamaEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
    from chromadb.utils.embedding_functions.open_clip_embedding_function import (
        OpenCLIPEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.openai_embedding_function import (
        OpenAIEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.roboflow_embedding_function import (
        RoboflowEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import (
        SentenceTransformerEmbeddingFunction,
    )
    from chromadb.utils.embedding_functions.text2vec_embedding_function import (
        Text2VecEmbeddingFunction,
    )

    from morshed_squad.rag.embeddings.providers.aws.types import BedrockProviderSpec
    from morshed_squad.rag.embeddings.providers.cohere.types import CohereProviderSpec
    from morshed_squad.rag.embeddings.providers.custom.types import CustomProviderSpec
    from morshed_squad.rag.embeddings.providers.google.genai_vertex_embedding import (
        GoogleGenAIVertexEmbeddingFunction,
    )
    from morshed_squad.rag.embeddings.providers.google.types import (
        GenerativeAiProviderSpec,
        VertexAIProviderSpec,
    )
    from morshed_squad.rag.embeddings.providers.huggingface.types import (
        HuggingFaceProviderSpec,
    )
    from morshed_squad.rag.embeddings.providers.ibm.embedding_callable import (
        WatsonXEmbeddingFunction,
    )
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
    from morshed_squad.rag.embeddings.providers.voyageai.embedding_callable import (
        VoyageAIEmbeddingFunction,
    )
    from morshed_squad.rag.embeddings.providers.voyageai.types import VoyageAIProviderSpec

T = TypeVar("T", bound=EmbeddingFunction[Any])


PROVIDER_PATHS = {
    "azure": "morshed_squad.rag.embeddings.providers.microsoft.azure.AzureProvider",
    "amazon-bedrock": "morshed_squad.rag.embeddings.providers.aws.bedrock.BedrockProvider",
    "cohere": "morshed_squad.rag.embeddings.providers.cohere.cohere_provider.CohereProvider",
    "custom": "morshed_squad.rag.embeddings.providers.custom.custom_provider.CustomProvider",
    "google-generativeai": "morshed_squad.rag.embeddings.providers.google.generative_ai.GenerativeAiProvider",
    "google": "morshed_squad.rag.embeddings.providers.google.generative_ai.GenerativeAiProvider",
    "google-vertex": "morshed_squad.rag.embeddings.providers.google.vertex.VertexAIProvider",
    "huggingface": "morshed_squad.rag.embeddings.providers.huggingface.huggingface_provider.HuggingFaceProvider",
    "instructor": "morshed_squad.rag.embeddings.providers.instructor.instructor_provider.InstructorProvider",
    "jina": "morshed_squad.rag.embeddings.providers.jina.jina_provider.JinaProvider",
    "ollama": "morshed_squad.rag.embeddings.providers.ollama.ollama_provider.OllamaProvider",
    "onnx": "morshed_squad.rag.embeddings.providers.onnx.onnx_provider.ONNXProvider",
    "openai": "morshed_squad.rag.embeddings.providers.openai.openai_provider.OpenAIProvider",
    "openclip": "morshed_squad.rag.embeddings.providers.openclip.openclip_provider.OpenCLIPProvider",
    "roboflow": "morshed_squad.rag.embeddings.providers.roboflow.roboflow_provider.RoboflowProvider",
    "sentence-transformer": "morshed_squad.rag.embeddings.providers.sentence_transformer.sentence_transformer_provider.SentenceTransformerProvider",
    "text2vec": "morshed_squad.rag.embeddings.providers.text2vec.text2vec_provider.Text2VecProvider",
    "voyageai": "morshed_squad.rag.embeddings.providers.voyageai.voyageai_provider.VoyageAIProvider",
    "watsonx": "morshed_squad.rag.embeddings.providers.ibm.watsonx.WatsonXProvider",
}


def build_embedder_from_provider(provider: BaseEmbeddingsProvider[T]) -> T:
    """Build an embedding function instance from a provider.

    Args:
        provider: The embedding provider configuration.

    Returns:
        An instance of the specified embedding function type.
    """
    return provider.embedding_callable(
        **provider.model_dump(exclude={"embedding_callable"})
    )


@overload
def build_embedder_from_dict(spec: AzureProviderSpec) -> OpenAIEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: BedrockProviderSpec,
) -> AmazonBedrockEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: CohereProviderSpec) -> CohereEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: CustomProviderSpec) -> EmbeddingFunction[Any]: ...


@overload
def build_embedder_from_dict(
    spec: GenerativeAiProviderSpec,
) -> GoogleGenerativeAiEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: HuggingFaceProviderSpec,
) -> HuggingFaceEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: OllamaProviderSpec) -> OllamaEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: OpenAIProviderSpec) -> OpenAIEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: VertexAIProviderSpec,
) -> GoogleGenAIVertexEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: VoyageAIProviderSpec,
) -> VoyageAIEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: WatsonXProviderSpec) -> WatsonXEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: SentenceTransformerProviderSpec,
) -> SentenceTransformerEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: InstructorProviderSpec,
) -> InstructorEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: JinaProviderSpec) -> JinaEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: RoboflowProviderSpec,
) -> RoboflowEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: OpenCLIPProviderSpec,
) -> OpenCLIPEmbeddingFunction: ...


@overload
def build_embedder_from_dict(
    spec: Text2VecProviderSpec,
) -> Text2VecEmbeddingFunction: ...


@overload
def build_embedder_from_dict(spec: ONNXProviderSpec) -> ONNXMiniLM_L6_V2: ...


def build_embedder_from_dict(spec):  # type: ignore[no-untyped-def]
    """Build an embedding function instance from a dictionary specification.

    Args:
        spec: A dictionary with 'provider' and 'config' keys.
              Example: {
                  "provider": "openai",
                  "config": {
                      "api_key": "sk-...",
                      "model_name": "text-embedding-3-small"
                  }
              }

    Returns:
        An instance of the appropriate embedding function.

    Raises:
        ValueError: If the provider is not recognized.
    """
    provider_name = spec["provider"]
    if not provider_name:
        raise ValueError("Missing 'provider' key in specification")

    if provider_name not in PROVIDER_PATHS:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available providers: {list(PROVIDER_PATHS.keys())}"
        )

    provider_path = PROVIDER_PATHS[provider_name]
    try:
        provider_class = import_and_validate_definition(provider_path)
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Failed to import provider {provider_name}: {e}") from e

    provider_config = spec.get("config", {})

    if provider_name == "custom" and "embedding_callable" not in provider_config:
        raise ValueError("Custom provider requires 'embedding_callable' in config")

    provider = provider_class(**provider_config)
    return build_embedder_from_provider(provider)


@overload
def build_embedder(spec: BaseEmbeddingsProvider[T]) -> T: ...


@overload
def build_embedder(spec: AzureProviderSpec) -> OpenAIEmbeddingFunction: ...


@overload
def build_embedder(spec: BedrockProviderSpec) -> AmazonBedrockEmbeddingFunction: ...


@overload
def build_embedder(spec: CohereProviderSpec) -> CohereEmbeddingFunction: ...


@overload
def build_embedder(spec: CustomProviderSpec) -> EmbeddingFunction[Any]: ...


@overload
def build_embedder(
    spec: GenerativeAiProviderSpec,
) -> GoogleGenerativeAiEmbeddingFunction: ...


@overload
def build_embedder(spec: HuggingFaceProviderSpec) -> HuggingFaceEmbeddingFunction: ...


@overload
def build_embedder(spec: OllamaProviderSpec) -> OllamaEmbeddingFunction: ...


@overload
def build_embedder(spec: OpenAIProviderSpec) -> OpenAIEmbeddingFunction: ...


@overload
def build_embedder(
    spec: VertexAIProviderSpec,
) -> GoogleGenAIVertexEmbeddingFunction: ...


@overload
def build_embedder(spec: VoyageAIProviderSpec) -> VoyageAIEmbeddingFunction: ...


@overload
def build_embedder(spec: WatsonXProviderSpec) -> WatsonXEmbeddingFunction: ...


@overload
def build_embedder(
    spec: SentenceTransformerProviderSpec,
) -> SentenceTransformerEmbeddingFunction: ...


@overload
def build_embedder(spec: InstructorProviderSpec) -> InstructorEmbeddingFunction: ...


@overload
def build_embedder(spec: JinaProviderSpec) -> JinaEmbeddingFunction: ...


@overload
def build_embedder(spec: RoboflowProviderSpec) -> RoboflowEmbeddingFunction: ...


@overload
def build_embedder(spec: OpenCLIPProviderSpec) -> OpenCLIPEmbeddingFunction: ...


@overload
def build_embedder(spec: Text2VecProviderSpec) -> Text2VecEmbeddingFunction: ...


@overload
def build_embedder(spec: ONNXProviderSpec) -> ONNXMiniLM_L6_V2: ...


def build_embedder(spec):  # type: ignore[no-untyped-def]
    """Build an embedding function from either a provider spec or a provider instance.

    Args:
        spec: Either a provider specification dictionary or a provider instance.

    Returns:
        An embedding function instance. If a typed provider is passed, returns
        the specific embedding function type.

    Examples:
        # From dictionary specification
        embedder = build_embedder({
            "provider": "openai",
            "config": {"api_key": "sk-..."}
        })

        # From provider instance
        provider = OpenAIProvider(api_key="sk-...")
        embedder = build_embedder(provider)
    """
    if isinstance(spec, BaseEmbeddingsProvider):
        return build_embedder_from_provider(spec)
    return build_embedder_from_dict(spec)


# Backward compatibility alias
get_embedding_function = build_embedder
