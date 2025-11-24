"""Naver search engine implementation."""

from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import quote_plus

from ddgs.base import BaseSearchEngine
from ddgs.results import TextResult


class Naver(BaseSearchEngine[TextResult]):
    """Naver search engine."""

    disabled = False  # Explicitly enable this engine
    name = "naver"
    category = "text"
    provider = "naver"
    priority = 3  # Highest priority (higher than Wikipedia's 2)

    search_url = "https://search.naver.com/search.naver"
    search_method = "GET"

    # XPath selectors for Naver search results
    # Note: Naver's HTML structure may vary, these are common patterns
    items_xpath = "//div[contains(@class, 'total_wrap')] | //li[contains(@class, 'bx')] | //div[contains(@class, 'api_subject_bx')]"
    elements_xpath: ClassVar[Mapping[str, str]] = {
        "title": ".//a[contains(@class, 'link_tit') or contains(@class, 'total_tit') or contains(@class, 'api_txt_lines')]//text() | .//strong[@class='ell']//text()",
        "href": ".//a[contains(@class, 'link_tit') or contains(@class, 'total_tit') or @class='link']/@href",
        "body": ".//div[contains(@class, 'total_txt') or contains(@class, 'api_txt_lines')] //text() | .//p[contains(@class, 'api_txt_lines')]//text() | .//dd[contains(@class, 'txt')]//text()",
    }

    def build_payload(
        self,
        query: str,
        region: str,
        safesearch: str,  # noqa: ARG002
        timelimit: str | None,
        page: int = 1,
        **kwargs: str,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Build a payload for the Naver search request."""
        # Naver uses 1-based indexing for start parameter
        # Each page shows 10 results, so start = (page - 1) * 10 + 1
        start = (page - 1) * 10 + 1

        payload = {
            "query": query,
            "where": "nexearch",  # Integrated search (통합검색)
            "start": str(start),
        }

        # Handle region (Naver is primarily Korean, but we can set display settings)
        if region and "-" in region:
            country, lang = region.lower().split("-")
            # Naver mainly supports Korean
            if lang == "ko" or country == "kr":
                payload["sm"] = "top_hty"  # Korean search mode

        # Timelimit mapping (Naver uses 'nso' parameter)
        # Format: nso=so:r,p:[period]
        if timelimit:
            period_map = {
                "d": "1d",  # Last day
                "w": "1w",  # Last week
                "m": "1m",  # Last month
                "y": "1y",  # Last year
            }
            if timelimit in period_map:
                payload["nso"] = f"so:r,p:{period_map[timelimit]}"

        return payload

    def post_extract_results(self, results: list[TextResult]) -> list[TextResult]:
        """Post-process search results."""
        post_results = []
        for result in results:
            # Filter out empty results
            if not result.href or not result.title:
                continue

            # Skip Naver's internal ads and related searches
            if "searchad.naver.com" in result.href:
                continue
            if result.href.startswith("https://search.naver.com/search.naver"):
                continue

            # Clean up the body text
            if result.body:
                result.body = " ".join(result.body.split())

            post_results.append(result)

        return post_results
