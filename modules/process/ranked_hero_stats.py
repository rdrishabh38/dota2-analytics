# modules/process/ranked_stats.py

import os
import pandas as pd
from bs4 import BeautifulSoup
from modules.common import path_manager

def process(profile_name: str) -> pd.DataFrame | None:
    """
    Parses the raw ranked stats HTML file into a clean DataFrame and saves it to a CSV.
    """
    print(f"\n⚙️ Processing Ranked Hero Stats for '{profile_name}'...")

    raw_html_path = path_manager.get_raw_ranked_stats_path(profile_name)
    output_csv_path = path_manager.get_processed_ranked_stats_path(profile_name)

    if not os.path.exists(raw_html_path):
        print(f"❌ File not found: '{raw_html_path}'. Please run the downloader first.")
        return None

    with open(raw_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    hero_table = soup.find('table', class_='generic_kv_table')

    if not hero_table:
        print("❌ Could not find the hero stats table in the HTML file.")
        return None

    # --- Extract Headers ---
    header_row = hero_table.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]

    # --- Extract Data Rows ---
    data_rows = []
    for row in hero_table.find_all('tr')[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(cells) == len(headers):  # Ensure row is not malformed
            data_rows.append(dict(zip(headers, cells)))

    if not data_rows:
        print("❌ No data rows were extracted from the table.")
        return None
        
    df = pd.DataFrame(data_rows)
    
    # Clean up a known bad row if it exists
    df = df[df['Hero'] != '-127']

    # Convert all columns except 'Hero' to numeric types
    for col in df.columns:
        if col != 'Hero':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add a Win Rate column for better analysis
    df['WinRate'] = (df['Wins'] / (df['Wins'] + df['Losses']) * 100).fillna(0)
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    
    print(f"✅ Success! Processed data saved to:\n   {output_csv_path}")
    return df
