"""Adapter for charity financial reporting guidance from HMRC, Charity Commission and others.

This adapter focuses on curated financial reporting, accounting and tax resources
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


class FinancialReportingAdapter(BaseAdapter):
    """Fetch and normalize curated financial reporting resources."""

    # Key financial guidance for charities
    RESOURCES = [
        {
            "url": "https://www.gov.uk/government/publications/charity-reporting-and-accounting-the-essentials-november-2016-cc15d",
            "title": "Charity reporting and accounting: the essentials",
            "summary": "A guide to the accounting framework that applies to charities in England and Wales and how to prepare charity accounts and reports.",
            "regulator": "CC",
            "last_updated": "2023-03-16"
        },
        {
            "url": "https://www.gov.uk/government/publications/charities-sorp-2023",
            "title": "Charities SORP (FRS 102)",
            "summary": "Statement of Recommended Practice for charity accounting - Accounting and Reporting by Charities.",
            "regulator": "CC", 
            "last_updated": "2023-04-01"
        },
        {
            "url": "https://www.gov.uk/government/publications/charity-finances-trustee-essentials-cc25",
            "title": "Charity finances: trustee essentials",
            "summary": "How charity trustees should manage their charity's finances, including internal financial controls, reserves and investments.",
            "regulator": "CC",
            "last_updated": "2022-05-02"
        },
        {
            "url": "https://www.gov.uk/government/publications/charities-detailed-guidance-notes/annex-iv-trading-and-business-activities-basic-principles",
            "title": "Charity tax: trading and business activities",
            "summary": "HMRC detailed guidance on charity trading, tax exemptions, and what constitutes primary purpose trading versus non-primary purpose trading.",
            "regulator": "HMRC",
            "last_updated": "2023-06-10"
        },
        {
            "url": "https://www.gov.uk/government/publications/charities-detailed-guidance-notes/chapter-3-gift-aid",
            "title": "Gift Aid: detailed guidance for charities",
            "summary": "How charities can claim tax back on eligible donations through the Gift Aid scheme.",
            "regulator": "HMRC",
            "last_updated": "2023-04-15" 
        },
        {
            "url": "https://www.gov.uk/government/publications/internal-financial-controls-for-charities-cc8",
            "title": "Internal financial controls for charities",
            "summary": "How charity trustees should establish robust internal financial controls to protect charity assets and prevent fraud.",
            "regulator": "CC",
            "last_updated": "2022-07-22" 
        }
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity financial reporting guidance",
            url="https://www.gov.uk/government/publications/charity-reporting-and-accounting-the-essentials-november-2016-cc15d",
            regulator="CC",
            update_frequency="quarterly",
        )

    def download_raw(self) -> Path:
        import json

        output_path = self.staging_dir / "financial_reporting_raw.json"
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
            record_id = f"FINANCE_{slug}"

            keywords = self._build_keywords(title, summary)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=item.get("last_updated", "2023-01-01"),
                last_updated=item.get("last_updated", "2023-01-01"),
                regulator=item.get("regulator", "CC"),
                domain="financial_reporting",
                document_type="guidance",
                keywords=keywords,
            )
            records.append(record)

        self.logger.info("Normalized %d financial reporting guidance records", len(records))
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
