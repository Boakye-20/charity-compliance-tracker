#!/usr/bin/env python3
"""
Remove duplicate records from charity_policies.csv.
Keeps the record with the most accurate date for each unique source_url.
"""

import csv
from pathlib import Path
from datetime import datetime

# Set up paths
ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = ROOT / "data"
CSV_FILE = DATA_DIR / "charity_policies.csv"

def remove_duplicates():
    """Read CSV, remove duplicates by source_url, keeping best date."""
    
    # Read all records
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            records.append(row)
    
    print(f"Total records before deduplication: {len(records)}")
    
    # Group by source_url
    url_groups = {}
    for record in records:
        url = record.get('source_url', '')
        if url not in url_groups:
            url_groups[url] = []
        url_groups[url].append(record)
    
    # For each URL group, keep the best record
    deduplicated = []
    removed_count = 0
    
    for url, group in url_groups.items():
        if len(group) == 1:
            # No duplicates
            deduplicated.append(group[0])
        else:
            # Multiple records for same URL - pick the best one
            # Prefer records with dates that aren't 2025-01-01 or 2025-12-31
            # Then prefer earlier dates (more likely to be correct)
            
            best = None
            for record in group:
                pub_date = record.get('published_date', '')
                
                # Skip obvious bad dates
                if pub_date in ['2025-01-01', '2025-12-31', '1970-01-01']:
                    continue
                
                if best is None:
                    best = record
                else:
                    # Compare dates - prefer the one that's not a placeholder
                    best_date = best.get('published_date', '')
                    if best_date in ['2025-01-01', '2025-12-31', '1970-01-01']:
                        best = record
            
            # If all records have bad dates, just take the first one
            if best is None:
                best = group[0]
            
            deduplicated.append(best)
            removed_count += len(group) - 1
            
            if len(group) > 1:
                print(f"Removed {len(group) - 1} duplicate(s) for: {record.get('title', 'Unknown')[:60]}")
    
    print(f"\nTotal records after deduplication: {len(deduplicated)}")
    print(f"Removed {removed_count} duplicate records")
    
    # Write back to CSV
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduplicated)
    
    print(f"\nDone! CSV updated at {CSV_FILE}")

if __name__ == "__main__":
    remove_duplicates()
