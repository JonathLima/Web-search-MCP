import pytest
from src.models import (
    SearchType, SearchCategory, SearchRequestAdvanced, SearchResultAdvanced,
    GetContentsRequest, ContentItem, AnswerRequest,
)

def test_search_type_enum_values():
    assert SearchType.AUTO == "auto"
    assert SearchType.DEEP_REASONING == "deep_reasoning"

def test_search_category_enum_values():
    assert SearchCategory.NEWS == "news"
    assert SearchCategory.RESEARCH_PAPER == "research_paper"
    assert SearchCategory.CODE == "code"

def test_search_request_advanced_defaults():
    req = SearchRequestAdvanced(query="test")
    assert req.type == SearchType.AUTO
    assert req.numResults == 10
    assert req.enableHighlights is True
    assert req.enableSummary is False
    assert req.additionalQueries is True

def test_search_request_advanced_full():
    req = SearchRequestAdvanced(
        query="python release",
        type=SearchType.DEEP,
        numResults=50,
        category=SearchCategory.RESEARCH_PAPER,
        includeDomains=["arxiv.org"],
        excludeDomains=["medium.com"],
        startPublishedDate="2024-01-01",
        endPublishedDate="2024-12-31",
        highlight_sentences=5,
    )
    assert req.type == SearchType.DEEP
    assert req.category == "research_paper"
    assert req.includeDomains == ["arxiv.org"]

def test_content_item_has_highlights():
    item = ContentItem(
        url="https://example.com",
        statusCode=200,
        title="Test",
        content="Full article text here",
        highlights=["First highlight", "Second highlight"],
        summary="Extractive summary here",
    )
    assert len(item.highlights) == 2
    assert item.summary == "Extractive summary here"

def test_answer_request_requires_urls():
    req = AnswerRequest(query="What is Python?", urls=["https://python.org"])
    assert len(req.urls) == 1