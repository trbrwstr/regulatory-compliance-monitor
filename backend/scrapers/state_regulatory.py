import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Optional


class StateRegulatoryScraper:
    """Scrapes state regulatory websites for compliance updates."""

    # Example state regulatory sources
    STATE_SOURCES = {
        "california": {
            "name": "California Office of Administrative Law",
            "url": "https://oal.ca.gov/publications/ccr_changes/",
            "type": "html",
        },
        "new_york": {
            "name": "NY State Register",
            "url": "https://dos.ny.gov/state-register",
            "type": "html",
        },
        "texas": {
            "name": "Texas Secretary of State - Texas Register",
            "url": "https://www.sos.state.tx.us/texreg/index.shtml",
            "type": "html",
        },
    }

    def __init__(self, sources: Optional[dict] = None):
        self.sources = sources or self.STATE_SOURCES

    async def scrape_state(self, state: str) -> list[dict]:
        """Scrape regulatory updates from a specific state."""
        source = self.sources.get(state)
        if not source:
            return []

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(source["url"])
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            return self._extract_updates(soup, source)
        except Exception as e:
            print(f"Error scraping {state}: {e}")
            return []

    def _extract_updates(self, soup: BeautifulSoup, source: dict) -> list[dict]:
        """Extract regulatory updates from parsed HTML.

        Uses generic heuristics to find regulation-related content.
        """
        updates = []

        # Look for common patterns in regulatory sites
        # Try tables first (many regulatory sites use tables)
        tables = soup.find_all("table")
        for table in tables[:2]:  # Limit to first 2 tables
            rows = table.find_all("tr")[1:]  # Skip header
            for row in rows[:20]:  # Limit rows
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    title = cells[0].get_text(strip=True)
                    link = cells[0].find("a")
                    url = link["href"] if link and link.get("href") else source["url"]

                    if title and len(title) > 10:
                        updates.append({
                            "title": title[:500],
                            "abstract": cells[1].get_text(strip=True)[:1000] if len(cells) > 1 else "",
                            "source_url": url if url.startswith("http") else f"{source['url'].rstrip('/')}/{url.lstrip('/')}",
                            "publication_date": datetime.now(timezone.utc).isoformat(),
                            "source_type": "state_site",
                            "state": source["name"],
                        })

        # If no tables, try article/list patterns
        if not updates:
            articles = soup.find_all(["article", "li", "div"], class_=lambda x: x and any(
                kw in str(x).lower() for kw in ["rule", "regulation", "notice", "update"]
            ))
            for article in articles[:20]:
                title_el = article.find(["h2", "h3", "h4", "a", "strong"])
                if title_el:
                    title = title_el.get_text(strip=True)
                    link = title_el.find("a") or (title_el if title_el.name == "a" else None)
                    url = link["href"] if link and link.get("href") else source["url"]

                    if title and len(title) > 10:
                        updates.append({
                            "title": title[:500],
                            "abstract": article.get_text(strip=True)[:1000],
                            "source_url": url if url.startswith("http") else f"{source['url'].rstrip('/')}/{url.lstrip('/')}",
                            "publication_date": datetime.now(timezone.utc).isoformat(),
                            "source_type": "state_site",
                            "state": source["name"],
                        })

        return updates

    async def scrape_all_states(self) -> dict[str, list[dict]]:
        """Scrape all configured state sources."""
        results = {}
        for state in self.sources:
            results[state] = await self.scrape_state(state)
        return results
