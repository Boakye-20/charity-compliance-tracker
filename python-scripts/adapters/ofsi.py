"""
Adapter for OFSI UK Sanctions List.

Source: https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets
Method: Direct CSV/XML download
"""

import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests

from .base import BaseAdapter, SourceMetadata, NormalizedRecord


class OFSIAdapter(BaseAdapter):
    """Fetches and normalizes OFSI consolidated sanctions list."""
    
    # OFSI provides both XML and CSV downloads. The most reliable
    # approach is to scrape the dedicated consolidated-list page and
    # discover the current CSV download URL.
    CSV_URL = None  # Only used as a last-resort fallback
    XML_URL = None
    
    # Main publication page that lists current downloads
    DOWNLOAD_PAGE = (
        "https://www.gov.uk/government/publications/financial-sanctions-"
        "consolidated-list-of-targets/consolidated-list-of-targets"
    )
    
    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="OFSI UK Sanctions Consolidated List",
            url=self.DOWNLOAD_PAGE,
            regulator="OFSI",
            update_frequency="daily"
        )
    
    def download_raw(self) -> Path:
        """
        Download the consolidated sanctions list.
        
        Tries CSV first (smaller, easier to parse), falls back to XML.
        """
        output_path = self.staging_dir / "ofsi_sanctions_raw.csv"
        
        # First, get the download page to find current links
        self.logger.info("Fetching OFSI download page...")
        
        try:
            response = requests.get(self.DOWNLOAD_PAGE, timeout=30)
            response.raise_for_status()
            
            # Look for CSV download link on the consolidated-list page
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html5lib')
            
            csv_link = None
            for link in soup.select('a'):
                href = (link.get('href') or '').strip()
                text = link.get_text(strip=True).lower()
                href_lower = href.lower()

                # The consolidated list CSV is currently published as
                # https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv
                # on both GOV.UK and data.gov.uk. We therefore look for
                # any link that ends in .csv and references "conlist".
                if href_lower.endswith('.csv') and 'conlist' in href_lower:
                    csv_link = href
                    break
            
            if csv_link:
                # If the link is relative, make it absolute
                if csv_link.startswith('http'):
                    download_url = csv_link
                else:
                    download_url = f"https://www.gov.uk{csv_link}"
                self.logger.info(f"Found CSV link: {download_url}")
            else:
                raise RuntimeError("CSV link not found on OFSI page (no ConList.csv link)")
            
        except Exception as e:
            self.logger.warning(f"Could not parse download page, OFSI sanctions will be skipped: {e}")
            # Let the caller handle the failure by raising so the adapter is marked as failed
            raise
        
        # Download the file
        self.logger.info(f"Downloading sanctions list from {download_url}")
        response = requests.get(download_url, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        self.logger.info(f"Downloaded {len(response.content)} bytes")
        return output_path
    
    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        """Convert OFSI CSV to normalized records."""
        records = []
        
        with open(raw_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)
            
            for row in reader:
                record = self._normalize_row(row)
                if record:
                    records.append(record)
        
        self.logger.info(f"Normalized {len(records)} sanctions entries")
        return records
    
    def _normalize_row(self, row: dict) -> Optional[NormalizedRecord]:
        """Normalize a single sanctions list row."""
        # OFSI CSV columns vary but typically include:
        # Name, Group Type, Regime, Listed On, etc.
        
        name = (
            row.get('Name 6') or  # Primary name column in some versions
            row.get('name') or
            row.get('Name') or
            row.get('Primary name') or
            ''
        )
        
        if not name or len(name.strip()) < 2:
            return None
        
        # Get other fields
        group_type = row.get('Group Type', row.get('Type', 'Unknown'))
        regime = (
            row.get('Regime', '') or
            row.get('Sanctions Regime', '') or
            row.get('regime', '')
        )
        listed_date = row.get('Listed On', row.get('Date Listed', ''))
        
        # Build ID
        name_slug = ''.join(c for c in name.lower() if c.isalnum())[:30]
        record_id = f"OFSI_sanction_{name_slug}"
        
        # Parse date
        published_date = self._parse_date(listed_date) or datetime.now().strftime('%Y-%m-%d')
        
        # Get designating authority
        designated_by = row.get('UK Statement of Reasons', '')
        if 'UN' in designated_by.upper():
            designated_by = 'UN'
        elif 'EU' in designated_by.upper():
            designated_by = 'EU'
        else:
            designated_by = 'UK'
        
        # Build summary
        summary = f"{name} is designated under {regime} sanctions regime."
        if group_type:
            summary = f"{group_type}: {summary}"
        
        return NormalizedRecord(
            id=record_id,
            title=f"Sanctions: {name[:100]}",
            summary=summary[:500],
            source_url=self.DOWNLOAD_PAGE,
            published_date=published_date,
            last_updated=datetime.now().strftime('%Y-%m-%d'),
            regulator='OFSI',
            domain='sanctions',
            document_type='sanction',
            risk_level='critical',  # All sanctions are high risk
            sanctions_regime=regime,
            designated_by=designated_by,
            keywords=['sanctions', 'ofsi', regime.lower(), group_type.lower()]
        )
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse OFSI date formats."""
        if not date_str:
            return None
        
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d %b %Y']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
