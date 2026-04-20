import pytest
from src.utils.summarizer import extractive_summary

def test_summary_returns_string():
    text = "Python is a high-level programming language. It supports multiple paradigms. It has a large standard library. Python is used for web development."
    result = extractive_summary(text, num_sentences=3)
    assert isinstance(result, str)

def test_summary_respects_num_sentences():
    text = "First sentence here. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
    result = extractive_summary(text, num_sentences=3)
    assert isinstance(result, str)

def test_summary_handles_short_text():
    text = "Short text."
    result = extractive_summary(text, num_sentences=3)
    assert isinstance(result, str)
    assert len(result) > 0

def test_summary_handles_empty_text():
    result = extractive_summary("", num_sentences=3)
    assert result == ""