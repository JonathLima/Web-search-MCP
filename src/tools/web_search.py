from __future__ import annotations

import logging

import httpx

from src.config import get_searxng_config
from src.errors import (
    SearchConnectionError,
    SearchHTTPError,
    SearchTimeoutError,
)
from src.models import SearchRequest, SearchResult, SearchResponse, ToolErrorResponse
from src.utils.dedup import deduplicate_and_score

logger = logging.getLogger(__name__)

try:
    from flashrank import Ranker, RerankRequest
    FLASHRANK_AVAILABLE = True
except ImportError:
    FLASHRANK_AVAILABLE = False
    logger.warning("flashrank not available, skipping AI reranking")

_ranker = None

def _get_ranker():
    global _ranker
    if _ranker is None and FLASHRANK_AVAILABLE:
        try:
            _ranker = Ranker()
            logger.info("FlashRank Ranker initialized")
        except Exception as exc:
            logger.warning("Failed to initialize FlashRank: %s", exc)
    return _ranker

def _rerank_with_flashrank(query: str, results: list[SearchResult]) -> list[SearchResult]:
    if not FLASHRANK_AVAILABLE or len(results) < 2:
        return results
    
    ranker = _get_ranker()
    if ranker is None:
        return results
    
    try:
        passages = [
            {
                "id": idx,
                "text": f"{r.title}. {r.snippet}" if r.snippet else r.title,
            }
            for idx, r in enumerate(results)
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        reranked = ranker.rerank(rerank_request)
        
        id_to_result = {r.id: r for r in results}
        reranked_results = [id_to_result[r["id"]] for r in reranked if r["id"] in id_to_result]
        
        logger.info("FlashRank reranked %d results", len(results))
        return reranked_results
        
    except Exception as exc:
        logger.warning("FlashRank reranking failed: %s", exc)
        return results

def _build_search_params(request: SearchRequest) -> dict[str, str]:
    config = get_searxng_config()

    params: dict[str, str] = {
        "q": request.query,
        "format": "json",
        "pageno": "1",
    }

    if request.categories:
        params["categories"] = request.categories
    else:
        params["categories"] = config.default_category

    if request.time_range:
        params["time_range"] = request.time_range

    params["language"] = "en"

    if request.safesearch is not None:
        params["safesearch"] = request.safesearch
    else:
        params["safesearch"] = config.safesearch

    params["engines"] = ",".join(config.engine_list)

    return params

async def _fetch_from_searxng(
    params: dict[str, str],
    timeout: float,
) -> tuple[list[dict], str]:
    config = get_searxng_config()

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(config.search_url, params=params)
        response.raise_for_status()
        data = response.json()

    raw_results: list[dict] = data.get("results", [])
    engines_str = params.get("engines", "")

    return raw_results, engines_str

_TIER_LABELS = {
    1: "🟢 Tier 1 — Official/Definitive (GitHub, Docs, .gov, .edu)",
    2: "🔵 Tier 2 — Authoritative (Wikipedia, Stack Overflow, Journals)",
    3: "🟡 Tier 3 — Reference (Technical Blogs, News, Reputable Orgs)",
    4: "⚪ Tier 4 — Other/General (SEO sites, Reddit, General Blogs)",
}

def _format_search_response(response: SearchResponse) -> str:
    if not response.results:
        lines: list[str] = []
        lines.append("## ❌ No Results Found")
        lines.append("")
        lines.append(f"No search results were found for the query: **{response.query}**.")
        lines.append("")
        lines.append(
            "**Suggestions to improve results:**\n"
            "- Try rephrasing your query with different keywords\n"
            "- Use broader or more specific search terms\n"
            "- Try a different time range (e.g., `time_range='month'`)\n"
            "- Try a different category (e.g., `categories='news'`)"
        )
        return "\n".join(lines)

    lines = []
    lines.append(f"## 🔍 Search Results ({len(response.results)} sources discovered)")
    lines.append("")
    lines.append(
        f"**Query:** `{response.query}` | "
        f"**Engines:** {', '.join(response.engines_used)}"
    )
    lines.append("")
    lines.append("> ⚠️ **IMPORTANT: Snippets are often cached and dates below may be stale.**")
    lines.append("> Always use `fetch_page(url)` to verify exact dates, versions, and facts.")
    lines.append("")

    for idx, result in enumerate(response.results, start=1):
        tier_label = _TIER_LABELS.get(result.domain_tier, "⚪ Tier 4 — Other")

        lines.append(f"### {idx}. {result.title}")
        lines.append(f"**URL:** {result.url_str}")
        if result.snippet:
            lines.append(f"**Snippet:** {result.snippet}")
        
        lines.append(
            f"**Authority:** {tier_label} | "
            f"**Reliability Score:** {result.score:.1f}/100"
        )

        indicators = []
        if result.domain_tier == 1:
            indicators.append("💎 **OFFICIAL SOURCE**")
        if result.has_specific_data:
            indicators.append("🔢 **Contains Specific Data** (Versions/Dates/Prices)")
        if result.vagueness_detected:
            indicators.append("🌫️ **Vague Language Detected**")
        
        if indicators:
            lines.append(f"**Indicators:** {' | '.join(indicators)}")

        if result.published_date:
            lines.append(f"**Engine Cache Date:** {result.published_date} (⚠️ verify on-page)")
        lines.append("")

    lines.append("---")
    lines.append(
        "## 🛠️ OPERATIONAL GUIDELINES FOR THE RESEARCHER\n"
        "\n"
        "1. **Prioritize 🟢 Tier 1 and 🔵 Tier 2 sources.** They are the 'Level 1 Truth' (official docs/GitHub/Academic).\n"
        "\n"
        "2. **NEVER trust a date or version number from a snippet.** Use `fetch_page(url)` on the top 1-2 authoritative results to find the actual release date/version in the current content.\n"
        "\n"
        "3. **Cross-reference facts.** If 🟡 Tier 3 or ⚪ Tier 4 sources conflict with 🟢 Tier 1, always follow the Tier 1 source.\n"
        "\n"
        "4. **If information is missing** → try `site_search` on a specific authoritative domain (e.g., `github.com` or `docs.python.org`)."
    )

    return "\n".join(lines)

def _format_error(error: ToolErrorResponse) -> str:
    lines = []
    lines.append(f"## ⚠️ Search Error: `{error.error_code}`")
    lines.append("")
    lines.append(f"**{error.message}**")
    lines.append("")
    lines.append(f"**How to proceed:** {error.retry_guidance}")
    lines.append("")
    return "\n".join(lines)

async def get_raw_searxng_results(
    query: str,
    time_range: str | None = None,
    categories: str | None = None,
    safesearch: str | None = None,
    limit: int = 10,
) -> list[dict]:
    try:
        request = SearchRequest(
            query=query,
            time_range=time_range,
            categories=categories,
            safesearch=safesearch,
            limit=limit,
        )
    except Exception:
        return []

    config = get_searxng_config()
    params = _build_search_params(request)
    try:
        raw_results, _ = await _fetch_from_searxng(params, timeout=config.timeout)
        return raw_results
    except Exception:
        return []

async def web_search(
    query: str,
    time_range: str | None = None,
    categories: str | None = None,
    safesearch: str | None = None,
    limit: int = 10,
) -> str:
    logger.info("web_search called: query=%r, time_range=%r, categories=%r, limit=%d",
                query, time_range, categories, limit)

    try:
        request = SearchRequest(
            query=query,
            time_range=time_range,
            categories=categories,
            safesearch=safesearch,
            limit=limit,
        )
    except Exception as exc:
        error = ToolErrorResponse(
            error_code="SEARCH_VALIDATION_ERROR",
            message=f"Invalid search parameters: {exc}",
            retry_guidance=(
                "Ensure query is a non-empty string (max 500 chars), "
                "limit is between 1-20, and time_range/categories/safesearch "
                "use valid values."
            ),
            markdown="",
        )
        error.markdown = _format_error(error)
        return error.markdown

    config = get_searxng_config()

    params = _build_search_params(request)

    try:
        raw_results, engines_used = await _fetch_from_searxng(
            params, timeout=config.timeout
        )
    except httpx.ConnectError as exc:
        logger.error("Cannot connect to SearxNG at %s — %s", config.host, exc)
        error = SearchConnectionError(
            f"Unable to connect to the search service at {config.host}."
        )
        return _format_error(ToolErrorResponse(
            error_code=error.error_code,
            message=str(error),
            retry_guidance=error.retry_guidance,
            markdown="",
        ))
    except httpx.TimeoutException as exc:
        logger.error("SearxNG request timed out — %s", exc)
        error = SearchTimeoutError(
            f"Search request timed out after {config.timeout}s. "
            f"Query: {query!r}"
        )
        return _format_error(ToolErrorResponse(
            error_code=error.error_code,
            message=str(error),
            retry_guidance=error.retry_guidance,
            markdown="",
        ))
    except httpx.HTTPStatusError as exc:
        logger.error("SearxNG returned HTTP %s — %s", exc.response.status_code, exc)
        error = SearchHTTPError(
            f"Search service returned HTTP {exc.response.status_code}.",
            status_code=exc.response.status_code,
        )
        return _format_error(ToolErrorResponse(
            error_code=error.error_code,
            message=str(error),
            retry_guidance=error.retry_guidance,
            markdown="",
        ))
    except Exception as exc:
        logger.error("Unexpected error in web_search: %s", exc, exc_info=True)
        return _format_error(ToolErrorResponse(
            error_code="SEARCH_UNKNOWN_ERROR",
            message=f"An unexpected error occurred during search: {exc}",
            retry_guidance="Try again with a different query or check server logs.",
            markdown="",
        ))

    total_found = len(raw_results)
    engines_list = [e.strip() for e in engines_used.split(",") if e.strip()] if engines_used else []

    results = deduplicate_and_score(raw_results, engines_list)

    if FLASHRANK_AVAILABLE and len(results) >= 2:
        results = _rerank_with_flashrank(query, results)

    results = results[: request.limit]

    if not results:
        logger.info("No results found for query: %r", query)
        response = SearchResponse(
            query=query,
            results=[],
            total_found=total_found,
            engines_used=engines_list,
            markdown="",
        )
        response.markdown = _format_search_response(response)
        return response.markdown

    response = SearchResponse(
        query=query,
        results=results,
        total_found=total_found,
        engines_used=engines_list,
        markdown="",
    )
    response.markdown = _format_search_response(response)

    logger.info(
        "web_search complete: query=%r, results=%d/%d",
        query,
        len(response.results),
        total_found,
    )

    return response.markdown
