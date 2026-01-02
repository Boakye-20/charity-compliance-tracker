"""Adapter for NSPCC, NCVO and gov.uk safeguarding guidance for charities.

This adapter focuses on curated safeguarding resources specifically
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


class SafeguardingAdapter(BaseAdapter):
    """Fetch and normalize curated safeguarding resources."""

    # Key safeguarding guidance for charities
    RESOURCES = [
        {
            "url": "https://www.gov.uk/government/publications/strategy-for-dealing-with-safeguarding-issues-in-charities",
            "title": "Strategy for dealing with safeguarding issues in charities",
            "summary": "How the Charity Commission approaches safeguarding concerns and works with other agencies to address them.",
            "regulator": "CC",
            "last_updated": "2018-12-06"
        },
        {
            "url": "https://www.gov.uk/guidance/safeguarding-duties-for-charity-trustees",
            "title": "Safeguarding duties for charity trustees",
            "summary": "How trustees should protect people who come into contact with their charity through its work from abuse or mistreatment of any kind.",
            "regulator": "CC", 
            "last_updated": "2022-10-14"
        },
        {
            "url": "https://www.gov.uk/government/publications/safeguarding-children-and-protecting-professionals-in-early-years-settings-online-safety-considerations",
            "title": "Safeguarding children in charities and voluntary organizations",
            "summary": "Guidance for people working in charities and voluntary organisations with children, including avoiding risks and handling incidents.",
            "regulator": "CC",
            "last_updated": "2019-02-04"
        },
        {
            "url": "https://www.ncvo.org.uk/help-and-guidance/safeguarding/",
            "title": "Safeguarding essentials for voluntary organizations",
            "summary": "NCVO guidance on safeguarding for charities with step-by-step advice and free templates.",
            "regulator": "CC",
            "last_updated": "2023-07-01"
        },
        {
            "url": "https://learning.nspcc.org.uk/safeguarding-child-protection/for-voluntary-community-groups",
            "title": "NSPCC Safeguarding for voluntary and community organizations",
            "summary": "Resources to help voluntary, community and faith organizations keep children safe, including guidance on writing policies and procedures.",
            "regulator": "CC",
            "last_updated": "2023-10-15" 
        }
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity safeguarding guidance",
            url="https://www.gov.uk/guidance/safeguarding-duties-for-charity-trustees",
            regulator="CC",
            update_frequency="quarterly",
        )

    def download_raw(self) -> Path:
        import json

        output_path = self.staging_dir / "safeguarding_guidance_raw.json"
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
            record_id = f"SAFEGUARDING_{slug}"

            keywords = self._build_keywords(title, summary)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=item.get("last_updated", "2023-01-01"),
                last_updated=item.get("last_updated", "2023-01-01"),
                regulator="CC",  # Most safeguarding resources are from CC
                domain="safeguarding",
                document_type="guidance",
                keywords=keywords,
            )
            records.append(record)

        self.logger.info("Normalized %d safeguarding guidance records", len(records))
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
