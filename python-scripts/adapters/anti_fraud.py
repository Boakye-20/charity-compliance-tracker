"""Adapter for charity anti-fraud guidance from Charity Commission and others.

This adapter focuses on curated anti-fraud resources specifically
relevant to charities and voluntary organizations.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, NormalizedRecord, SourceMetadata


class AntiFraudAdapter(BaseAdapter):
    """Fetch and normalize curated anti-fraud resources."""

    # Key anti-fraud guidance for charities
    RESOURCES = [
        {
            "url": "https://www.gov.uk/guidance/protect-your-charity-from-fraud",
            "title": "Protect your charity from fraud",
            "summary": "Practical steps for charity trustees to protect your charity from different types of fraud, including financial crime and cybercrime.",
            "regulator": "CC",
            "last_updated": "2023-07-18"
        },
        {
            "url": "https://www.gov.uk/government/publications/fraud-and-cybercrime-prevention-for-charities/tackling-charity-fraud-prevention-is-better-than-cure",
            "title": "Tackling charity fraud: prevention is better than cure",
            "summary": "Guidance from the Charity Commission on fraud awareness, prevention, and the steps trustees should take to protect their charity.",
            "regulator": "CC", 
            "last_updated": "2022-09-26"
        },
        {
            "url": "https://www.gov.uk/government/publications/compliance-toolkit-protecting-charities-from-harm/chapter-3-fraud-and-financial-crime",
            "title": "Compliance toolkit: protecting charities from financial crime",
            "summary": "How trustees can protect their charities from financial crime such as fraud, theft, and money laundering.",
            "regulator": "CC",
            "last_updated": "2023-01-05"
        },
        {
            "url": "https://www.gov.uk/government/publications/charities-fraud-and-financial-crime",
            "title": "Charity fraud: how to spot it and reduce the risks",
            "summary": "Charity Commission guide to common types of charity fraud and the practical steps trustees can take to prevent it.",
            "regulator": "CC",
            "last_updated": "2022-11-13"
        },
        {
            "url": "https://www.gov.uk/government/publications/compliance-toolkit-chapter-2-due-diligence-monitoring-and-verification-of-end-use-of-charitable-funds",
            "title": "Preventing terrorist financing: due diligence for charities",
            "summary": "How charities operating in high-risk areas can protect themselves from terrorist financing and money laundering risks.",
            "regulator": "CC",
            "last_updated": "2022-05-19" 
        }
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity anti-fraud guidance",
            url="https://www.gov.uk/guidance/protect-your-charity-from-fraud",
            regulator="CC",
            update_frequency="quarterly",
        )

    def download_raw(self) -> Path:
        import json

        output_path = self.staging_dir / "anti_fraud_raw.json"
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
            record_id = f"FRAUD_{slug}"

            keywords = self._build_keywords(title, summary)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=item.get("last_updated", "2023-01-01"),
                last_updated=item.get("last_updated", "2023-01-01"),
                regulator=item.get("regulator", "CC"),
                domain="anti_fraud",
                document_type="guidance",
                keywords=keywords,
            )
            records.append(record)

        self.logger.info("Normalized %d anti-fraud guidance records", len(records))
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
