"""
Adapter for ICO enforcement actions.

Source: https://ico.org.uk/action-weve-taken/enforcement/
Method: CSV download + page scraping
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, SourceMetadata, NormalizedRecord


class ICOAdapter(BaseAdapter):
    """Fetches and normalizes ICO enforcement decisions."""
    
    ENFORCEMENT_URL = "https://ico.org.uk/action-weve-taken/enforcement/"
    
    # Keywords that indicate charity relevance
    CHARITY_KEYWORDS = [
        'charity', 'trust', 'foundation', 'association',
        'society', 'church', 'hospice', 'shelter', 'relief',
        'volunteer', 'not-for-profit', 'nonprofit'
    ]
    
    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="ICO Enforcement Actions",
            url=self.ENFORCEMENT_URL,
            regulator="ICO",
            update_frequency="weekly"
        )
    
    def download_raw(self) -> Path:
        """
        Scrape ICO enforcement page for cases.
        
        Note: ICO sometimes provides CSV downloads, but the structure varies.
        This scrapes the HTML tables which are more consistent.
        """
        import json
        
        self.logger.info("Fetching ICO enforcement page...")
        
        response = requests.get(self.ENFORCEMENT_URL, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html5lib')
        
        # Find enforcement tables
        cases = []
        
        # ICO uses tables with enforcement data
        tables = soup.select('table')
        
        for table in tables:
            rows = table.select('tr')
            headers = [th.get_text(strip=True).lower() for th in rows[0].select('th, td')]
            
            for row in rows[1:]:
                cells = row.select('td')
                if len(cells) < 3:
                    continue
                
                case_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        # Check for links
                        link = cell.select_one('a')
                        if link:
                            case_data[headers[i]] = cell.get_text(strip=True)
                            case_data[f"{headers[i]}_url"] = link.get('href', '')
                        else:
                            case_data[headers[i]] = cell.get_text(strip=True)
                
                if case_data:
                    cases.append(case_data)
        
        self.logger.info(f"Found {len(cases)} enforcement cases")
        
        # Save raw data
        output_path = self.staging_dir / "ico_enforcement_raw.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cases, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        """Convert raw ICO data to normalized records."""
        import json
        
        with open(raw_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        
        records = []
        for case in cases:
            # Try to find organization name
            org_name = (
                case.get('organisation') or
                case.get('name') or
                case.get('company') or
                'Unknown Organisation'
            )
            
            # Check charity relevance
            org_lower = org_name.lower()
            is_charity_relevant = any(kw in org_lower for kw in self.CHARITY_KEYWORDS)
            
            # Extract date
            date_str = case.get('date') or case.get('published')
            published_date = self._parse_date(date_str)
            
            # Extract fine amount
            fine_amount = self._extract_fine(case)
            
            # Generate ID
            date_part = published_date[:10].replace('-', '') if published_date else 'unknown'
            org_slug = re.sub(r'[^a-z0-9]', '', org_name.lower())[:20]
            record_id = f"ICO_enforcement_{org_slug}_{date_part}"
            
            # Build summary
            action_type = case.get('type') or case.get('action') or 'Enforcement action'
            summary = f"{action_type} against {org_name}."
            if fine_amount:
                summary += f" Fine: £{fine_amount:,.0f}."
            
            # Determine risk level based on fine
            risk_level = self._assess_risk(fine_amount, action_type)
            
            record = NormalizedRecord(
                id=record_id,
                title=f"ICO action: {org_name}",
                summary=summary[:500],
                source_url=case.get('organisation_url') or case.get('name_url') or self.ENFORCEMENT_URL,
                published_date=published_date or '1970-01-01',
                last_updated=published_date or '1970-01-01',
                regulator='ICO',
                domain='gdpr',
                document_type='enforcement',
                charity_name=org_name if is_charity_relevant else None,
                risk_level=risk_level,
                outcome=action_type,
                fine_amount=fine_amount,
                keywords=['data protection', 'gdpr', 'ico', action_type.lower()]
            )
            records.append(record)
        
        return records
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        
        # Common ICO date formats
        for fmt in ['%d/%m/%Y', '%d %B %Y', '%Y-%m-%d', '%B %Y']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _extract_fine(self, case: dict) -> Optional[float]:
        """Extract monetary fine from case data."""
        for key in ['fine', 'amount', 'penalty']:
            if key in case:
                text = case[key]
                # Extract number from strings like "£500,000"
                match = re.search(r'£?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', str(text))
                if match:
                    return float(match.group(1).replace(',', ''))
        return None
    
    def _assess_risk(self, fine_amount: Optional[float], action_type: str) -> str:
        """Assess risk level based on enforcement severity."""
        action_lower = action_type.lower()
        
        if fine_amount and fine_amount >= 100000:
            return 'critical'
        if fine_amount and fine_amount >= 10000:
            return 'high'
        if 'prosecution' in action_lower or 'criminal' in action_lower:
            return 'critical'
        if 'undertaking' in action_lower or 'reprimand' in action_lower:
            return 'medium'
        
        return 'low'
