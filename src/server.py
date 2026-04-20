from __future__ import annotations

import logging
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from mcp.server.fastmcp import FastMCP

from src.config import get_server_config
from src.tools.web_search import web_search as do_web_search
from src.tools.web_fetch import fetch_page as do_fetch_page
from src.tools.site_search import site_search as do_site_search
from src.tools.web_search_advanced import web_search_advanced as do_web_search_advanced
from src.tools.get_contents import get_contents as do_get_contents
from src.tools.answer import answer as do_answer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

server_config = get_server_config()

mcp = FastMCP(
    name="Web Search & Fetch MCP",
    host=server_config.host,
    port=server_config.port,
)

class APIKeyMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        api_key = server_config.api_key
        if not api_key:
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not secrets.compare_digest(auth, f"Bearer {api_key}"):
            return Response(content="Unauthorized", status_code=401)

        return await call_next(request)

@mcp.tool()
async def web_search(
    query: str,
    time_range: str | None = None,
    categories: str | None = None,
    safesearch: str | None = None,
    limit: int = 10,
) -> str:
    return await do_web_search(
        query=query,
        time_range=time_range,
        categories=categories,
        safesearch=safesearch,
        limit=limit,
    )

@mcp.tool()
async def site_search(
    query: str,
    site: str,
    time_range: str | None = None,
    limit: int = 5,
) -> str:
    return await do_site_search(
        query=query,
        site=site,
        time_range=time_range,
        limit=limit,
    )

@mcp.tool()
async def fetch_page(url: str, max_tokens: int | None = None) -> str:
    return await do_fetch_page(url=url, max_tokens=max_tokens)

@mcp.tool()
async def web_search_advanced(
    query: str,
    type: str = "auto",
    numResults: int = 10,
    category: str | None = None,
    includeDomains: list[str] | None = None,
    excludeDomains: list[str] | None = None,
    startPublishedDate: str | None = None,
    endPublishedDate: str | None = None,
    startCrawlDate: str | None = None,
    endCrawlDate: str | None = None,
    includeText: list[str] | None = None,
    excludeText: list[str] | None = None,
    userLocation: dict | None = None,
    safesearch: int | None = None,
    enableHighlights: bool = True,
    highlight_sentences: int = 3,
    enableSummary: bool = False,
    additionalQueries: bool = True,
) -> str:
    return await do_web_search_advanced(
        query=query,
        type=type,
        numResults=numResults,
        category=category,
        includeDomains=includeDomains,
        excludeDomains=excludeDomains,
        startPublishedDate=startPublishedDate,
        endPublishedDate=endPublishedDate,
        startCrawlDate=startCrawlDate,
        endCrawlDate=endCrawlDate,
        includeText=includeText,
        excludeText=excludeText,
        userLocation=userLocation,
        safesearch=safesearch,
        enableHighlights=enableHighlights,
        highlight_sentences=highlight_sentences,
        enableSummary=enableSummary,
        additionalQueries=additionalQueries,
    )

@mcp.tool()
async def get_contents(
    urls: list[str],
    highlight_query: str | None = None,
    highlight_sentences: int = 3,
    enableSummary: bool = False,
    max_tokens: int = 8000,
) -> str:
    return await do_get_contents(
        urls=urls,
        highlight_query=highlight_query,
        highlight_sentences=highlight_sentences,
        enableSummary=enableSummary,
        max_tokens=max_tokens,
    )

@mcp.tool()
async def answer(query: str, urls: list[str]) -> str:
    return await do_answer(query=query, urls=urls)

def run_http() -> None:
    """Run server in Streamable HTTP mode (for remote clients - Zed compatible)."""
    logger.info(
        "MCP server starting on %s:%d (Streamable HTTP)",
        server_config.host,
        server_config.port,
    )
    mcp.run(transport="streamable-http")


def run_stdio() -> None:
    """Run server in STDIO mode (for Claude Desktop, Cursor, Zed, etc.)."""
    logger.info("MCP server starting in STDIO mode")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "http"

    if mode == "http":
        run_http()
    elif mode == "stdio":
        run_stdio()
    else:
        run_http()
