from types import SimpleNamespace
from unittest.mock import MagicMock

from src.models.run_context import RunContext
from src.tools.read_knowledge_base_file import ReadKnowledgeBaseFileTool
from src.tools.search_knowledge_base import SearchKnowledgeBaseTool


# --- read_knowledge_base_file ---

def test_read_kb_file_rejects_negative_skip():
    out = ReadKnowledgeBaseFileTool().execute(status_message="x", file="repo/doc", skip=-1)
    assert "cannot be negative" in out


def test_read_kb_file_returns_content_metadata():
    services = MagicMock()
    services.kb_files.read_file.return_value = "file body"
    out = ReadKnowledgeBaseFileTool().execute(
        status_message="x", file="repo/doc", services=services
    )
    assert "FILE CONTENT" in out
    assert "file body" in out


def test_read_kb_file_respects_kb_files_allowlist():
    services = MagicMock()
    ctx = RunContext(extra={"kb_files": ["allowed/"]})
    out = ReadKnowledgeBaseFileTool().execute(
        status_message="x", file="denied/doc", run_context=ctx, services=services
    )
    assert "not found" in out
    services.kb_files.read_file.assert_not_called()


def test_read_kb_file_handles_read_error():
    services = MagicMock()
    services.kb_files.read_file.side_effect = RuntimeError("boom")
    out = ReadKnowledgeBaseFileTool().execute(
        status_message="x", file="repo/doc", services=services
    )
    assert "not found" in out


# --- search_knowledge_base ---

def _wire_embeddings(services):
    """Make the embedding models return shapes the qdrant models accept."""
    services.qdrant.dense_model.query_embed.return_value = iter([[0.1, 0.2, 0.3]])
    sparse_embedding = SimpleNamespace(as_object=lambda: {"indices": [1], "values": [0.5]})
    services.qdrant.sparse_model.query_embed.return_value = iter([sparse_embedding])


def test_search_kb_returns_message_when_no_results():
    services = MagicMock()
    _wire_embeddings(services)
    services.qdrant.client.query_points.return_value = SimpleNamespace(points=[])
    out = SearchKnowledgeBaseTool().execute(
        status_message="x", queries=["q"], services=services
    )
    assert "No relevant information" in out


def test_search_kb_formats_grouped_results():
    services = MagicMock()
    _wire_embeddings(services)
    point = SimpleNamespace(
        id="1",
        score=0.9,
        payload={"file": "repo/doc", "page_content": "chunk", "title": "Doc"},
    )
    services.qdrant.client.query_points.return_value = SimpleNamespace(points=[point])
    out = SearchKnowledgeBaseTool().execute(
        status_message="x", queries=["q"], services=services
    )
    assert "repo/doc" in out
    assert "Doc" in out
