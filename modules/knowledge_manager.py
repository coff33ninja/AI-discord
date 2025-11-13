"""
Knowledge Manager - thin wrapper around the async AI database for reusable knowledge

Provides a small, stable interface used by other modules to add/search/get knowledge
without depending directly on the lower-level DB implementation.
"""
import logging
from typing import List, Optional, Dict

import json


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
        """Add knowledge to the DB.

        Behavior: merge/append new facts into any existing record for (category, key_term).
        - If existing content is JSON array or object, attempt to merge entries (dedupe by 'text').
        - If existing content is plain text, convert to a single-item list and merge.
        - The final stored `content` is a JSON array string.
        """
        if not self.ai_db:
            logger.debug("No AI DB configured; skipping add_knowledge")
            return None
        try:
            # Normalize incoming content into a list of fact objects
            new_items = []
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    new_items = parsed
                elif isinstance(parsed, dict):
                    new_items = [parsed]
                else:
                    # Primitive types -> wrap as text
                    new_items = [{'text': str(parsed)}]
            except Exception:
                # Not JSON -> treat as plain text
                new_items = [{'text': str(content)}]

            # Try to find existing record for exact (category, key_term)
            existing_rows = []
            try:
                existing_rows = await self.ai_db.search_knowledge(key_term, category, limit=5)
            except Exception:
                existing_rows = []

            existing_content = None
            for r in existing_rows:
                if r.get('key_term') == key_term:
                    existing_content = r.get('content')
                    break

            merged = []
            seen_texts = set()

            # Load existing items if present
            if existing_content:
                try:
                    parsed_existing = json.loads(existing_content)
                    if isinstance(parsed_existing, list):
                        for it in parsed_existing:
                            text = (it.get('text') if isinstance(it, dict) else str(it))
                            key = text.strip().lower()
                            if key not in seen_texts:
                                seen_texts.add(key)
                                merged.append(it)
                    elif isinstance(parsed_existing, dict):
                        text = parsed_existing.get('text') if isinstance(parsed_existing, dict) else str(parsed_existing)
                        key = text.strip().lower()
                        seen_texts.add(key)
                        merged.append(parsed_existing)
                    else:
                        txt = str(parsed_existing)
                        seen_texts.add(txt.strip().lower())
                        merged.append({'text': txt})
                except Exception:
                    # Treat raw existing content as single text item
                    txt = str(existing_content)
                    seen_texts.add(txt.strip().lower())
                    merged.append({'text': txt})

            # Merge in new items, dedupe by lowercase text
            for it in new_items:
                if isinstance(it, dict):
                    text = it.get('text') or it.get('content') or str(it)
                else:
                    text = str(it)
                key = text.strip().lower()
                if key in seen_texts:
                    continue
                seen_texts.add(key)
                # Prefer to store dicts when supplied
                if isinstance(it, dict):
                    merged.append(it)
                else:
                    merged.append({'text': text})

            # Final content as JSON array
            final_content = json.dumps(merged, ensure_ascii=False)

            return await self.ai_db.add_knowledge(category, key_term, final_content, relevance_score)

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
