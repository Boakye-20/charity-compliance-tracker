"""Adapter for charity risk management guidance from Charity Commission and others.

This adapter focuses on curated risk management resources
specifically relevant to charities and voluntary organizations.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, NormalizedRecord, SourceMetadata


class RiskManagementAdapter(BaseAdapter):
    """Fetch and normalize curated risk management resources."""

    # Key risk management guidance for charities
    RESOURCES = [
        {
            "url": "https://www.gov.uk/government/publications/charities-and-risk-management-cc26",
            "title": "Charities and risk management (CC26)",
            "summary": "How charity trustees should approach risk management and the requirements to report on risk in the trustees' annual report.",
            "regulator": "CC",
            "last_updated": "2022-11-09"
        },
        {
            "url": "https://www.gov.uk/government/publications/how-to-manage-risks-in-your-charity",
            "title": "How to manage risks in your charity",
            "summary": "Practical guidance on identifying risks, establishing a risk management framework, and reporting on risk management.",
            "regulator": "CC", 
            "last_updated": "2023-03-14"
        },
        {
            "url": "https://www.gov.uk/guidance/how-to-manage-your-charitys-volunteers",
            "title": "How to manage your charity's volunteers",
            "summary": "Guidance for charity trustees on recruiting, supporting and managing volunteers, including managing associated risks.",
            "regulator": "CC",
            "last_updated": "2022-09-08"
        },
        {
            "url": "https://www.gov.uk/guidance/apply-risk-management",
            "title": "Apply risk management principles to your charity",
            "summary": "Practical steps for charity trustees to identify and mitigate risks to their organization, people, and assets.",
            "regulator": "CC",
            "last_updated": "2023-05-21"
        },
        {
            "url": "https://www.gov.uk/government/publications/charities-due-diligence-checks-and-monitoring-end-use-of-funds",
            "title": "Charities: due diligence and monitoring end use of funds",
            "summary": "How charities should undertake due diligence on those individuals and organizations that receive charity funds or work closely with the charity.",
            "regulator": "CC",
            "last_updated": "2022-07-11" 
        }
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity risk management guidance",
            url="https://www.gov.uk/government/publications/charities-and-risk-management-cc26",
            regulator="CC",
            update_frequency="quarterly",
        )

    def download_raw(self) -> Path:
        import json

        output_path = self.staging_dir / "risk_management_raw.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.RESOURCES, f, indent=2, ensure_ascii=False)

        return output_path

    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        import json

        with open(raw_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        records: list[NormalizedRecord] = []
        for item in items:
            title: str = item.get("title", "")
            summary: str = item.get("summary", "")

            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
            record_id = f"RISK_{slug}"

            keywords = self._build_keywords(title, summary)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=item.get("last_updated", "2023-01-01"),
                last_updated=item.get("last_updated", "2023-01-01"),
                regulator=item.get("regulator", "CC"),
                domain="risk_management",
                document_type="guidance",
                keywords=keywords,
            )
            records.append(record)

        self.logger.info("Normalized %d risk management guidance records", len(records))
        return records

    def _build_keywords(self, title: str, summary: str) -> list[str]:
        base = f"{title} {summary}".lower()
        tokens = re.findall(r"[a-z]{4,}", base)
        unique: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            if token not in seen:
                unique.append(token)
                seen.add(token)
            if len(unique) >= 20:
                break
        return unique
