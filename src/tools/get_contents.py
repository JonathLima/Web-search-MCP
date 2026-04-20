from __future__ import annotations

import asyncio
import logging
from typing import Optional

from src.tools.web_fetch import fetch_page
from src.utils.highlights import extract_highlights
from src.utils.summarizer import extractive_summary

logger = logging.getLogger(__name__)

async def _fetch_single_url(
    url: str,
    highlight_query: Optional[str],
    highlight_sentences: int,
    enable_summary: bool,
    max_tokens: int,
) -> dict:
    try:
        content = await fetch_page(url, max_tokens=max_tokens)

        title = ""
        page_content = ""
        if "## " in content:
            parts = content.split("## ", 2)
            if len(parts) > 1:
                title = parts[1].split("\n")[0].strip()

        lines = content.split("\n")
        content_lines = [line for line in lines if not line.startswith("#") and line.strip()]
        page_content = "\n".join(content_lines)

        highlights = []
        if highlight_query:
            highlights = extract_highlights(
                page_content, highlight_query, num_sentences=highlight_sentences
            )

        summary = None
        if enable_summary:
            summary = extractive_summary(page_content, num_sentences=3)

        return {
            "url": url,
            "statusCode": 200,
            "title": title,
            "content": page_content,
            "highlights": highlights,
            "summary": summary,
        }
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return {
            "url": url,
            "statusCode": 500,
            "title": "",
            "content": "",
            "highlights": [],
            "summary": None,
        }

async def get_contents(
    urls: list[str],
    highlight_query: Optional[str] = None,
    highlight_sentences: int = 3,
    enableSummary: bool = False,
    max_tokens: int = 8000,
) -> str:
    logger.info(f"get_contents: {len(urls)} URLs")

    semaphore = asyncio.Semaphore(3)

    async def bounded_fetch(url: str):
        async with semaphore:
            return await _fetch_single_url(
                url, highlight_query, highlight_sentences, enableSummary, max_tokens
            )

    results = await asyncio.gather(*[bounded_fetch(u) for u in urls])

    lines = [f"## 📄 Contents ({len(results)} pages)"]
    lines.append("")

    for i, item in enumerate(results, 1):
        lines.append(f"### {i}. {item['title'] or item['url']}")
        lines.append(f"**URL:** {item['url']}")
        lines.append(f"**Status:** {item['statusCode']}")

        if item["highlights"]:
            lines.append("**Highlights:**")
            for h in item["highlights"]:
                lines.append(f"> {h}")

        if item["summary"]:
            lines.append(f"**Summary:** {item['summary']}")

        lines.append("")
        lines.append(f"**Content:**\n{item['content'][:2000]}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)