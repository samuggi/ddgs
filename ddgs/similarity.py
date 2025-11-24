"""Simple filter ranker."""

import re
from typing import Final


class SimpleFilterRanker:
    """Simple filter ranker with priority support.

    1) Group results by engine priority (higher priority first)
    2) Within each priority group, bucket according to where query tokens appear:
       - both title & body/description
       - title only
       - body only
       - neither
    3) Return results sorted by priority, then by relevance within each priority.
    """

    _splitter: Final = re.compile(r"\W+")

    def __init__(self, min_token_length: int = 3) -> None:
        self.min_token_length = min_token_length

    def _extract_tokens(self, query: str) -> set[str]:
        """Split on non-word characters & filter out short tokens."""
        return {token for token in self._splitter.split(query.lower()) if len(token) >= self.min_token_length}

    def _has_any_token(self, text: str, tokens: set[str]) -> bool:
        """Check if any token is a substring of the lower-cased text."""
        lower_text = text.lower()
        return any(tok in lower_text for tok in tokens)

    def rank(self, docs: list[dict[str, str]], query: str) -> list[dict[str, str]]:
        """Rank a list of docs based on a query string and engine priority."""
        tokens = self._extract_tokens(query)

        # Group results by priority
        priority_groups: dict[float, dict[str, list[dict[str, str]]]] = {}

        for doc in docs:
            href = doc.get("href", "")
            title = doc.get("title", "")
            # fallback to 'description' if no 'body'
            body = doc.get("body", doc.get("description", ""))

            # Skip Wikimedia category pages
            if all(x in title for x in ["Category:", "Wikimedia"]):
                continue

            # Get engine priority (default to 1 if not set)
            priority = doc.get("engine_priority", 1)

            # Initialize priority group if needed
            if priority not in priority_groups:
                priority_groups[priority] = {
                    "both": [],
                    "title_only": [],
                    "body_only": [],
                    "neither": [],
                }

            # Title / Body match
            hit_title = self._has_any_token(title, tokens)
            hit_body = self._has_any_token(body, tokens)

            if hit_title and hit_body:
                priority_groups[priority]["both"].append(doc)
            elif hit_title:
                priority_groups[priority]["title_only"].append(doc)
            elif hit_body:
                priority_groups[priority]["body_only"].append(doc)
            else:
                priority_groups[priority]["neither"].append(doc)

        # Build final ranking: sort by priority (high to low), then by relevance
        final_results = []
        for priority in sorted(priority_groups.keys(), reverse=True):
            group = priority_groups[priority]
            final_results.extend(group["both"])
            final_results.extend(group["title_only"])
            final_results.extend(group["body_only"])
            final_results.extend(group["neither"])

        return final_results
