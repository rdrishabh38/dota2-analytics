# Dota 2 Analytics Hub
# A personal desktop dashboard to download, analyze, and visualize your Dota 2 metadata.
# Copyright (C) 2025 Kocha rdrishabh38@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import json
import os
import sys
import pandas as pd
from bs4 import BeautifulSoup

class Processor:
    """
    Handles the processing of various raw data types into clean, structured files.
    Each data type will have its own dedicated processing method.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initializes the processor by loading configuration for the active profile."""
        print("---  Dota 2 Analytics Processor ---")
        self.config = self._load_config(config_path)
        
        self.active_profile = self._get_active_profile()
        if not self.active_profile:
            sys.exit(1)

        self.profile_name = self.active_profile["profile_name"]
        self.profile_dir = os.path.join("data", self.profile_name)
        
        print(f"✅ Initialized successfully for profile: '{self.profile_name}'")

    # region Helper Methods
    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as f: return json.load(f)
        except FileNotFoundError: print(f"❌ FATAL: Config file '{config_path}' not found."); sys.exit(1)
        except json.JSONDecodeError: print(f"❌ FATAL: Could not decode JSON from '{config_path}'."); sys.exit(1)
            
    def _get_active_profile(self) -> dict | None:
        active_profile_name = self.config.get("active_profile")
        if not active_profile_name: print("❌ FATAL: 'active_profile' key not found in config.json."); return None
        for profile in self.config.get("profiles", []):
            if profile.get("profile_name") == active_profile_name: return profile
        print(f"❌ FATAL: Active profile '{active_profile_name}' not found."); return None

    def _parse_html_table(self, html_content: str) -> list[list[str]]:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            table = soup.find("table", class_="generic_kv_table")
            if not table: return []
            data_rows = [[ele.text.strip() for ele in row.find_all('td')] for row in table.find_all("tr")[1:]]
            return data_rows
        except Exception as e:
            print(f"⚠️ Warning: Could not parse HTML. Error: {e}"); return []
    # endregion

    def process_conduct_summary(self):
        """Processes raw conduct summary data and saves it to a CSV file."""
        print("\n✨ Processing Conduct Summary data...")
        
        # Define paths specific to this data type
        raw_data_dir = os.path.join(self.profile_dir, "raw_conduct_summary")
        output_csv_path = os.path.join(self.profile_dir, "conduct_summary.csv")
        column_names = [
            'MatchID', 'SummaryDate', 'Periodic', 'ExcessiveReports', 'ExcessiveAbandons',
            'MatchCount', 'PositiveMatches', 'ReportedMatches', 'AbandonedMatches', 'Reports',
            'ReportingParties', 'CommsReports', 'CommsReportingParties', 'Commends', 'BehaviorScore'
        ]

        if not os.path.exists(raw_data_dir):
            print(f"❌ Directory not found: '{raw_data_dir}'. Please run the downloader first."); return

        json_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
        if not json_files: print("❌ No raw data files found to process."); return
            
        print(f"  > Found {len(json_files)} files to process.")
        
        all_records = []
        for file_name in json_files:
            file_path = os.path.join(raw_data_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
                if data.get("html"): all_records.extend(self._parse_html_table(data["html"]))
            except Exception as e: print(f"⚠️ Warning: Could not process file '{file_name}'. Error: {e}")
        
        if not all_records: print("❌ No records were extracted."); return

        print(f"\n🔧 Processing a total of {len(all_records)} records...")
        df = pd.DataFrame(all_records, columns=column_names)

        print("  > Cleaning data and converting types...")
        df['SummaryDate'] = pd.to_datetime(df['SummaryDate'].str.replace(' GMT', ''), errors='coerce')
        for col in ['Periodic', 'ExcessiveReports', 'ExcessiveAbandons']:
            df[col] = df[col].apply(lambda x: True if x == 'Yes' else False)
        numeric_cols = [c for c in column_names if c not in ['SummaryDate', 'Periodic', 'ExcessiveReports', 'ExcessiveAbandons']]
        for col in numeric_cols: df[col] = pd.to_numeric(df[col], errors='coerce')

        print("  > Finalizing data structure...")
        df.dropna(subset=['MatchID', 'SummaryDate'], inplace=True)
        df.drop_duplicates(subset=['MatchID'], keep='first', inplace=True)
        df.sort_values(by='SummaryDate', ascending=False, inplace=True)
        df[numeric_cols] = df[numeric_cols].astype(int)
        
        try:
            df.to_csv(output_csv_path, index=False)
            print(f"\n✅ Success! Clean Conduct Summary data saved to:\n{output_csv_path}")
        except Exception as e:
            print(f"❌ FATAL: Could not save the final CSV file. Error: {e}")


if __name__ == "__main__":
    # This block only runs when you execute the script directly
    processor = Processor()
    processor.process_conduct_summary()
    print("\n--- Processing phase finished ---")
