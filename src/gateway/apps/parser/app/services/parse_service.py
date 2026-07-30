__anchor__ = "parser"
# schema-ref: project-schema.yaml#/services/4

import re
import uuid
from typing import Any

from bs4 import BeautifulSoup, Tag


class ParseService:
    """Extracts text and structure from crawled regulatory documents."""

    async def parse_html(
        self, url: str, html_content: str, document_title: str | None = None
    ) -> dict[str, Any]:
        soup = BeautifulSoup(html_content, "html.parser")
        title = document_title or (soup.title.string if soup.title else url)
        doc_id = str(uuid.uuid4())

        fragments: list[dict[str, Any]] = []
        fragment_no = 0

        # Extract text from meaningful block elements
        for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th"]):
            text = tag.get_text(strip=True)
            if not text or len(text) < 20:
                continue

            fragment_no += 1
            section_path = self._detect_section(tag)
            paragraph_label = self._detect_paragraph_label(tag)

            fragments.append({
                "fragment_id": str(uuid.uuid4()),
                "fragment_no": fragment_no,
                "section_path": section_path,
                "paragraph_label": paragraph_label,
                "fragment_text": text,
                "citation_label": self._build_citation_label(fragment_no, paragraph_label),
                "token_count": len(text.split()),
            })

        return {
            "document_id": doc_id,
            "document_title": title,
            "fragments": fragments,
            "fragment_count": len(fragments),
        }

    def _detect_section(self, tag: Tag) -> str | None:
        """Walk up the DOM to build a section path."""
        parts: list[str] = []
        for parent in tag.parents:
            if isinstance(parent, Tag) and parent.name in ("section", "article", "div"):
                _id = parent.get("id")
                _class = parent.get("class")
                if _id:
                    parts.insert(0, f"#{_id}")
                elif _class:
                    parts.insert(0, ".".join(_class[:1]))
                if len(parts) > 3:
                    break
        return " / ".join(parts) if parts else None

    def _detect_paragraph_label(self, tag: Tag) -> str | None:
        """Extract paragraph number from id or text prefix."""
        text = tag.get_text(strip=True)
        _id = tag.get("id", "")
        if _id:
            return str(_id)
        # Match patterns like "1.", "1.1", "п. 3", "абз. 2"
        m = re.match(r"^(п\.\s*\d+|абз\.\s*\d+|\d+\.\d+|\d+\.)\s", text)
        if m:
            return m.group(1)
        return None

    def _build_citation_label(self, fragment_no: int, paragraph_label: str | None) -> str:
        if paragraph_label:
            return f"п. {paragraph_label}"
        return f"фр. {fragment_no}"
