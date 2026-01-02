"""Adapter for ICO and gov.uk data protection guidance for charities.

This adapter focuses on curated data protection and privacy resources
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


class DataProtectionAdapter(BaseAdapter):
    """Fetch and normalize curated data protection resources."""

    # Key data protection guidance for charities
    RESOURCES = [
        {
            "url": "https://ico.org.uk/for-organisations/charity/",
            "title": "Data protection for charities and small voluntary organisations",
            "summary": "ICO guidance on how charities should comply with data protection law including GDPR, marketing rules, and handling personal data.",
            "regulator": "ICO",
            "last_updated": "2023-09-22"
        },
        {
            "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/guidance-for-charity-and-voluntary-organisations/",
            "title": "GDPR compliance for charities and voluntary organisations",
            "summary": "Information Commissioner's Office guidance on handling personal data, fundraising, and marketing in compliance with UK GDPR.",
            "regulator": "ICO", 
            "last_updated": "2023-06-10"
        },
        {
            "url": "https://ico.org.uk/for-organisations/charity/charities-faqs/",
            "title": "Charity FAQs on data protection",
            "summary": "Answers to common questions about how data protection applies to charitable activities.",
            "regulator": "ICO",
            "last_updated": "2022-11-18"
        },
        {
            "url": "https://www.gov.uk/government/publications/data-protection-and-privacy-guidance-for-the-charity-sector",
            "title": "Data protection and privacy guidance for the charity sector",
            "summary": "Guidance on collecting, storing and using personal data in accordance with data protection legislation, including when sharing information with other organisations.",
            "regulator": "ICO",
            "last_updated": "2023-02-14"
        },
        {
            "url": "https://ico.org.uk/for-organisations/charity/data-protection-self-assessment-for-charities/",
            "title": "Data protection self-assessment for charities",
            "summary": "Self-assessment toolkit to help charities evaluate their compliance with data protection law and identify areas for improvement.",
            "regulator": "ICO",
            "last_updated": "2022-08-20" 
        }
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity data protection guidance",
            url="https://ico.org.uk/for-organisations/charity/",
            regulator="ICO",
            update_frequency="quarterly",
        )

    def download_raw(self) -> Path:
        import json

        output_path = self.staging_dir / "data_protection_raw.json"
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
            record_id = f"GDPR_{slug}"

            keywords = self._build_keywords(title, summary)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=item.get("last_updated", "2023-01-01"),
                last_updated=item.get("last_updated", "2023-01-01"),
                regulator=item.get("regulator", "ICO"),
                domain="gdpr",
                document_type="guidance",
                keywords=keywords,
            )
            records.append(record)

        self.logger.info("Normalized %d data protection guidance records", len(records))
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
