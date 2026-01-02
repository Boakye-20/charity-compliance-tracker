#!/usr/bin/env python3
"""
Build analytics.json from charity_policies.csv for the Analytics dashboard.

Generates aggregated data for:
- Time-series: inquiries/enforcement by month and domain
- Breakdowns: by regulator, income band, region, status
- Top keywords by year
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any

# Paths
ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = ROOT / "data"
CSV_FILE = DATA_DIR / "charity_policies.csv"
OUTPUT_FILE = DATA_DIR / "analytics.json"


def parse_income_band(income_str: str) -> str:
    """Categorize income into bands."""
    if not income_str:
        return "Unknown"
    
    try:
        income = float(income_str)
        if income < 10_000:
            return "Under £10k"
        elif income < 100_000:
            return "£10k-£100k"
        elif income < 500_000:
            return "£100k-£500k"
        elif income < 1_000_000:
            return "£500k-£1m"
        elif income < 5_000_000:
            return "£1m-£5m"
        else:
            return "Over £5m"
    except (ValueError, TypeError):
        return "Unknown"


def extract_keywords(text: str, min_length: int = 4) -> List[str]:
    """Extract meaningful keywords from text."""
    if not text:
        return []
    
    # Simple tokenization and filtering
    import re
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter out common words
    stopwords = {
        'charity', 'commission', 'inquiry', 'report', 'the', 'and', 'for',
        'with', 'from', 'that', 'this', 'have', 'been', 'were', 'their',
        'about', 'into', 'which', 'other', 'some', 'what', 'when', 'where',
        'will', 'would', 'could', 'should', 'also', 'more', 'than', 'such'
    }
    
    keywords = [w for w in words if len(w) >= min_length and w not in stopwords]
    return keywords


def build_analytics():
    """Generate analytics.json from the CSV."""
    if not CSV_FILE.exists():
        print(f"Error: CSV file not found at {CSV_FILE}")
        return
    
    print(f"Reading from: {CSV_FILE}")
    
    # Counters and aggregators
    by_month_domain = Counter()
    by_month_regulator = Counter()
    by_regulator = Counter()
    by_domain = Counter()
    by_document_type = Counter()
    by_income_band = Counter()
    by_status = Counter()
    by_region = Counter()
    by_year_keywords = defaultdict(Counter)
    
    total_records = 0
    case_records = 0
    guidance_records = 0
    
    # Read and aggregate
    with CSV_FILE.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_records += 1
            
            # Extract fields
            pub_date_str = row.get('published_date', '')
            domain = row.get('domain', 'unknown')
            regulator = row.get('regulator', 'unknown')
            doc_type = row.get('document_type', 'unknown')
            income = row.get('cc_latest_income', '')
            status = row.get('cc_status', '')
            region = row.get('cc_primary_region', '')
            title = row.get('title', '')
            summary = row.get('summary', '')
            
            # Parse date
            try:
                pub_date = datetime.fromisoformat(pub_date_str)
                month = pub_date.strftime('%Y-%m')
                year = pub_date.year
            except (ValueError, TypeError):
                month = 'unknown'
                year = None
            
            # Count by document type
            if doc_type == 'case':
                case_records += 1
            elif doc_type == 'guidance':
                guidance_records += 1
            
            # Time-series aggregations
            if month != 'unknown':
                by_month_domain[(month, domain)] += 1
                by_month_regulator[(month, regulator)] += 1
            
            # Categorical aggregations
            by_regulator[regulator] += 1
            by_domain[domain] += 1
            by_document_type[doc_type] += 1
            
            # Enriched field aggregations
            if income:
                band = parse_income_band(income)
                by_income_band[band] += 1
            
            if status:
                by_status[status] += 1
            
            if region:
                by_region[region] += 1
            
            # Keywords by year
            if year and doc_type == 'case':
                keywords = extract_keywords(f"{title} {summary}")
                for kw in keywords:
                    by_year_keywords[year][kw] += 1
    
    # Build output structure
    analytics = {
        "summary": {
            "total_records": total_records,
            "case_records": case_records,
            "guidance_records": guidance_records,
            "last_updated": datetime.now().isoformat()
        },
        "time_series": {
            "by_month_domain": [
                {"month": m, "domain": d, "count": c}
                for (m, d), c in sorted(by_month_domain.items())
            ],
            "by_month_regulator": [
                {"month": m, "regulator": r, "count": c}
                for (m, r), c in sorted(by_month_regulator.items())
            ]
        },
        "breakdowns": {
            "by_regulator": [
                {"regulator": r, "count": c}
                for r, c in by_regulator.most_common()
            ],
            "by_domain": [
                {"domain": d, "count": c}
                for d, c in by_domain.most_common()
            ],
            "by_document_type": [
                {"type": t, "count": c}
                for t, c in by_document_type.most_common()
            ],
            "by_income_band": [
                {"band": b, "count": c}
                for b, c in by_income_band.most_common()
            ],
            "by_status": [
                {"status": s, "count": c}
                for s, c in by_status.most_common()
            ],
            "by_region": [
                {"region": r, "count": c}
                for r, c in by_region.most_common(10)  # Top 10 regions
            ]
        },
        "keywords": {
            str(year): [
                {"keyword": kw, "count": c}
                for kw, c in keywords.most_common(20)  # Top 20 per year
            ]
            for year, keywords in sorted(by_year_keywords.items())
        }
    }
    
    # Write output
    with OUTPUT_FILE.open('w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)
    print("Analytics generated successfully!")
    print(f"Output: {OUTPUT_FILE}")
    print()
    print("Summary:")
    print(f"  Total records: {total_records}")
    print(f"  Cases: {case_records}")
    print(f"  Guidance: {guidance_records}")
    print(f"  Regulators: {len(by_regulator)}")
    print(f"  Domains: {len(by_domain)}")
    print()
    print("Top regulators:")
    for reg, count in by_regulator.most_common(5):
        print(f"  {reg}: {count}")
    print()
    print("Top domains:")
    for dom, count in by_domain.most_common(5):
        print(f"  {dom}: {count}")


if __name__ == "__main__":
    build_analytics()
