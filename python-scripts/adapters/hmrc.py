"""Adapter for HMRC charities guidance (financial reporting and tax).

This focuses on curated, high‑value guidance pages rather than crawling
all of GOV.UK.

Primary source (from DATA_SOURCES.md):
    https://www.gov.uk/government/publications/charities-detailed-guidance-notes
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, NormalizedRecord, SourceMetadata


class HMRCAdapter(BaseAdapter):
    """Fetch and normalize a curated set of HMRC guidance pages."""

    HMRC_PAGES = [
        # Core detailed guidance notes for charities
        "https://www.gov.uk/government/publications/charities-detailed-guidance-notes",
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="HMRC charities detailed guidance notes",
            url="https://www.gov.uk/government/collections/charities-detailed-guidance-notes",
            regulator="HMRC",
            update_frequency="annual",
        )

    def download_raw(self) -> Path:
        import json

        records: list[dict] = []

        for i, url in enumerate(self.HMRC_PAGES):
            self.logger.info("[%d/%d] Fetching HMRC guidance page: %s", i + 1, len(self.HMRC_PAGES), url)
            try:
                data = self._fetch_page(url)
                if data:
                    records.append(data)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("Failed to fetch %s: %s", url, exc)

        output_path = self.staging_dir / "hmrc_guidance_raw.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        return output_path

    def _fetch_page(self, url: str) -> Optional[dict]:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html5lib")

        title_el = soup.select_one("h1")
        title = title_el.get_text(strip=True) if title_el else "HMRC charities guidance"

        # Try meta description first
        desc_meta = soup.select_one('meta[name="description"]')
        if desc_meta and desc_meta.get("content"):
            summary = desc_meta["content"].strip()
        else:
            p = soup.select_one("main p, #content p, .content p")
            summary = p.get_text(strip=True) if p else "HMRC detailed guidance notes for charities."

        last_updated = self._extract_last_updated(soup)

        main_el = soup.select_one("main, #content, .content")
        full_text = main_el.get_text(" ", strip=True) if main_el else ""
        full_text = full_text[:8000]

        return {
            "url": url,
            "title": title,
            "summary": summary[:600],
            "last_updated": last_updated,
            "full_text": full_text,
        }

    def _extract_last_updated(self, soup: BeautifulSoup) -> Optional[str]:
        text = soup.get_text(" ", strip=True)
        m = re.search(r"(\d{1,2} \w+ \d{4})", text)
        if m:
            try:
                dt = datetime.strptime(m.group(1), "%d %B %Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None
        return None

    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        import json

        with open(raw_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        records: list[NormalizedRecord] = []
        for item in items:
            title: str = item.get("title", "HMRC charities guidance")
            summary: str = item.get("summary", "")
            full_text: str = item.get("full_text", "")

            last_updated = item.get("last_updated") or datetime.now().strftime("%Y-%m-%d")

            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
            record_id = f"HMRC_guidance_{slug}" if slug else f"HMRC_guidance_{int(datetime.now().timestamp())}"

            keywords = self._build_keywords(title, summary, full_text)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=last_updated,
                last_updated=last_updated,
                regulator="HMRC",
                domain="financial_reporting",
                document_type="guidance",
                keywords=keywords,
                full_text=full_text,
            )
            records.append(record)

        self.logger.info("Normalized %d HMRC guidance records", len(records))
        return records

    def _build_keywords(self, title: str, summary: str, full_text: str) -> list[str]:
        base = f"{title} {summary} {full_text[:500]}".lower()
        tokens = re.findall(r"[a-z]{4,}", base)
        unique: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            if token not in seen:
                unique.append(token)
                seen.add(token)
            if len(unique) >= 25:
                break
        return unique
