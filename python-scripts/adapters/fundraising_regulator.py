"""Adapter for Fundraising Regulator guidance.

This currently treats the Code of Fundraising Practice as a single,
key guidance document, using a static record based on the published PDF
link in DATA_SOURCES.md.

The Fundraising Regulator website does not expose a simple HTML index
of all adjudications in a consistent structure, so this adapter focuses
on getting at least the core Code into the unified schema.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
import re

from .base import BaseAdapter, NormalizedRecord, SourceMetadata


class FundraisingRegulatorAdapter(BaseAdapter):
    """Provide a minimal normalized record for the Code of Practice."""

    CODE_PDF_URL = (
        "https://www.fundraisingregulator.org.uk/sites/default/files/2019-09/"
        "Code-of-Fundraising-Practice-October-2019.pdf"
    )

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Fundraising Regulator – Code of Fundraising Practice",
            url="https://www.fundraisingregulator.org.uk/",
            regulator="FR",
            update_frequency="annual",
        )

    def download_raw(self) -> Path:
        import json

        # For now we don't attempt to parse the PDF contents; we just
        # register the document in a small JSON structure.
        record = {
            "url": self.CODE_PDF_URL,
            "title": "Code of Fundraising Practice",
            "summary": "Official Code of Fundraising Practice issued by the Fundraising Regulator.",
            "last_updated": "2019-10-01",
            "full_text": "",
        }

        output_path = self.staging_dir / "fr_guidance_raw.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([record], f, indent=2, ensure_ascii=False)

        return output_path

    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        import json

        with open(raw_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        records: list[NormalizedRecord] = []
        for item in items:
            title: str = item.get("title", "Code of Fundraising Practice")
            summary: str = item.get("summary", "")
            full_text: str = item.get("full_text", "")

            last_updated = item.get("last_updated") or datetime.now().strftime("%Y-%m-%d")

            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
            record_id = f"FR_guidance_{slug}" if slug else f"FR_guidance_{int(datetime.now().timestamp())}"

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=last_updated,
                last_updated=last_updated,
                regulator="FR",
                domain="risk_management",
                document_type="guidance",
                keywords=["fundraising", "code", "practice", "governance"],
                full_text=full_text,
            )
            records.append(record)

        self.logger.info("Normalized %d Fundraising Regulator records", len(records))
        return records
