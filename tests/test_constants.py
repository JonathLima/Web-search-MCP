import pytest
from src.constants import (
    SEARCH_TYPE_CONFIG, CATEGORY_DOMAINS, CATEGORY_ENGINES,
    DOMAIN_TIER_1_LIST, DOMAIN_TIER_2_LIST, DOMAIN_TIER_3_LIST,
    VAGUE_PHRASES, SPECIFIC_DATA_PATTERNS,
)

def test_search_type_config_has_all_types():
    expected = {"auto", "fast", "instant", "deep_lite", "deep", "deep_reasoning"}
    assert set(SEARCH_TYPE_CONFIG.keys()) == expected

def test_search_type_config_deep_has_variations():
    cfg = SEARCH_TYPE_CONFIG["deep"]
    assert cfg.query_variations == 5
    assert cfg.enable_rerank is True
    assert cfg.enable_summary is True

def test_category_domains_has_all_categories():
    expected = {"news", "research_paper", "company", "people", "financial_report",
                "product", "personal_site", "code", "video", "image", "general"}
    assert set(CATEGORY_DOMAINS.keys()) == expected

def test_tier1_includes_official_domains():
    assert "github.com" in DOMAIN_TIER_1_LIST
    assert "arxiv.org" in DOMAIN_TIER_1_LIST

def test_tier3_includes_blogs():
    assert "medium.com" in DOMAIN_TIER_3_LIST