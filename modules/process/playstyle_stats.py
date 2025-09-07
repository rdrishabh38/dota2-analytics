# modules/process/playstyle_stats.py

import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from modules.common import path_manager

def process(profile_name: str) -> pd.DataFrame | None:
    """
    Processes all raw playstyle JSONs into a clean DataFrame and saves to a CSV.
    """
    print(f"\n⚙️ Processing Playstyle Stats for '{profile_name}'...")

    raw_data_dir = path_manager.get_raw_playstyle_stats_dir(profile_name)
    output_csv_path = path_manager.get_processed_playstyle_stats_path(profile_name)

    if not os.path.exists(raw_data_dir):
        print(f"❌ Directory not found: '{raw_data_dir}'. Please run the downloader first.")
        return None

    all_records = []
    for file_name in os.listdir(raw_data_dir):
        if file_name.endswith('.json'):
            file_path = os.path.join(raw_data_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            html_content = data.get("html", "")
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                table = soup.find("table", class_="generic_kv_table")
                if not table: continue
                
                # Extract rows, skipping the header
                for row in table.find_all("tr")[1:]:
                    cells = [ele.text.strip() for ele in row.find_all('td')]
                    all_records.append(cells)
    
    if not all_records:
        print("❌ No records were extracted from the raw files.")
        return None

    # Define column headers based on the API response
    headers = [
        'MatchID', 'Timestamp', 'Hero', 'FightScore', 'FarmScore', 'PushScore',
        'Versatility', 'Kills', 'Deaths', 'Assists', 'LastHits', 'Denies',
        'GPM', 'XPPM', 'NetWorth', 'Damage', 'Heals'
    ]
    
    df = pd.DataFrame(all_records, columns=headers)
    
    # Clean and convert data types
    df['Timestamp'] = pd.to_datetime(df['Timestamp'].str.replace(' GMT', ''), errors='coerce')
    numeric_cols = [col for col in headers if col not in ['Timestamp', 'Hero']]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.sort_values(by='Timestamp', ascending=False, inplace=True)
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    
    print(f"✅ Success! Processed playstyle data saved to:\n   {output_csv_path}")
    return df
