"""OpenAI agent tool adapter for Morshed Squad tool integration.

This module contains the OpenAIAgentToolAdapter class that converts Morshed Squad tools
to OpenAI Assistant-compatible format using the agents library.
"""

from collections.abc import Awaitable
import inspect
import json
from typing import Any, cast

from morshed_squad.agents.agent_adapters.base_tool_adapter import BaseToolAdapter
from morshed_squad.agents.agent_adapters.openai_agents.protocols import (
    OpenAIFunctionTool,
    OpenAITool,
)
from morshed_squad.tools import BaseTool
from morshed_squad.utilities.import_utils import require
from morshed_squad.utilities.pydantic_schema_utils import force_additional_properties_false
from morshed_squad.utilities.string_utils import sanitize_tool_name


agents_module = cast(
    Any,
    require(
        "agents",
        purpose="OpenAI agents functionality",
    ),
)
FunctionTool = agents_module.FunctionTool
Tool = agents_module.Tool


class OpenAIAgentToolAdapter(BaseToolAdapter):
    """Adapter for OpenAI Assistant tools.

    Converts Morshed Squad BaseTool instances to OpenAI Assistant FunctionTool format
    that can be used by OpenAI agents.
    """

    def __init__(self, tools: list[BaseTool] | None = None) -> None:
        """Initialize the tool adapter.

        Args:
            tools: Optional list of Morshed Squad tools to adapt.
        """
        super().__init__()
        self.original_tools: list[BaseTool] = tools or []
        self.converted_tools: list[OpenAITool] = []

    def configure_tools(self, tools: list[BaseTool]) -> None:
        """Configure tools for the OpenAI Assistant.

        Merges provided tools with original tools and converts them to
        OpenAI Assistant format.

        Args:
            tools: List of Morshed Squad tools to configure.
        """
        if self.original_tools:
            all_tools: list[BaseTool] = tools + self.original_tools
        else:
            all_tools = tools
        if all_tools:
            self.converted_tools = self._convert_tools_to_openai_format(all_tools)

    @staticmethod
    def _convert_tools_to_openai_format(
        tools: list[BaseTool] | None,
    ) -> list[OpenAITool]:
        """Convert Morshed Squad tools to OpenAI Assistant tool format.

        Args:
            tools: List of Morshed Squad tools to convert.

        Returns:
            List of OpenAI Assistant FunctionTool instances.
        """
        if not tools:
            return []

        def create_tool_wrapper(tool: BaseTool) -> Any:
            """Create a wrapper function that handles the OpenAI function tool interface.

            Args:
                tool: The Morshed Squad tool to wrap.

            Returns:
                Async wrapper function for OpenAI agent integration.
            """

            async def wrapper(context_wrapper: Any, arguments: Any) -> Any:
                """Wrapper function to adapt Morshed Squad tool calls to OpenAI format.

                Args:
                    context_wrapper: OpenAI context wrapper.
                    arguments: Tool arguments from OpenAI.

                Returns:
                    Tool execution result.
                """
                # Get the parameter name from the schema
                param_name: str = next(
                    iter(tool.args_schema.model_json_schema()["properties"].keys())
                )

                # Handle different argument types
                args_dict: dict[str, Any]
                if isinstance(arguments, dict):
                    args_dict = arguments
                elif isinstance(arguments, str):
                    try:
                        args_dict = json.loads(arguments)
                    except json.JSONDecodeError:
                        args_dict = {param_name: arguments}
                else:
                    args_dict = {param_name: str(arguments)}

                # Run the tool with the processed arguments
                output: Any | Awaitable[Any] = tool._run(**args_dict)

                # Await if the tool returned a coroutine
                if inspect.isawaitable(output):
                    result: Any = await output
                else:
                    result = output

                # Ensure the result is JSON serializable
                if isinstance(result, (dict, list, str, int, float, bool, type(None))):
                    return result
                return str(result)

            return wrapper

        openai_tools: list[OpenAITool] = []
        for tool in tools:
            schema: dict[str, Any] = tool.args_schema.model_json_schema()

            schema = force_additional_properties_false(schema)

            schema.update({"type": "object"})

            openai_tool: OpenAIFunctionTool = cast(
                OpenAIFunctionTool,
                FunctionTool(
                    name=sanitize_tool_name(tool.name),
                    description=tool.description,
                    params_json_schema=schema,
                    on_invoke_tool=create_tool_wrapper(tool),
                ),
            )
            openai_tools.append(openai_tool)

        return openai_tools
