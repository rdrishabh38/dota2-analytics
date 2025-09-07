# modules/process/conduct_summary.py

import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Import from our new common modules
from modules.common import path_manager

# --- Helper function (previously a method) ---

def _parse_html_table(html_content: str) -> List[List[str]]:
    """Parses the HTML table from a raw JSON file's content."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_="generic_kv_table")
        if not table:
            return []
        # Extract text from each cell in each row, skipping the header row
        data_rows = [[ele.text.strip() for ele in row.find_all('td')] for row in table.find_all("tr")[1:]]
        return data_rows
    except Exception as e:
        print(f"⚠️ Warning: Could not parse HTML. Error: {e}")
        return []

# --- Main public function ---

def process(profile_name: str) -> pd.DataFrame | None:
    """
    Processes all raw conduct summary JSONs for a profile into a clean DataFrame.
    Saves the result to a CSV file.
    """
    print(f"\n✨ Processing Conduct Summary data for '{profile_name}'...")
    
    # Get paths from our centralized path manager
    raw_data_dir = path_manager.get_raw_conduct_summary_dir(profile_name)
    processed_dir = path_manager.get_processed_dir(profile_name)
    output_csv_path = path_manager.get_processed_conduct_summary_path(profile_name)
    
    # Ensure the output directory exists
    os.makedirs(processed_dir, exist_ok=True)
    
    column_names = [
        'MatchID', 'SummaryDate', 'Periodic', 'ExcessiveReports', 'ExcessiveAbandons',
        'MatchCount', 'PositiveMatches', 'ReportedMatches', 'AbandonedMatches', 'Reports',
        'ReportingParties', 'CommsReports', 'CommsReportingParties', 'Commends', 'BehaviorScore'
    ]

    if not os.path.exists(raw_data_dir):
        print(f"❌ Directory not found: '{raw_data_dir}'. Please run the downloader first.")
        return None

    json_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
    if not json_files:
        print("❌ No raw data files found to process.")
        return None
        
    print(f"   > Found {len(json_files)} files to process.")
    
    all_records = []
    for file_name in json_files:
        file_path = os.path.join(raw_data_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("html"):
                all_records.extend(_parse_html_table(data["html"]))
        except Exception as e:
            print(f"⚠️ Warning: Could not process file '{file_name}'. Error: {e}")
    
    if not all_records:
        print("❌ No records were extracted from the raw files.")
        return None

    print(f"\n🔧 Processing a total of {len(all_records)} records...")
    df = pd.DataFrame(all_records, columns=column_names)

    print("   > Cleaning data and converting types...")
    df['SummaryDate'] = pd.to_datetime(df['SummaryDate'].str.replace(' GMT', ''), errors='coerce')
    
    bool_cols = ['Periodic', 'ExcessiveReports', 'ExcessiveAbandons']
    for col in bool_cols:
        df[col] = df[col].apply(lambda x: True if x == 'Yes' else False).astype(bool)
    
    numeric_cols = [c for c in column_names if c not in ['SummaryDate'] + bool_cols]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print("   > Finalizing data structure...")
    df.dropna(subset=['MatchID', 'SummaryDate'], inplace=True)
    df.drop_duplicates(subset=['MatchID'], keep='first', inplace=True)
    df.sort_values(by='SummaryDate', ascending=False, inplace=True)
    
    # Convert numeric columns to integer type, handling potential NaNs
    df[numeric_cols] = df[numeric_cols].astype('Int64')
    
    try:
        df.to_csv(output_csv_path, index=False)
        print(f"\n✅ Success! Clean data saved to:\n   {output_csv_path}")
        return df
    except IOError as e:
        print(f"❌ FATAL: Could not save the final CSV file. Error: {e}")
        return None
