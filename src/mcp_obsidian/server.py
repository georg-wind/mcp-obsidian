import logging
import os
from collections.abc import Sequence
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Load environment variables
load_dotenv()

from . import tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

# Validate API key
api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError(f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}")

# Create FastMCP server
host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
port = int(os.getenv("MCP_SERVER_PORT", 8080))
mcp = FastMCP("mcp-obsidian", host=host, port=port)

# Initialize tool handlers
tool_handlers = {}


def add_tool_handler(tool_class: tools.ToolHandler):
    global tool_handlers
    tool_handlers[tool_class.name] = tool_class


# Register all tool handlers
add_tool_handler(tools.ListFilesInDirToolHandler())
add_tool_handler(tools.ListFilesInVaultToolHandler())
add_tool_handler(tools.GetFileContentsToolHandler())
add_tool_handler(tools.SearchToolHandler())
add_tool_handler(tools.PatchContentToolHandler())
add_tool_handler(tools.AppendContentToolHandler())
add_tool_handler(tools.PutContentToolHandler())
add_tool_handler(tools.DeleteFileToolHandler())
add_tool_handler(tools.ComplexSearchToolHandler())
add_tool_handler(tools.BatchGetFileContentsToolHandler())
add_tool_handler(tools.PeriodicNotesToolHandler())
add_tool_handler(tools.RecentPeriodicNotesToolHandler())
add_tool_handler(tools.RecentChangesToolHandler())
add_tool_handler(tools.GetActiveNoteToolHandler())
add_tool_handler(tools.AppendToActiveToolHandler())
add_tool_handler(tools.ReplaceActiveNoteToolHandler())
add_tool_handler(tools.PatchActiveNoteToolHandler())
add_tool_handler(tools.DeleteActiveNoteToolHandler())
add_tool_handler(tools.AppendToPeriodicToolHandler())
add_tool_handler(tools.ReplacePeriodicNoteToolHandler())
add_tool_handler(tools.PatchPeriodicNoteToolHandler())
add_tool_handler(tools.DeletePeriodicNoteToolHandler())
add_tool_handler(tools.ListCommandsToolHandler())
add_tool_handler(tools.ExecuteCommandToolHandler())
add_tool_handler(tools.OpenFileToolHandler())


# Create a closure to capture the handler
def make_tool_function(tool_handler):
    async def tool_function(**arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Dynamically created tool function."""
        try:
            return tool_handler.run_tool(arguments)
        except Exception as e:
            logger.error(f"Tool error: {str(e)}")
            raise RuntimeError(f"Caught Exception. Error: {str(e)}")

    return tool_function


# Register tools dynamically with FastMCP
for handler in tool_handlers.values():
    tool_description = handler.get_tool_description()

    # Register the tool with FastMCP
    tool_func = make_tool_function(handler)
    tool_func.__name__ = tool_description.name
    tool_func.__doc__ = tool_description.description

    # Use the low-level _add_tool method to register with custom schema
    mcp.add_tool(
        tool_func,
        name=tool_description.name,
        description=tool_description.description,
    )


def main():
    """Run the server with streamable HTTP transport."""
    logger.info("Starting MCP server using streamable HTTP transport")

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
