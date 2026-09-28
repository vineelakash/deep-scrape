# -*- coding: utf-8 -*-
"""
DeepScrape MCP Server — expose doctor/status as MCP tool.

Run: python -m deep_scrape.integrations.mcp_server

DeepScrape is an autonomous scraping, intelligence, and doctor tool.
"""

import asyncio
import json
import sys

from deep_scrape.config import Config
from deep_scrape.core import DeepScrape
from deep_scrape.utils.text import scrub_url_credentials

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    HAS_MCP = True
except ImportError:
    HAS_MCP = False


def create_server():
    if not HAS_MCP:
        print(
            "MCP not installed. Install: python -m pip install "
            "'deep-scrape[mcp] @ "
            "https://github.com/vineelakash/deep-scrape/archive/main.zip'",
            file=sys.stderr,
        )
        sys.exit(1)

    server = Server("deep-scrape")
    config = Config(read_only=True)
    eyes = DeepScrape(config)

    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="get_status",
                 description="Get DeepScrape status: which channels are installed and active.",
                 inputSchema={"type": "object", "properties": {}}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "get_status":
                result = eyes.doctor_report()
            else:
                result = f"Unknown tool: {name}"

            text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, (dict, list)) else str(result)
            return [TextContent(type="text", text=text)]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error: {scrub_url_credentials(e)}",
                )
            ]

    return server


async def main():
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
