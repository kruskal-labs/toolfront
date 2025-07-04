import asyncio
import logging
from typing import Literal

import click
from mcp.server.fastmcp import FastMCP

from toolfront.storage import save_api_key, save_connections
from toolfront.tools import (
    inspect_endpoint,
    inspect_table,
    query_database,
    request_api,
    sample_table,
    search_endpoints,
    search_queries,
    search_tables,
)

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)

logging.info("Starting ToolFront MCP server")


async def get_mcp(urls: tuple[str, ...], api_key: str | None = None) -> FastMCP:
    clean_urls = await save_connections(urls)

    mcp = FastMCP("ToolFront MCP server")

    async def discover() -> list[str]:
        """
        Lists all available datasources.

        Discover Instructions:
        1. Use this tool to list all available datasources.
        2. Passwords and secrets are obfuscated in the URL for security, but you can use the URLs as-is in other tools.
        """
        return clean_urls

    mcp.add_tool(discover)
    mcp.add_tool(inspect_endpoint)
    mcp.add_tool(inspect_table)
    mcp.add_tool(query_database)
    mcp.add_tool(request_api)
    mcp.add_tool(sample_table)
    mcp.add_tool(search_endpoints)
    mcp.add_tool(search_tables)

    if api_key:
        save_api_key(api_key)
        mcp.add_tool(search_queries)

    return mcp


@click.command()
@click.option("--api-key", envvar="KRUSKAL_API_KEY", help="API key for authentication")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport mode for MCP server")
@click.argument("urls", nargs=-1)
def main(api_key: str | None = None, transport: Literal["stdio", "sse"] = "stdio", urls: tuple[str, ...] = ()) -> None:
    logger.info("Starting MCP server")
    mcp_instance = asyncio.run(get_mcp(urls, api_key))
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    main()
