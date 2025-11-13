"""
Knowledge Manager - thin wrapper around the async AI database for reusable knowledge

Provides a small, stable interface used by other modules to add/search/get knowledge
without depending directly on the lower-level DB implementation.
"""
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class KnowledgeManager:
    def __init__(self, ai_db=None):
        """Wrap an AIDatabase-like instance providing async methods.

        The wrapped object must implement: `add_knowledge`, `search_knowledge`, `get_random_knowledge`.
        """
        self.ai_db = ai_db

    def set_ai_db(self, ai_db):
        """Inject the underlying DB instance (AIDatabase)."""
        self.ai_db = ai_db

    async def add_knowledge(self, category: str, key_term: str, content: str, relevance_score: float = 1.0):
        """Add or replace a knowledge entry. Returns None or raises on error."""
        if not self.ai_db:
            logger.debug("No AI DB configured; skipping add_knowledge")
            return None
        try:
            return await self.ai_db.add_knowledge(category, key_term, content, relevance_score)
        except Exception as e:
            logger.exception(f"Failed to add knowledge: {e}")
            return None

    async def search_knowledge(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search the knowledge base; returns list of rows or empty list."""
        if not self.ai_db:
            logger.debug("No AI DB configured; search_knowledge returning empty list")
            return []
        try:
            return await self.ai_db.search_knowledge(query, category, limit)
        except Exception as e:
            logger.exception(f"Knowledge search failed: {e}")
            return []

    async def get_random_knowledge(self, category: str = None) -> Optional[Dict]:
        """Return a single random knowledge row or None."""
        if not self.ai_db:
            logger.debug("No AI DB configured; get_random_knowledge returning None")
            return None
        try:
            return await self.ai_db.get_random_knowledge(category)
        except Exception as e:
            logger.exception(f"get_random_knowledge failed: {e}")
            return None


# Module-level default manager for easy import
knowledge_manager = KnowledgeManager()
