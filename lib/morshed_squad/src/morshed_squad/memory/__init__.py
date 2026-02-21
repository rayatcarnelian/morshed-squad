"""Memory module: unified Memory with LLM analysis and pluggable storage."""

from morshed_squad.memory.encoding_flow import EncodingFlow
from morshed_squad.memory.memory_scope import MemoryScope, MemorySlice
from morshed_squad.memory.types import (
    MemoryMatch,
    MemoryRecord,
    ScopeInfo,
    compute_composite_score,
    embed_text,
    embed_texts,
)
from morshed_squad.memory.unified_memory import Memory


__all__ = [
    "EncodingFlow",
    "Memory",
    "MemoryMatch",
    "MemoryRecord",
    "MemoryScope",
    "MemorySlice",
    "ScopeInfo",
    "compute_composite_score",
    "embed_text",
    "embed_texts",
]
