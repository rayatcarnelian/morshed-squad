"""Morshed Squad events system for monitoring and extending agent behavior.

This module provides the event infrastructure that allows users to:
- Monitor agent, task, and crew execution
- Track memory operations and performance
- Build custom logging and analytics
- Extend Morshed Squad with custom event handlers
- Declare handler dependencies for ordered execution
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from morshed_squad.events.base_event_listener import BaseEventListener
from morshed_squad.events.depends import Depends
from morshed_squad.events.event_bus import crewai_event_bus
from morshed_squad.events.handler_graph import CircularDependencyError
from morshed_squad.events.types.crew_events import (
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
    CrewKickoffStartedEvent,
    CrewTestCompletedEvent,
    CrewTestFailedEvent,
    CrewTestResultEvent,
    CrewTestStartedEvent,
    CrewTrainCompletedEvent,
    CrewTrainFailedEvent,
    CrewTrainStartedEvent,
)
from morshed_squad.events.types.flow_events import (
    FlowCreatedEvent,
    FlowEvent,
    FlowFinishedEvent,
    FlowPlotEvent,
    FlowStartedEvent,
    HumanFeedbackReceivedEvent,
    HumanFeedbackRequestedEvent,
    MethodExecutionFailedEvent,
    MethodExecutionFinishedEvent,
    MethodExecutionStartedEvent,
)
from morshed_squad.events.types.knowledge_events import (
    KnowledgeQueryCompletedEvent,
    KnowledgeQueryFailedEvent,
    KnowledgeQueryStartedEvent,
    KnowledgeRetrievalCompletedEvent,
    KnowledgeRetrievalStartedEvent,
    KnowledgeSearchQueryFailedEvent,
)
from morshed_squad.events.types.llm_events import (
    LLMCallCompletedEvent,
    LLMCallFailedEvent,
    LLMCallStartedEvent,
    LLMStreamChunkEvent,
)
from morshed_squad.events.types.llm_guardrail_events import (
    LLMGuardrailCompletedEvent,
    LLMGuardrailStartedEvent,
)
from morshed_squad.events.types.logging_events import (
    AgentLogsExecutionEvent,
    AgentLogsStartedEvent,
)
from morshed_squad.events.types.mcp_events import (
    MCPConnectionCompletedEvent,
    MCPConnectionFailedEvent,
    MCPConnectionStartedEvent,
    MCPToolExecutionCompletedEvent,
    MCPToolExecutionFailedEvent,
    MCPToolExecutionStartedEvent,
)
from morshed_squad.events.types.memory_events import (
    MemoryQueryCompletedEvent,
    MemoryQueryFailedEvent,
    MemoryQueryStartedEvent,
    MemoryRetrievalCompletedEvent,
    MemoryRetrievalFailedEvent,
    MemoryRetrievalStartedEvent,
    MemorySaveCompletedEvent,
    MemorySaveFailedEvent,
    MemorySaveStartedEvent,
)
from morshed_squad.events.types.reasoning_events import (
    AgentReasoningCompletedEvent,
    AgentReasoningFailedEvent,
    AgentReasoningStartedEvent,
    ReasoningEvent,
)
from morshed_squad.events.types.task_events import (
    TaskCompletedEvent,
    TaskEvaluationEvent,
    TaskFailedEvent,
    TaskStartedEvent,
)
from morshed_squad.events.types.tool_usage_events import (
    ToolExecutionErrorEvent,
    ToolSelectionErrorEvent,
    ToolUsageErrorEvent,
    ToolUsageEvent,
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
    ToolValidateInputErrorEvent,
)


if TYPE_CHECKING:
    from morshed_squad.events.types.agent_events import (
        AgentEvaluationCompletedEvent,
        AgentEvaluationFailedEvent,
        AgentEvaluationStartedEvent,
        AgentExecutionCompletedEvent,
        AgentExecutionErrorEvent,
        AgentExecutionStartedEvent,
        LiteAgentExecutionCompletedEvent,
        LiteAgentExecutionErrorEvent,
        LiteAgentExecutionStartedEvent,
    )


__all__ = [
    "AgentEvaluationCompletedEvent",
    "AgentEvaluationFailedEvent",
    "AgentEvaluationStartedEvent",
    "AgentExecutionCompletedEvent",
    "AgentExecutionErrorEvent",
    "AgentExecutionStartedEvent",
    "AgentLogsExecutionEvent",
    "AgentLogsStartedEvent",
    "AgentReasoningCompletedEvent",
    "AgentReasoningFailedEvent",
    "AgentReasoningStartedEvent",
    "BaseEventListener",
    "CircularDependencyError",
    "CrewKickoffCompletedEvent",
    "CrewKickoffFailedEvent",
    "CrewKickoffStartedEvent",
    "CrewTestCompletedEvent",
    "CrewTestFailedEvent",
    "CrewTestResultEvent",
    "CrewTestStartedEvent",
    "CrewTrainCompletedEvent",
    "CrewTrainFailedEvent",
    "CrewTrainStartedEvent",
    "Depends",
    "FlowCreatedEvent",
    "FlowEvent",
    "FlowFinishedEvent",
    "FlowPlotEvent",
    "FlowStartedEvent",
    "HumanFeedbackReceivedEvent",
    "HumanFeedbackRequestedEvent",
    "KnowledgeQueryCompletedEvent",
    "KnowledgeQueryFailedEvent",
    "KnowledgeQueryStartedEvent",
    "KnowledgeRetrievalCompletedEvent",
    "KnowledgeRetrievalStartedEvent",
    "KnowledgeSearchQueryFailedEvent",
    "LLMCallCompletedEvent",
    "LLMCallFailedEvent",
    "LLMCallStartedEvent",
    "LLMGuardrailCompletedEvent",
    "LLMGuardrailStartedEvent",
    "LLMStreamChunkEvent",
    "LiteAgentExecutionCompletedEvent",
    "LiteAgentExecutionErrorEvent",
    "LiteAgentExecutionStartedEvent",
    "MCPConnectionCompletedEvent",
    "MCPConnectionFailedEvent",
    "MCPConnectionStartedEvent",
    "MCPToolExecutionCompletedEvent",
    "MCPToolExecutionFailedEvent",
    "MCPToolExecutionStartedEvent",
    "MemoryQueryCompletedEvent",
    "MemoryQueryFailedEvent",
    "MemoryQueryStartedEvent",
    "MemoryRetrievalCompletedEvent",
    "MemoryRetrievalFailedEvent",
    "MemoryRetrievalStartedEvent",
    "MemorySaveCompletedEvent",
    "MemorySaveFailedEvent",
    "MemorySaveStartedEvent",
    "MethodExecutionFailedEvent",
    "MethodExecutionFinishedEvent",
    "MethodExecutionStartedEvent",
    "ReasoningEvent",
    "TaskCompletedEvent",
    "TaskEvaluationEvent",
    "TaskFailedEvent",
    "TaskStartedEvent",
    "ToolExecutionErrorEvent",
    "ToolSelectionErrorEvent",
    "ToolUsageErrorEvent",
    "ToolUsageEvent",
    "ToolUsageFinishedEvent",
    "ToolUsageStartedEvent",
    "ToolValidateInputErrorEvent",
    "_extension_exports",
    "crewai_event_bus",
]

_AGENT_EVENT_MAPPING = {
    "AgentEvaluationCompletedEvent": "morshed_squad.events.types.agent_events",
    "AgentEvaluationFailedEvent": "morshed_squad.events.types.agent_events",
    "AgentEvaluationStartedEvent": "morshed_squad.events.types.agent_events",
    "AgentExecutionCompletedEvent": "morshed_squad.events.types.agent_events",
    "AgentExecutionErrorEvent": "morshed_squad.events.types.agent_events",
    "AgentExecutionStartedEvent": "morshed_squad.events.types.agent_events",
    "LiteAgentExecutionCompletedEvent": "morshed_squad.events.types.agent_events",
    "LiteAgentExecutionErrorEvent": "morshed_squad.events.types.agent_events",
    "LiteAgentExecutionStartedEvent": "morshed_squad.events.types.agent_events",
}

_extension_exports: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """Lazy import for agent events and registered extensions."""
    if name in _AGENT_EVENT_MAPPING:
        import importlib

        module_path = _AGENT_EVENT_MAPPING[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)

    if name in _extension_exports:
        import importlib

        value = _extension_exports[name]
        if isinstance(value, str):
            module_path, _, attr_name = value.rpartition(".")
            if module_path:
                module = importlib.import_module(module_path)
                return getattr(module, attr_name)
            return importlib.import_module(value)
        return value

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
