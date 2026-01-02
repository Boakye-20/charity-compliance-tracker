#!/usr/bin/env python3
"""
Direct CSV file updater to fix dates in the Charity Compliance Tracker data.
This bypasses all adapters and directly corrects published_date and last_updated
in the CSV for records that have known good dates.

Run with:
    python fix_dates.py
"""

import csv
import os.path
from pathlib import Path

# Set up paths
ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = ROOT / "data"
CSV_FILE = DATA_DIR / "charity_policies.csv"

# Known good dates for specific records
FIXED_DATES = {
    # CC guidance pages with known publication dates from GOV.UK
    "CC_guidance_making-decisions-at-a-charity": "2018-05-01",
    "CC_guidance_managing-charity-finances": "2018-04-10",
    "CC_guidance_managing-conflicts-of-interest-in-a-charity": "2019-05-06",
    "CC_guidance_what-to-send-to-the-charity-commission-and-how-to-get-help": "2018-06-15",
    
    # CC inquiry cases with known publication dates from GOV.UK
    "CC_case_1100416_unknown": "2023-10-20",
    "CC_case_1142005_unknown": "2023-07-01",
    "CC_case_1117893_unknown": "2023-11-05",
    "CC_case_1127466_unknown": "2023-07-03",
    "CC_case_1136163_unknown": "2023-02-28",
    "CC_case_1122974_unknown": "2023-01-22",
    "CC_case_1159575_unknown": "2023-12-19",
    "CC_case_1164018_unknown": "2023-12-05",
    "CC_case_1189808_unknown": "2023-11-21",
    "CC_case_1143110_unknown": "2023-11-15",
    
    # Additional CC inquiry cases with placeholder dates - manually verified from GOV.UK
    "CC_case_1160575_unknown": "2024-10-24",  # Mermaids
    "CC_case_1058334_unknown": "2024-10-18",  # Keren Shmuel
    "CC_case_517381_unknown": "2024-10-17",   # Dar Ul Uloom Islamia Rizwia (Bralawai)
    "CC_case_1159995_unknown": "2024-09-26",  # Fashion for Relief
    "CC_case_1155658_unknown": "2024-09-05",  # Burke's Peerage Foundation
    "CC_case_1149924_unknown": "2024-09-05",  # The Mahfouz Foundation
    "CC_case_1152988_unknown": "2024-08-22",  # Salvation Proclaimers Ministries Limited
    "CC_case_1180264_unknown": "2024-07-19",  # Devon Freewheelers
    "CC_case_1026493_unknown": "2024-07-12",  # Ampleforth Abbey and St Laurence Educational Trust
    "CC_case_1111470_unknown": "2024-07-08",  # Citygate Christian Outreach Centre
    "CC_case_1149828_unknown": "2024-05-22",  # Effective Ventures Foundation UK
    "CC_case_1014419_unknown": "2024-05-14",  # Kogan Academy of Dramatic Arts
    "CC_case_1014813_unknown": "2024-04-25",  # Children Care Centre
    "CC_case_1026816_unknown": "2024-04-24",  # Islamic Education Centre and Mosque
    "CC_case_1026963_unknown": "2024-04-16",  # Jamia Hanfia Ghosia Mosque and Princess Street Resource Centre
    "CC_case_1098071_unknown": "2024-03-06",  # JAFLAS
    "CC_case_1176670_unknown": "2024-01-25",  # The Kingdom Church GB
    "CC_case_1175877_unknown": "2025-04-23",  # Education for Gondar (and related charities)
    
    # HSE guidance with known publication dates
    "HSE_guidance_protecting-volunteers-in-charity-shops-and-fundraising": "2021-06-15",
    "HSE_guidance_volunteering-how-to-manage-the-risks": "2021-03-22",
    "HSE_guidance_does-health-and-safety-legislation-apply-to-volunteers": "2020-09-18",
    "HSE_guidance_managing-risks-and-risk-assessment-at-work": "2022-01-13",
}

def patch_csv():
    """Read the CSV, update dates for known records, and write it back."""
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}")
        return
    
    # Read all records
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            records.append(row)
    
    # Update the dates
    updates = 0
    for record in records:
        record_id = record.get('id')
        if record_id in FIXED_DATES:
            record['published_date'] = FIXED_DATES[record_id]
            record['last_updated'] = FIXED_DATES[record_id]
            updates += 1
            print(f"Updated {record_id} to {FIXED_DATES[record_id]}")
    
    # Write back to CSV
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"\nDone! Updated {updates} records with correct dates.")

if __name__ == "__main__":
    patch_csv()
