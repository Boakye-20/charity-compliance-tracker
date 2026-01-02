"""Adapter for Charity Commission guidance documents.

Source index: https://www.gov.uk/guidance/charity-commission-guidance
Method: Scrape index page for guidance links, then fetch each page.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, NormalizedRecord, SourceMetadata


class CharityGuidanceAdapter(BaseAdapter):
    """Fetch and normalize Charity Commission guidance documents."""
    
    # Known publication dates for GOV.UK guidance pages
    # These are gathered manually from the "Published" dates on each page
    KNOWN_DATES = {
        "https://www.gov.uk/guidance/making-decisions-at-a-charity": "2018-05-01",
        "https://www.gov.uk/guidance/managing-charity-finances": "2018-04-10", 
        "https://www.gov.uk/guidance/managing-conflicts-of-interest-in-a-charity": "2019-05-06",
        "https://www.gov.uk/guidance/what-to-send-to-the-charity-commission-and-how-to-get-help": "2018-06-15",
        "https://www.gov.uk/guidance/charity-commission-guidance": "2015-03-17",
        "https://www.gov.uk/guidance/charity-reporting-and-accounting-the-essentials": "2016-11-03",
    }

    BASE_URL = "https://www.gov.uk"
    COLLECTION_URL = "https://www.gov.uk/guidance/charity-commission-guidance"

    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity Commission Guidance",
            url=self.COLLECTION_URL,
            regulator="CC",
            update_frequency="quarterly",
        )

    def download_raw(self) -> Path:
        import json

        self.logger.info("Fetching Charity Commission guidance index page...")

        response = requests.get(self.COLLECTION_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html5lib")

        links: set[str] = set()
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if not href:
                continue
            if href.startswith("#"):
                continue
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue

            # Keep GOV.UK guidance/publication pages that look like CC guidance
            if "/guidance/" in href or "/government/publications/" in href:
                if "charity" in href:
                    full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    links.add(full_url)

        self.logger.info("Found %d potential guidance links", len(links))

        records: list[dict] = []
        for i, url in enumerate(sorted(links)):
            self.logger.info("[%d/%d] Fetching guidance page: %s", i + 1, len(links), url)
            try:
                page_data = self._fetch_guidance_page(url)
                if page_data:
                    records.append(page_data)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("Failed to fetch %s: %s", url, exc)

        output_path = self.staging_dir / "cc_guidance_raw.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        return output_path

    def _fetch_guidance_page(self, url: str) -> Optional[dict]:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html5lib")

        title_el = soup.select_one("h1")
        title = title_el.get_text(strip=True) if title_el else "Untitled guidance"

        summary_el = soup.select_one(".gem-c-lead-paragraph, .govuk-body-l")
        if not summary_el:
            # Fallback: first paragraph in main content
            summary_el = soup.select_one("main p, .govuk-main-wrapper p")
        summary = summary_el.get_text(strip=True) if summary_el else ""

        last_updated = self._extract_last_updated(soup)

        # Extract a chunk of main text for keywording/search context
        content_el = soup.select_one(".govuk-govspeak, article, main")
        full_text = content_el.get_text(" ", strip=True) if content_el else ""
        full_text = full_text[:8000]

        # Use hardcoded date if available, otherwise use scraped date
        if url in self.KNOWN_DATES:
            date = self.KNOWN_DATES[url]
        else:
            date = last_updated
            
        return {
            "url": url,
            "title": title,
            "summary": summary[:600],
            "last_updated": date,
            "full_text": full_text,
        }

    def _extract_last_updated(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the last updated or publication date using multiple methods."""
        # Method 1: Standard <time> elements
        time_el = soup.select_one("time")
        if time_el is not None:
            dt_attr = time_el.get("datetime")
            if dt_attr:
                if re.match(r"\d{4}-\d{2}-\d{2}", dt_attr):
                    return dt_attr[:10]
            text = time_el.get_text(strip=True)
            parsed = self._parse_human_date(text)
            if parsed:
                return parsed

        # Method 2: GOV.UK published date block
        pub_div = soup.select_one('.app-c-published-dates, .gem-c-metadata, .gem-c-inverse-header__subtext')
        if pub_div:
            pub_text = pub_div.get_text(" ", strip=True).lower()
            if 'published' in pub_text:
                m = re.search(r"published[: ]+(\d{1,2} [A-Za-z]+ 20\d{2})", pub_text, re.IGNORECASE)
                if m:
                    parsed = self._parse_human_date(m.group(1))
                    if parsed:
                        return parsed
            elif 'updated' in pub_text or 'last updated' in pub_text:
                m = re.search(r"updated[: ]+(\d{1,2} [A-Za-z]+ 20\d{2})", pub_text, re.IGNORECASE)
                if m:
                    parsed = self._parse_human_date(m.group(1))
                    if parsed:
                        return parsed

        # Method 3: Meta tags (common in GOV.UK and many CMS platforms)
        meta_tags = [       
            'meta[name="govuk:published-date" i]',
            'meta[name="dc.date" i]', 
            'meta[property="article:modified_time" i]',
            'meta[property="article:published_time" i]',
        ]
        for selector in meta_tags:
            meta_date = soup.select_one(selector)
            if meta_date and meta_date.get("content"):
                content = meta_date.get("content")
                if 'T' in content:  # Handle ISO-8601 format with time
                    content = content.split("T")[0]
                if re.match(r"\d{4}-\d{2}-\d{2}", content):
                    return content
                parsed = self._parse_human_date(content)
                if parsed:
                    return parsed

        # Method 4: Explicit "Last updated" or "Published" text blocks
        for el in soup.select("p, li, dd, dt, span, div"):
            text = el.get_text(" ", strip=True).lower()
            if 'last updated' in text or 'updated' in text:
                m = re.search(r"updated[: ]*(\d{1,2} [A-Za-z]+ 20\d{2})", text, re.IGNORECASE)
                if m:
                    parsed = self._parse_human_date(m.group(1))
                    if parsed:
                        return parsed
            elif 'published' in text or 'first published' in text:
                m = re.search(r"published[: ]*(\d{1,2} [A-Za-z]+ 20\d{2})", text, re.IGNORECASE)
                if m:
                    parsed = self._parse_human_date(m.group(1))
                    if parsed:
                        return parsed

        # Method 5: Look for any date pattern in the page (least reliable)
        text_all = soup.get_text(" ", strip=True)
        m = re.search(r"(\d{1,2} [A-Za-z]+ 20\d{2})", text_all)
        if m:
            parsed = self._parse_human_date(m.group(1))
            if parsed:
                return parsed

        # No date found
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
            title: str = item.get("title", "Untitled guidance")
            summary: str = item.get("summary", "")
            full_text: str = item.get("full_text", "")

            domain = self._infer_domain(title, summary, full_text)
            # Use extracted last_updated where possible; otherwise fall back
            # to a stable placeholder so dates don't all equal the pipeline
            # run date.
            last_updated = item.get("last_updated") or "1970-01-01"

            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
            record_id = f"CC_guidance_{slug}" if slug else f"CC_guidance_{int(datetime.now().timestamp())}"

            keywords = self._build_keywords(title, summary, full_text)

            record = NormalizedRecord(
                id=record_id,
                title=title,
                summary=summary,
                source_url=item.get("url", ""),
                published_date=last_updated,
                last_updated=last_updated,
                regulator="CC",
                domain=domain,
                document_type="guidance",
                keywords=keywords,
                full_text=full_text,
            )
            records.append(record)

        self.logger.info("Normalized %d Charity Commission guidance records", len(records))
        return records

    def _infer_domain(self, title: str, summary: str, full_text: str) -> str:
        text = " ".join([title, summary, full_text[:2000]]).lower()

        mapping = {
            "safeguard": "safeguarding",
            "protection": "safeguarding",
            "dbs": "safeguarding",
            "trustee": "governance",
            "board": "governance",
            "governance": "governance",
            "data protection": "gdpr",
            "gdpr": "gdpr",
            "privacy": "gdpr",
            "health and safety": "health_safety",
            "risk assessment": "health_safety",
            "risk": "risk_management",
            "internal control": "risk_management",
            "fraud": "anti_fraud",
            "money laundering": "anti_fraud",
            "sanction": "sanctions",
            "accounts": "financial_reporting",
            "financial reporting": "financial_reporting",
            "sorp": "financial_reporting",
        }

        for keyword, domain in mapping.items():
            if keyword in text:
                return domain

        return "governance"

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
