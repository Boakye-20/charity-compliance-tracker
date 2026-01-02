"""Adapter for HSE (Health and Safety Executive) guidance relevant to charities.

Rather than crawling the whole HSE site, this adapter focuses on a curated list
of high‑value pages (volunteers, fundraising, charity retail, etc.). You can
extend the HSE_PAGES list over time.

Example primary source (from DATA_SOURCES.md):
    https://www.hse.gov.uk/voluntary/work-types/charity-retail-and-fundraising-activities.htm
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, NormalizedRecord, SourceMetadata


class HSEAdapter(BaseAdapter):
    """Fetch and normalize a curated set of HSE guidance pages."""

    HSE_PAGES = [
        # Core page from your DATA_SOURCES list
        "https://www.hse.gov.uk/voluntary/work-types/charity-retail-and-fundraising-activities.htm",
        # Additional charity/voluntary guidance pages
        "https://www.hse.gov.uk/voluntary/index.htm", # Main voluntary sector page
        "https://www.hse.gov.uk/contact/faqs/charities.htm", # Charity FAQs
        "https://www.hse.gov.uk/voluntary/about.htm", # About voluntary organizations
        "https://www.hse.gov.uk/voluntary/resources.htm", # Resources for voluntary organizations
        "https://www.hse.gov.uk/voluntary/work-types/events.htm", # Charity events guidance
        "https://www.hse.gov.uk/voluntary/work-types/outdoor.htm", # Outdoor activities
        "https://www.hse.gov.uk/simple-health-safety/risk/index.htm", # Risk assessment guidance
    ]

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="HSE charity‑relevant guidance",
            url="https://www.hse.gov.uk/voluntary/",
            regulator="HSE",
            update_frequency="annual",
        )

    def download_raw(self) -> Path:
        import json

        records: list[dict] = []

        for i, url in enumerate(self.HSE_PAGES):
            self.logger.info("[%d/%d] Fetching HSE guidance page: %s", i + 1, len(self.HSE_PAGES), url)
            try:
                data = self._fetch_page(url)
                if data:
                    records.append(data)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("Failed to fetch %s: %s", url, exc)

        output_path = self.staging_dir / "hse_guidance_raw.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        return output_path

    def _fetch_page(self, url: str) -> Optional[dict]:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html5lib")

        title_el = soup.select_one("h1")
        title = title_el.get_text(strip=True) if title_el else "HSE guidance"

        # Try meta description first
        desc_meta = soup.select_one('meta[name="description"]')
        if desc_meta and desc_meta.get("content"):
            summary = desc_meta["content"].strip()
        else:
            # Fallback: first paragraph in main content
            p = soup.select_one("main p, #content p, .content p")
            summary = p.get_text(strip=True) if p else ""

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
        # HSE sometimes uses phrases like "Page last reviewed: 01 May 2023"
        text = soup.get_text(" ", strip=True)
        m = re.search(r"(\d{1,2} \w+ \d{4})", text)
        if m:
            parsed = self._parse_human_date(m.group(1))
            if parsed:
                return parsed
        return None

    def _parse_human_date(self, value: str) -> Optional[str]:
        value = value.strip()
        for fmt in ("%d %B %Y", "%d %b %Y"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        import json

        with open(raw_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        records: list[NormalizedRecord] = []
        for item in items:
            title: str = item.get("title", "HSE guidance")
            summary: str = item.get("summary", "")
            full_text: str = item.get("full_text", "")

            # Prefer scraped "last reviewed" dates; if none are present,
            # use a stable placeholder instead of the current date so the
            # UI doesn't show everything as updated "today".
            last_updated = item.get("last_updated") or "1970-01-01"

            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
            record_id = f"HSE_guidance_{slug}" if slug else f"HSE_guidance_{int(datetime.now().timestamp())}"

            keywords = self._build_keywords(title, summary, full_text)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=last_updated,
                last_updated=last_updated,
                regulator="HSE",
                domain="health_safety",
                document_type="guidance",
                keywords=keywords,
                full_text=full_text,
            )
            records.append(record)

        self.logger.info("Normalized %d HSE guidance records", len(records))
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
