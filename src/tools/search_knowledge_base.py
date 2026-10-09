import logging
from collections import defaultdict

from mcp.types import Tool

from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool

logger = logging.getLogger(__name__)


class SearchKnowledgeBaseTool(BaseTool):
    requires_services = True

    MAX_RESULTS = 20
    OVERSAMPLE_FACTOR = 8

    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="search_knowledge_base",
            description=(
                "Searches Pier Cloud's knowledge base. The knowledge base is in English, so "
                "queries must be in English."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status_message": {
                        "type": "string",
                        "description": "One sentence explanation as to why this tool is being used.",
                    },
                    "queries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Up to 3 English queries. Prefer affirmative statements.",
                        "maxItems": 3,
                    },
                },
                "required": ["status_message", "queries"],
            },
        )

    def execute(
        self,
        status_message: str,
        queries: list,
        run_context: RunContext = None,
        services=None,
    ) -> str:
        from qdrant_client import models

        vector_db = services.qdrant
        kb_files = run_context.extra.get("kb_files") if run_context else None
        filter_obj = self._build_filter(models, kb_files)

        collected = []
        for query in queries[:3]:
            dense = next(vector_db.dense_model.query_embed(query))
            sparse = models.SparseVector(
                **next(vector_db.sparse_model.query_embed(query)).as_object()
            )
            points = vector_db.client.query_points(
                vector_db.collection_name,
                prefetch=self._prefetch(models, dense, sparse),
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=self.MAX_RESULTS,
                query_filter=filter_obj,
            ).points
            if points:
                collected.append(points)

        if not collected:
            return "No relevant information found in the knowledge base."

        deduped = list(
            {p.id: p for points in collected for p in points}.values()
        )
        return self._format_results(deduped)

    def _prefetch(self, models, dense, sparse):
        limit = self.MAX_RESULTS * self.OVERSAMPLE_FACTOR
        return [
            models.Prefetch(query=dense, using="all-MiniLM-L6-v2", limit=limit, score_threshold=0.25),
            models.Prefetch(query=sparse, using="bm25", limit=limit),
        ]

    def _build_filter(self, models, kb_files):
        if not kb_files:
            return None
        return models.Filter(
            should=[
                models.FieldCondition(key="file", match=models.MatchPhrase(phrase=folder))
                for folder in kb_files
            ]
        )

    def _format_results(self, results) -> str:
        grouped = defaultdict(lambda: {"chunks": [], "title": None})
        for r in results:
            fname = r.payload.get("file")
            grouped[fname]["chunks"].append(
                {"score": round(r.score, 3), "content": r.payload.get("page_content")}
            )
            if not grouped[fname]["title"]:
                grouped[fname]["title"] = r.payload.get("title", fname.split("/")[-1])

        formatted = []
        for fname, data in grouped.items():
            top = sorted(data["chunks"], key=lambda c: c["score"], reverse=True)[:3]
            formatted.append(
                {
                    "file": fname,
                    "title": data["title"],
                    "num_chunks": len(data["chunks"]),
                    "top_chunks": top,
                }
            )
        formatted = sorted(
            formatted, key=lambda x: x["top_chunks"][0]["score"], reverse=True
        )[: self.MAX_RESULTS]
        return str(formatted)
