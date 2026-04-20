import pytest
from src.utils.query_expander import QueryExpander, expand_query

def test_expand_instant_single_variation():
    result = expand_query("Python 3.13 release", "instant")
    assert len(result) == 1
    assert result[0]["query"] == "Python 3.13 release"

def test_expand_auto_single_variation():
    result = expand_query("Python 3.13 release", "auto")
    assert len(result) == 1

def test_expand_deep_lite_variations():
    result = expand_query("Python 3.13 release", "deep_lite")
    assert len(result) == 5

def test_expand_deep_variations():
    result = expand_query("Python 3.13 release", "deep")
    assert len(result) >= 5

def test_expand_deep_reasoning_variations():
    result = expand_query("Python 3.13 release", "deep_reasoning")
    assert len(result) >= 7

def test_expand_query_includes_metadata():
    result = expand_query("Python 3.13 release", "deep")
    for item in result:
        assert "query" in item
        assert "purpose" in item
        assert "weight" in item

def test_expander_class_reproducible():
    expander = QueryExpander()
    r1 = expander.expand("Python release", "deep")
    r2 = expander.expand("Python release", "deep")
    assert r1 == r2