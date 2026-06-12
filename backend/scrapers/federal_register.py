import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import get_settings


class FederalRegisterScraper:
    """Scrapes the Federal Register API for new regulatory documents."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.federal_register_base_url

    async def fetch_recent_documents(
        self,
        days_back: int = 1,
        per_page: int = 50,
        agencies: Optional[list[str]] = None,
    ) -> list[dict]:
        """Fetch recent documents from the Federal Register API."""
        start_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

        params = {
            "conditions[publication_date][gte]": start_date,
            "per_page": per_page,
            "order": "newest",
            "fields[]": [
                "title",
                "document_number",
                "abstract",
                "publication_date",
                "effective_on",
                "html_url",
                "agencies",
                "type",
                "subtype",
            ],
        }

        if agencies:
            params["conditions[agencies][]"] = agencies

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/documents.json", params=params)
            response.raise_for_status()
            data = response.json()

        return self._parse_documents(data.get("results", []))

    async def fetch_by_topic(self, topic: str, per_page: int = 20) -> list[dict]:
        """Search Federal Register by topic/keyword."""
        params = {
            "conditions[term]": topic,
            "per_page": per_page,
            "order": "newest",
            "fields[]": [
                "title",
                "document_number",
                "abstract",
                "publication_date",
                "effective_on",
                "html_url",
                "agencies",
                "type",
            ],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/documents.json", params=params)
            response.raise_for_status()
            data = response.json()

        return self._parse_documents(data.get("results", []))

    def _parse_documents(self, results: list[dict]) -> list[dict]:
        """Parse raw API results into normalized document dicts."""
        documents = []
        for doc in results:
            agencies = [a.get("name", "") for a in doc.get("agencies", [])]
            documents.append({
                "title": doc.get("title", ""),
                "document_number": doc.get("document_number", ""),
                "abstract": doc.get("abstract", ""),
                "publication_date": doc.get("publication_date"),
                "effective_date": doc.get("effective_on"),
                "source_url": doc.get("html_url", ""),
                "agencies": agencies,
                "doc_type": doc.get("type", ""),
                "source_type": "federal_register",
            })
        return documents

    async def fetch_document_detail(self, document_number: str) -> Optional[dict]:
        """Fetch full details for a specific document."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/documents/{document_number}.json")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
