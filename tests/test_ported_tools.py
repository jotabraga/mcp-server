from unittest.mock import MagicMock, patch

from src.tools.fetch_skill import FetchSkillTool
from src.tools.read_webpage import ReadWebpageTool
from src.tools.search_web import SearchWebTool


# --- read_webpage ---

def test_read_webpage_rejects_negative_skip():
    out = ReadWebpageTool().execute(status_message="x", url="http://e.com", skip=-1)
    assert "cannot be negative" in out


def test_read_webpage_returns_metadata_and_content():
    resp = MagicMock()
    resp.text = "<html><body><p>Hello World</p></body></html>"
    resp.raise_for_status.return_value = None
    with patch("src.tools.read_webpage.requests.get", return_value=resp):
        out = ReadWebpageTool().execute(status_message="x", url="http://e.com")
    assert "WEBPAGE CONTENT" in out
    assert "Hello World" in out
    assert "Response is truncated: False" in out


# --- search_web ---

def test_search_web_formats_results():
    with patch("src.tools.search_web.DDGS") as ddgs_cls:
        ddgs = ddgs_cls.return_value
        ddgs.text.side_effect = [
            [{"title": "A", "href": "http://a", "body": "body a"}],
            [],
        ]
        out = SearchWebTool().execute(status_message="x", query="q")
    assert "Search Results" in out
    assert "[A](http://a)" in out


def test_search_web_handles_no_results():
    with patch("src.tools.search_web.DDGS") as ddgs_cls:
        ddgs_cls.return_value.text.side_effect = [[], []]
        out = SearchWebTool().execute(status_message="x", query="q")
    assert "No results found" in out


# --- fetch_skill (dependency injection) ---

def test_fetch_skill_returns_matching_skill_content():
    services = MagicMock()
    services.ia_service.get_skills.return_value = [
        {"name": "deploy", "content": "steps to deploy"},
        {"name": "other", "content": "nope"},
    ]
    out = FetchSkillTool().execute(status_message="x", skill_name="deploy", services=services)
    assert out == "steps to deploy"


def test_fetch_skill_reports_missing_skill():
    services = MagicMock()
    services.ia_service.get_skills.return_value = []
    out = FetchSkillTool().execute(status_message="x", skill_name="deploy", services=services)
    assert "not found" in out
