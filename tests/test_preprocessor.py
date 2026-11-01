import pytest
from app.services.preprocessor import preprocess, PreprocessedText

def test_preserve_original():
    raw = "  messy \t\t text  \r\n line 2"
    result = preprocess(raw)
    assert isinstance(result, PreprocessedText)
    assert result.original == raw

def test_normalize_line_breaks():
    raw = "Skills\r\n\r\n\r\n\r\nReact\r\nNode.js"
    result = preprocess(raw)
    assert "\r" not in result.cleaned
    assert "\n\n\n" not in result.cleaned
    assert "Skills\n\nReact\nNode.js" == result.cleaned

def test_collapse_multiple_spaces_and_tabs():
    raw = "Software    Engineer     at   Google"
    result = preprocess(raw)
    assert result.cleaned == "Software Engineer at Google"

def test_repair_spaced_out_characters():
    raw = "J O H N   S M I T H\nEmail : john.smith@email.com"
    result = preprocess(raw)
    assert "JOHN SMITH" in result.cleaned
    assert "john.smith@email.com" in result.cleaned

def test_preserve_unicode_and_special_chars():
    # Review Focus 3: Non-ASCII characters (accents, umlauts, CJK, symbols)
    raw = "René Müller | São Paulo, Brasil | C++ & C# Developer"
    result = preprocess(raw)
    assert "René Müller" in result.cleaned
    assert "São Paulo, Brasil" in result.cleaned
    assert "C++ & C#" in result.cleaned

def test_strip_trailing_and_leading_whitespace_per_line():
    raw = "  Line 1   \n   Line 2   \n\n   Line 3   "
    result = preprocess(raw)
    lines = result.cleaned.split("\n")
    for line in lines:
        assert line == line.strip()
