#!/usr/bin/env python3
"""
Enrich charity_policies.csv with data from the Charity Commission Register API.

Adds fields:
- cc_registered_number: Official charity number
- cc_suffix: Charity suffix (usually 0)
- cc_status: Registration status (Registered, Removed, etc.)
- cc_latest_income: Most recent annual income
- cc_governing_document: Type of governing document
- cc_primary_region: Primary area of operation

API docs: https://register-of-charities.charitycommission.gov.uk/en/documentation-on-the-api
"""

import csv
import os
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import requests

# API configuration
API_BASE = "https://api.charitycommission.gov.uk/register/api"
API_KEY = os.environ.get("CHARITY_COMMISSION_API_KEY", "dd4b5c3b569045b9b43d0c577d6c54f3")

HEADERS = {
    "Ocp-Apim-Subscription-Key": API_KEY,
    "Accept": "application/json"
}

# Paths
ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = ROOT / "data"
CSV_FILE = DATA_DIR / "charity_policies.csv"
OUTPUT_FILE = DATA_DIR / "charity_policies_enriched.csv"

# Rate limiting
REQUEST_DELAY = 0.5  # seconds between API calls


def find_charity_by_name(name: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Search for a charity by name using the Register API.
    Returns (registered_number, suffix) or (None, None) if not found.
    """
    if not name:
        return None, None
    
    # Clean the name for search
    search_name = name.strip()
    
    try:
        url = f"{API_BASE}/searchCharityName"
        params = {"name": search_name}
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        
        if results and len(results) > 0:
            # Take the first result (best match)
            first = results[0]
            reg_no = str(first.get("registeredCharityNumber", ""))
            suffix = first.get("subsidiaryNumber", 0)
            return reg_no, suffix
        
    except Exception as e:
        print(f"  Warning: Failed to search for '{name}': {e}")
    
    return None, None


def get_charity_overview(reg_no: str, suffix: int = 0) -> Optional[Dict[str, Any]]:
    """
    Get charity overview data from the Register API.
    Returns dict with status, income, governance info, or None if failed.
    """
    if not reg_no:
        return None
    
    try:
        url = f"{API_BASE}/charityoverview/{reg_no}/{suffix}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except Exception as e:
        print(f"  Warning: Failed to get overview for {reg_no}/{suffix}: {e}")
        return None


def get_charity_governance(reg_no: str, suffix: int = 0) -> Optional[Dict[str, Any]]:
    """
    Get charity governance information from the Register API.
    Returns dict with governing document info, or None if failed.
    """
    if not reg_no:
        return None
    
    try:
        url = f"{API_BASE}/charitygovernanceinformation/{reg_no}/{suffix}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except Exception as e:
        print(f"  Warning: Failed to get governance for {reg_no}/{suffix}: {e}")
        return None


def get_charity_area_of_operation(reg_no: str, suffix: int = 0) -> Optional[Dict[str, Any]]:
    """
    Get charity area of operation from the Register API.
    Returns dict with geographic info, or None if failed.
    """
    if not reg_no:
        return None
    
    try:
        url = f"{API_BASE}/charityareaofoperation/{reg_no}/{suffix}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except Exception as e:
        print(f"  Warning: Failed to get area of operation for {reg_no}/{suffix}: {e}")
        return None


def extract_enrichment_fields(overview: Optional[Dict], governance: Optional[Dict], 
                              area: Optional[Dict]) -> Dict[str, str]:
    """
    Extract the fields we want to add to the CSV from API responses.
    """
    fields = {
        "cc_status": "",
        "cc_latest_income": "",
        "cc_governing_document": "",
        "cc_primary_region": "",
    }
    
    if overview:
        # Status - need to get from separate endpoint
        # For now, leave empty as overview doesn't have registration status
        
        # Latest income
        latest_income = overview.get("latest_income")
        if latest_income is not None:
            fields["cc_latest_income"] = str(latest_income)
    
    if governance:
        # Governing document
        gov_doc = governance.get("governing_document", "")
        fields["cc_governing_document"] = gov_doc
    
    if area and isinstance(area, list) and len(area) > 0:
        # Primary region (first in list)
        first_area = area[0]
        fields["cc_primary_region"] = first_area.get("area_of_operation", "")
    
    return fields


def enrich_csv():
    """
    Read the CSV, enrich each record with Register API data, and write to new file.
    """
    if not CSV_FILE.exists():
        print(f"Error: CSV file not found at {CSV_FILE}")
        return
    
    print(f"Reading from: {CSV_FILE}")
    print(f"Writing to: {OUTPUT_FILE}")
    print(f"Using API key: {API_KEY[:10]}...")
    print()
    
    # Read all records
    with CSV_FILE.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        records = list(reader)
    
    # Add new fields to schema
    new_fields = [
        "cc_registered_number",
        "cc_suffix",
        "cc_status",
        "cc_latest_income",
        "cc_governing_document",
        "cc_primary_region",
    ]
    
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    # Cache to avoid repeated API calls for same charity
    cache: Dict[Tuple[str, int], Dict[str, str]] = {}
    
    enriched_count = 0
    skipped_count = 0
    
    # Process each record
    for i, row in enumerate(records, 1):
        print(f"[{i}/{len(records)}] Processing: {row.get('title', 'Unknown')[:60]}...")
        
        charity_name = row.get('charity_name', '').strip()
        charity_number = row.get('charity_number', '').strip()
        
        # Skip if not a charity case/inquiry
        if not charity_name and not charity_number:
            print("  → Skipping (no charity info)")
            skipped_count += 1
            continue
        
        # Determine charity number
        reg_no = charity_number
        suffix = 0
        
        # If we don't have a number, search by name
        if not reg_no and charity_name:
            print(f"  → Searching for charity by name: {charity_name}")
            reg_no, suffix = find_charity_by_name(charity_name)
            time.sleep(REQUEST_DELAY)
            
            if not reg_no:
                print("  → Not found in register")
                skipped_count += 1
                continue
        
        # Check cache
        cache_key = (reg_no, suffix)
        if cache_key in cache:
            print(f"  → Using cached data for {reg_no}/{suffix}")
            enrichment = cache[cache_key]
        else:
            # Fetch from API
            print(f"  → Fetching data for charity {reg_no}/{suffix}")
            
            overview = get_charity_overview(reg_no, suffix)
            time.sleep(REQUEST_DELAY)
            
            governance = get_charity_governance(reg_no, suffix)
            time.sleep(REQUEST_DELAY)
            
            area = get_charity_area_of_operation(reg_no, suffix)
            time.sleep(REQUEST_DELAY)
            
            enrichment = extract_enrichment_fields(overview, governance, area)
            enrichment["cc_registered_number"] = reg_no
            enrichment["cc_suffix"] = str(suffix)
            
            cache[cache_key] = enrichment
            
            print(f"  → Status: {enrichment['cc_status']}, Income: £{enrichment['cc_latest_income']}")
        
        # Update row
        row.update(enrichment)
        enriched_count += 1
    
    # Write enriched CSV
    with OUTPUT_FILE.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print()
    print("=" * 60)
    print(f"Done! Enriched {enriched_count} records, skipped {skipped_count}")
    print(f"Output written to: {OUTPUT_FILE}")
    print()
    print("Next steps:")
    print(f"  1. Review the enriched file: {OUTPUT_FILE}")
    print(f"  2. If satisfied, replace the original:")
    print(f"     mv {OUTPUT_FILE} {CSV_FILE}")


if __name__ == "__main__":
    enrich_csv()
