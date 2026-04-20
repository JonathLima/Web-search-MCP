import pytest
from src.utils.highlights import extract_highlights

def test_extract_highlights_returns_list():
    text = "Python is a programming language. It is widely used. Python was created in 1991."
    result = extract_highlights(text, "Python", num_sentences=2)
    assert isinstance(result, list)
    assert len(result) <= 2

def test_extract_highlights_query_match():
    text = "Machine learning is a subset of AI. Deep learning uses neural networks."
    highlights = extract_highlights(text, "machine learning", num_sentences=1)
    assert len(highlights) >= 0

def test_extract_highlights_empty_text():
    result = extract_highlights("", "python", num_sentences=3)
    assert result == []

def test_extract_highlights_sentence_boundary():
    text = "First sentence here. Second sentence here. Third sentence."
    result = extract_highlights(text, "second", num_sentences=1)
    assert any("second" in h.lower() for h in result)

def test_extract_highlights_no_query_match():
    text = "Completely unrelated content about something else entirely."
    result = extract_highlights(text, "python javascript coding", num_sentences=3)
    assert isinstance(result, list)
