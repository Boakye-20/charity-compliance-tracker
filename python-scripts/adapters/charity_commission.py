"""
Adapter for Charity Commission inquiry reports.

Source: https://www.gov.uk/government/collections/charity-inquiry-reports
Method: Web scraping (HTML pages)
"""

import re
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup

from .base import BaseAdapter, SourceMetadata, NormalizedRecord


class CharityCommissionAdapter(BaseAdapter):
    # Key inquiry reports with known publication dates
    KNOWN_DATES = {
        "https://www.gov.uk/government/publications/charity-inquiry-mountain-of-fire-and-miracles-ministries-international": "2023-10-20",
        "https://www.gov.uk/government/publications/charity-inquiry-obac-organisation-of-blind-africans-and-caribbeans": "2023-07-01",
        "https://www.gov.uk/government/publications/charity-inquiry-four-paws-animal-rescue-south-wales": "2023-11-05",
        "https://www.gov.uk/government/publications/charity-inquiry-island-health-trust": "2023-07-03",
        "https://www.gov.uk/government/publications/charity-inquiry-the-sikh-channel-community-broadcasting-company-limited": "2023-02-28",
        "https://www.gov.uk/government/publications/charity-inquiry-brighton-mosque-muslim-community-centre": "2023-01-22",
        "https://www.gov.uk/government/publications/charity-inquiry-quba-trust": "2023-12-19",
        "https://www.gov.uk/government/publications/charity-inquiry-muffin-pug-rescue": "2023-12-05",
        "https://www.gov.uk/government/publications/charity-inquiry-the-captain-tom-foundation": "2023-11-21",
        "https://www.gov.uk/government/publications/charity-inquiry-the-knightland-foundation": "2023-11-15",
    }
    """Fetches and normalizes Charity Commission inquiry reports."""
    
    BASE_URL = "https://www.gov.uk"
    COLLECTION_URL = f"{BASE_URL}/government/collections/inquiry-reports-charity-commission"
    
    # Rate limiting
    REQUEST_DELAY = 1.0  # seconds between requests

    # Scrape all years (no filter)
    YEAR_FILTER = None
    
    # Domain mapping from CC issue tags
    ISSUE_TO_DOMAIN = {
        'safeguarding': 'safeguarding',
        'child protection': 'safeguarding',
        'vulnerable adults': 'safeguarding',
        'vulnerable beneficiaries': 'safeguarding',
        'governance': 'governance',
        'trustee duties': 'governance',
        'conflicts of interest': 'governance',
        'financial': 'financial_reporting',
        'financial controls': 'financial_reporting',
        'accounts': 'financial_reporting',
        'fraud': 'anti_fraud',
        'money laundering': 'anti_fraud',
        'terrorist financing': 'anti_fraud',
        'terrorism': 'anti_fraud',
        'data protection': 'gdpr',
        'health and safety': 'health_safety',
        'risk': 'risk_management',
    }
    
    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Charity Commission Inquiry Reports",
            url=self.COLLECTION_URL,
            regulator="CC",
            update_frequency="monthly"
        )
    
    def download_raw(self) -> Path:
        """
        Download all case report pages.
        
        Returns path to JSON file containing all scraped data.
        """
        import json
        
        # Crawl paginated collection (each page lists ~30 cases)
        import json

        def extract_links(page_soup):
            links: list[str] = []
            for link in page_soup.select('a.govuk-link'):
                href = link.get('href', '')
                if '/government/publications/' in href and 'inquiry' in href.lower():
                    full = href if href.startswith('http') else f"{self.BASE_URL}{href}"
                    links.append(full)
            return links
        report_links: list[str] = []
        page_num = 1
        while True:
            page_url = self.COLLECTION_URL if page_num == 1 else f"{self.COLLECTION_URL}?page={page_num}"
            self.logger.info("Fetching collection page %s", page_url)
            resp = requests.get(page_url, timeout=30)
            if resp.status_code == 404:
                break  # no more pages
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html5lib')
            new_links = extract_links(soup)
            if not new_links:
                break
            report_links.extend(new_links)

            next_link = soup.find('link', rel='next') or soup.find('a', rel='next')
            if not next_link:
                break
            page_num += 1
            if page_num > 25:  # safety guard
                self.logger.warning("Stopping CC pagination after 25 pages for safety")
                break

        self.logger.info("Total inquiry links collected: %d", len(report_links))

        # Fetch each report page (all years)
        reports: list[dict] = []
        for i, url in enumerate(report_links):
            self.logger.info("Fetching report %d/%d", i + 1, len(report_links))
            try:
                time.sleep(self.REQUEST_DELAY)
                data = self._fetch_report_page(url)
                if data:
                    reports.append(data)
            except Exception as exc:
                self.logger.warning("Failed to fetch %s: %s", url, exc)
                continue
        
        # Save to staging
        output_path = self.staging_dir / "cc_cases_raw.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _fetch_report_page(self, url: str) -> Optional[dict]:
        """Fetch and parse a single report page."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html5lib')
        
        # Extract title
        title_elem = soup.select_one('h1')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"
        
        # Use hardcoded date if available
        if url in self.KNOWN_DATES:
            published_date = self.KNOWN_DATES[url]
        else:
            # Extract publication date - GOV.UK pages often have this in metadata
            # or a standard "Published DD Month YYYY" format at top of pages
            published_date: Optional[str] = None
            
            # Try method 1: Standard <time> element with datetime attribute 
            date_elem = soup.select_one('time, .published-dates')
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                published_date = self._parse_date(date_str)

            # Method 2: GOV.UK standard published date block
            if not published_date:
                pub_div = soup.select_one('.app-c-published-dates, .gem-c-metadata, .gem-c-inverse-header__subtext')
                if pub_div:
                    pub_text = pub_div.get_text(" ", strip=True).lower()
                    if 'published' in pub_text:
                        m = re.search(r"published[: ]+(\d{1,2} [A-Za-z]+ 20\d{2})", pub_text, re.IGNORECASE)
                        if m:
                            published_date = self._parse_date(m.group(1))
            
            # Method 3: Meta tags
            if not published_date:
                meta_pub = soup.select_one('meta[name="govuk:published-date"], meta[property="article:published_time"]')
                if meta_pub and meta_pub.get('content'):
                    content = meta_pub.get('content')
                    if 'T' in content:
                        content = content.split('T')[0]
                    published_date = content if re.match(r'\d{4}-\d{2}-\d{2}', content) else None

            # Method 4: Look for any "published" text with a date near it
            if not published_date:
                for p in soup.select('p, div'):
                    text = p.get_text(" ", strip=True).lower()
                    if 'published' in text:
                        m = re.search(r"published[: ]*(\d{1,2} [A-Za-z]+ 20\d{2})", text, re.IGNORECASE)
                        if m:
                            published_date = self._parse_date(m.group(1))                        
                            break

            # Method 5: Fallback to any date pattern in the document
            if not published_date:
                text = soup.get_text(" ", strip=True)
                m = re.search(r"(\d{1,2}\s+[A-Za-z]+\s+20\d{2})", text)
                if m:
                    parsed = self._parse_date(m.group(1))
                    if parsed:
                        published_date = parsed
        
        # Extract summary
        summary_elem = soup.select_one('.govuk-body-l, .gem-c-lead-paragraph')
        summary = summary_elem.get_text(strip=True) if summary_elem else ""
        
        # Extract charity details from content
        content = soup.select_one('.govuk-govspeak, article')
        content_text = content.get_text() if content else ""
        
        charity_number = self._extract_charity_number(content_text)
        charity_name = self._extract_charity_name(title, content_text)
        issues = self._extract_issues(title, summary, content_text)
        outcome = self._extract_outcome(content_text)
        
        return {
            'url': url,
            'title': title,
            'summary': summary[:500] if summary else "",
            'published_date': published_date,
            'charity_number': charity_number,
            'charity_name': charity_name,
            'issues': issues,
            'outcome': outcome,
            'full_text': content_text[:5000] if content_text else ""
        }
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to ISO format."""
        if not date_str:
            return None
            
        # Try ISO format first
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str[:10]
        
        # Try common UK formats
        for fmt in ['%d %B %Y', '%d %b %Y', '%B %Y']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _extract_charity_number(self, text: str) -> Optional[str]:
        """Extract charity registration number from text."""
        # Charity numbers are typically 6-7 digits
        match = re.search(r'(?:charity\s+(?:number|no\.?|registration)?\s*:?\s*)(\d{6,7})', 
                         text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Also try standalone 7-digit numbers near "registered"
        match = re.search(r'registered[^\d]*(\d{7})', text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_charity_name(self, title: str, text: str) -> Optional[str]:
        """Extract charity name - often in the title."""
        # Often format is "Charity inquiry: [Name]"
        if ':' in title:
            name = title.split(':', 1)[1].strip()
            # Remove common suffixes
            name = re.sub(r'\s*-\s*conclud.*$', '', name, flags=re.IGNORECASE)
            return name
        return None
    
    def _extract_issues(self, title: str, summary: str, text: str) -> list[str]:
        """Heuristically derive issue domains from the report text.

        We look for a richer set of phrases across the title, summary and
        main body. Domains are added in order of specificity, and we only
        fall back to plain governance if nothing else matches.
        """
        combined = f"{title}\n{summary}\n{text}".lower()
        issues: list[str] = []

        def any_kw(kws: list[str]) -> bool:
            return any(kw in combined for kw in kws)

        # Safeguarding / protection of people
        if any_kw([
            'safeguard', 'safeguarding', 'child protection', 'vulnerable adult',
            'vulnerable beneficiary', 'sexual abuse', 'physical abuse',
            'emotional abuse', 'neglect', 'harm to beneficiaries'
        ]):
            issues.append('safeguarding')

        # Data protection / privacy
        if any_kw([
            'data protection', 'personal data', 'gdpr', 'uk gdpr',
            'information commissioner', 'ico', 'data breach', 'loss of data',
            'unlawful processing'
        ]):
            issues.append('gdpr')

        # Health & safety
        if any_kw([
            'health and safety', 'health & safety', 'hse', 'risk assessment',
            'safe systems of work', 'fire safety', 'fire risk',
        ]):
            issues.append('health_safety')

        # Financial reporting / controls
        if any_kw([
            'financial controls', 'inadequate financial controls',
            'accounting records', 'accounts', 'financial mismanagement',
            'funds misapplied', 'unauthorised payment', 'unauthorized payment',
            'loan to trustee', 'related party transaction', 'sorp'
        ]):
            issues.append('financial_reporting')

        # Anti‑fraud / criminal finance
        if any_kw([
            'fraud', 'fraudulent', 'false accounting', 'money laundering',
            'terrorist financing', 'terrorism', 'theft', 'misappropriation',
            'misuse of funds'
        ]):
            issues.append('anti_fraud')

        # Risk management and internal control
        if any_kw([
            'risk management', 'risk register', 'risk framework',
            'internal control', 'internal controls', 'poor risk management',
            'lack of risk management', 'due diligence'
        ]):
            issues.append('risk_management')

        # Governance catch‑all: only if nothing more specific matched
        if not issues:
            issues.append('governance')

        return issues
    
    def _extract_outcome(self, text: str) -> Optional[str]:
        """Extract the regulatory outcome."""
        outcomes = []
        text_lower = text.lower()
        
        if 'removed from the register' in text_lower:
            outcomes.append('charity removed')
        if 'official warning' in text_lower:
            outcomes.append('warning issued')
        if 'action plan' in text_lower:
            outcomes.append('action plan required')
        if 'trustees removed' in text_lower or 'trustee removed' in text_lower:
            outcomes.append('trustees removed')
        if 'no regulatory action' in text_lower:
            outcomes.append('no action')
        if 'monitoring' in text_lower:
            outcomes.append('ongoing monitoring')
        
        return ', '.join(outcomes) if outcomes else None
    
    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        """Convert raw JSON to normalized records."""
        import json
        
        with open(raw_path, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        records = []
        for report in reports:
            # Determine primary domain from issues
            issues = report.get('issues', [])
            primary_domain = issues[0] if issues else 'governance'

            # Use scraped publication date where possible; fall back to a
            # stable placeholder instead of "today" so dates don't all look
            # like the last pipeline run.
            published = report.get('published_date') or '1970-01-01'

            # Generate unique ID
            published_raw = published or 'unknown'
            date_part = str(published_raw)[:10].replace('-', '')
            charity_part = report.get('charity_number', 'unknown')
            record_id = f"CC_case_{charity_part}_{date_part}"
            
            record = NormalizedRecord(
                id=record_id,
                title=report.get('title', 'Unknown Case'),
                summary=report.get('summary', '')[:500],
                source_url=report.get('url', ''),
                published_date=published,
                last_updated=published,
                regulator='CC',
                domain=primary_domain,
                document_type='case',
                charity_number=report.get('charity_number'),
                charity_name=report.get('charity_name'),
                case_status='concluded',
                outcome=report.get('outcome'),
                issues_identified=issues,
                keywords=self._generate_keywords(report)
            )
            records.append(record)
        
        return records
    
    def _generate_keywords(self, report: dict) -> list[str]:
        """Generate search keywords from report content."""
        keywords = set()
        
        # Add issues
        keywords.update(report.get('issues', []))
        
        # Add charity name words
        if report.get('charity_name'):
            words = report['charity_name'].lower().split()
            keywords.update(w for w in words if len(w) > 3)
        
        # Add outcome words
        if report.get('outcome'):
            keywords.update(report['outcome'].lower().split(', '))
        
        return list(keywords)[:20]  # Limit to 20 keywords
