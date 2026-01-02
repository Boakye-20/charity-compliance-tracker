#!/usr/bin/env python3
"""
Main orchestrator for the Charity Compliance Tracker data pipeline.

This script:
1. Runs all source adapters to fetch raw data
2. Normalizes data to common schema
3. Merges with existing data
4. Saves to CSV for use by the Next.js application

Run with:
    python run_charity_update.py

Options:
    --source NAME     Run a single source adapter
    --dry-run         Don't save output files
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path
import importlib

from adapters import (
    CharityCommissionAdapter,
    CharityGuidanceAdapter,
    HSEAdapter,
    ICOAdapter,
    HMRCAdapter,
    FundraisingRegulatorAdapter,
    SafeguardingAdapter,
    DataProtectionAdapter,
    FinancialReportingAdapter,
    RiskManagementAdapter,
    AntiFraudAdapter,
    NormalizedRecord,
)

# Setup paths
_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = _ROOT / "data"
STAGING_DIR = DATA_DIR / "staging"
REVIEW_DIR = DATA_DIR / "review"
OUTPUT_FILE = DATA_DIR / "charity_policies.csv"

# CSV column order (must match schema)
CSV_COLUMNS = [
    'id', 'title', 'summary', 'source_url', 'published_date', 'last_updated',
    'regulator', 'domain', 'document_type', 'charity_number', 'charity_name',
    'charity_income_band', 'risk_level', 'case_id', 'case_status', 'outcome',
    'issues_identified', 'sanctions_regime', 'designated_by', 'fine_amount',
    'keywords'
]

# Source registry
SOURCES = {
    'cc': CharityCommissionAdapter,
    'cc_guidance': CharityGuidanceAdapter,
    'ico': ICOAdapter,
    'hse': HSEAdapter,
    'hmrc': HMRCAdapter,
    'fr': FundraisingRegulatorAdapter,
    'safeguarding': SafeguardingAdapter,
    'data_protection': DataProtectionAdapter,
    'financial_reporting': FinancialReportingAdapter,
    'risk_management': RiskManagementAdapter,
    'anti_fraud': AntiFraudAdapter,
}


def load_existing_records() -> dict[str, dict]:
    """Load existing records from CSV, keyed by ID."""
    records = {}
    
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records[row['id']] = row
    
    return records


def merge_records(
    existing: dict[str, dict],
    new_records: list[NormalizedRecord]
) -> list[dict]:
    """
    Merge new records with existing, handling deduplication.
    
    Strategy:
    - If ID exists and last_updated is newer, update
    - If ID is new, add
    - Keep existing records not in new batch (from other sources)
    """
    merged = dict(existing)  # Copy
    
    for record in new_records:
        row = record.to_csv_row()
        record_id = row['id']
        
        if record_id in merged:
            # Check if newer
            existing_date = merged[record_id].get('last_updated', '')
            new_date = row.get('last_updated', '')
            
            if new_date > existing_date:
                merged[record_id] = row
                print(f"  Updated: {record_id}")
        else:
            merged[record_id] = row
            print(f"  Added: {record_id}")
    
    return list(merged.values())


def save_records(records: list[dict], output_path: Path):
    """Save records to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
        writer.writeheader()
        
        # Sort by date descending
        sorted_records = sorted(
            records,
            key=lambda r: r.get('published_date', ''),
            reverse=True
        )
        
        for record in sorted_records:
            writer.writerow(record)
    
    print(f"Saved {len(records)} records to {output_path}")


def run_pipeline(
    sources: list[str] = None,
    dry_run: bool = False
):
    """
    Run the complete data pipeline.
    
    Args:
        sources: List of source keys to run (None = all)
        dry_run: If True, don't write output
    """
    print("=" * 60)
    print("CHARITY COMPLIANCE TRACKER - DATA REFRESH")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    STAGING_DIR.mkdir(exist_ok=True)
    REVIEW_DIR.mkdir(exist_ok=True)
    
    # Load existing data
    print("\nLoading existing records...")
    existing = load_existing_records()
    print(f"Found {len(existing)} existing records")
    
    # Determine which sources to run
    sources_to_run = sources if sources else list(SOURCES.keys())
    
    # Run each adapter
    all_new_records = []
    
    for source_key in sources_to_run:
        if source_key not in SOURCES:
            print(f"\nWARNING: Unknown source '{source_key}', skipping")
            continue
        
        print(f"\n{'='*40}")
        print(f"PROCESSING: {source_key.upper()}")
        print('='*40)
        
        try:
            adapter_class = SOURCES[source_key]
            adapter = adapter_class(STAGING_DIR)
            
            records = adapter.fetch_and_normalize()
            all_new_records.extend(records)
            
            print(f"✓ Retrieved {len(records)} records from {source_key}")
            
        except Exception as e:
            print(f"✗ Failed to process {source_key}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Merge all records
    print(f"\n{'='*40}")
    print("MERGING RECORDS")
    print('='*40)
    
    merged = merge_records(existing, all_new_records)
    
    print(f"\nTotal records after merge: {len(merged)}")
    print(f"  - New/updated: {len(all_new_records)}")
    print(f"  - Pre-existing: {len(existing)}")
    
    # Save results
    if dry_run:
        print("\n[DRY RUN] Would save to:", OUTPUT_FILE)
    else:
        save_records(merged, OUTPUT_FILE)
    
    # Summary by source
    print(f"\n{'='*40}")
    print("SUMMARY BY REGULATOR")
    print('='*40)
    
    by_regulator = {}
    for record in merged:
        reg = record.get('regulator', 'Unknown')
        by_regulator[reg] = by_regulator.get(reg, 0) + 1
    
    for reg, count in sorted(by_regulator.items()):
        print(f"  {reg}: {count}")
    
    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Charity Compliance Tracker Data Pipeline"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Don't write output files"
    )
    parser.add_argument(
        '--source',
        type=str,
        help=f"Run single source: {', '.join(SOURCES.keys())}"
    )
    
    args = parser.parse_args()
    
    sources = [args.source] if args.source else None
    run_pipeline(sources=sources, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
