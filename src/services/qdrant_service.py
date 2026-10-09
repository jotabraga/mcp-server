"""Vector DB service for knowledge-base search.

Heavy imports (qdrant_client, fastembed) happen inside the constructor, not at module import,
so importing this module stays cheap. The service is only built by the lazy provider inside
the HTTP lifespan, never at import time.
"""
import logging

from src.const import Model

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self, host, port, api_key, collection_name):
        from qdrant_client import QdrantClient
        from fastembed import SparseTextEmbedding, TextEmbedding

        self.collection_name = collection_name
        self.client = QdrantClient(
            url=host, port=port, api_key=api_key, timeout=30.0, check_compatibility=False
        )
        self.dense_model = TextEmbedding(f"sentence-transformers/{Model.ALL_MINILM_L6_V2}")
        self.sparse_model = SparseTextEmbedding(f"Qdrant/{Model.BM25}")

        if not self.client.collection_exists(self.collection_name):
            raise RuntimeError(f"Collection '{self.collection_name}' does not exist")
        logger.info("QdrantService ready for collection '%s'", self.collection_name)
