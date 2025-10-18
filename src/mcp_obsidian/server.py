import logging
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

# Create FastMCP server
mcp_server_host = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
mcp_server_port = int(os.getenv("MCP_SERVER_PORT", 8080))

mcp = FastMCP("mcp-obsidian", host=mcp_server_host, port=mcp_server_port)

from .tools import init_tools


def main():
    """Run the MCP server."""
    logger.info("Starting MCP Obsidian server")
    init_tools(mcp)
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
