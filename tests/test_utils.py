from src.utils import truncate_response


def test_short_text_is_returned_unchanged():
    assert truncate_response("hello", max_length=100) == "hello"


def test_text_at_exact_limit_is_unchanged():
    text = "x" * 100
    assert truncate_response(text, max_length=100) == text


def test_oversized_text_is_truncated_with_warning():
    text = "x" * 500
    # Budget comfortably larger than the warning, so real slicing happens.
    out = truncate_response(text, max_length=300)
    assert len(out) == 300
    assert out.endswith("received.]")
    assert "WARNING" in out


def test_limit_smaller_than_warning_still_returns_only_the_warning():
    text = "x" * 500
    out = truncate_response(text, max_length=10)
    # keep == 0, so the output is just the (longer) warning, never the raw text.
    assert "x" not in out
    assert "WARNING" in out
