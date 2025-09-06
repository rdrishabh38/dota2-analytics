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


import requests
import json
import os
import time
import sys
from bs4 import BeautifulSoup

class Downloader:
    """
    Handles the downloading of various data types from a user's Steam profile.
    Each data type will have its own dedicated download method.
    """
    BASE_URL_TEMPLATE = "https://steamcommunity.com/id/{custom_url}/gcpd/570"

    def __init__(self, config_path: str = "config.json"):
        """Initializes the downloader by loading configuration for the active profile."""
        print("---  Dota 2 Analytics Downloader ---")
        self.config = self._load_config(config_path)
        
        self.active_profile = self._get_active_profile()
        if not self.active_profile:
            sys.exit(1)

        self.profile_name = self.active_profile["profile_name"]
        self.custom_url = self.active_profile["custom_url"]
        self.cookies = self.active_profile["cookies"]
        
        # Define profile-specific paths
        self.profile_dir = os.path.join("data", self.profile_name)
        
        self.session = self._create_session()
        print(f"✅ Initialized successfully for profile: '{self.profile_name}'")

    # ... (Keep all the helper methods like _load_state, _save_state, _fetch_batch, etc. exactly as they were) ...
    # region State Management and Helpers
    def _load_state(self, state_file: str) -> str | None:
        if not os.path.exists(state_file): return None
        try:
            with open(state_file, 'r') as f: return json.load(f).get("next_continue_token")
        except (IOError, json.JSONDecodeError): return None

    def _save_state(self, state_file: str, token: str):
        with open(state_file, 'w') as f: json.dump({"next_continue_token": token}, f)

    def _clear_state(self, state_file: str):
        if os.path.exists(state_file): os.remove(state_file)

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as f: return json.load(f)
        except FileNotFoundError: print(f"❌ FATAL: Config file '{config_path}' not found."); sys.exit(1)
        except json.JSONDecodeError: print(f"❌ FATAL: Could not decode JSON from '{config_path}'."); sys.exit(1)

    def _get_active_profile(self) -> dict | None:
        active_profile_name = self.config.get("active_profile")
        if not active_profile_name: print("❌ FATAL: 'active_profile' not found in config.json."); return None
        for profile in self.config.get("profiles", []):
            if profile.get("profile_name") == active_profile_name:
                if "YOUR_CUSTOM_URL" in profile.get("custom_url", ""): print(f"❌ FATAL: Update 'custom_url' for profile '{active_profile_name}'."); return None
                return profile
        print(f"❌ FATAL: Active profile '{active_profile_name}' not found."); return None

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
        session.cookies.update(self.cookies)
        return session
        
    def _fetch_batch(self, continue_token: str = None) -> dict | None:
        base_url = self.BASE_URL_TEMPLATE.format(custom_url=self.custom_url)
        params = {"ajax": 1, "tab": "MatchPlayerReportIncoming", "sessionid": self.cookies.get("sessionid")}
        if continue_token: params["continue_token"] = continue_token
        retries, backoff = self.config.get("max_retries", 5), self.config.get("initial_backoff_seconds", 5)
        for i in range(retries):
            try:
                time.sleep(2)
                response = self.session.get(base_url, params=params, timeout=30)
                if response.status_code == 200: return response.json()
                if response.status_code in [401, 403]: print("❌ FATAL: Authentication failed (401/403)."); return None
                print(f"⚠️ Warning: Received status {response.status_code}. Retrying...")
            except requests.exceptions.RequestException as e: print(f"⚠️ An error occurred: {e}. Retrying...")
            time.sleep(backoff * (2 ** i))
        print(f"❌ FATAL: Failed to fetch data after {retries} retries."); return None

    def _get_latest_local_match_id(self, data_dir) -> str | None:
        files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.json')]
        if not files: return None
        latest_file = max(files, key=os.path.getctime)
        try:
            with open(latest_file, 'r', encoding='utf-8') as f: data = json.load(f)
            soup = BeautifulSoup(data.get("html", ""), "html.parser")
            first_row = soup.find("table").find("tr").find_next_sibling("tr")
            return first_row.find("td").text.strip() if first_row else None
        except Exception as e: print(f"⚠️ Could not read last MatchID: {e}"); return None
    # endregion
    
    def download_conduct_summary(self):
        """
        Main method to run the download process for Conduct Summary data.
        This unified loop handles all cases: historical, incremental, and resumed downloads.
        """
        # Setup paths specific to this data type
        data_dir = os.path.join(self.profile_dir, "raw_conduct_summary")
        state_file = os.path.join(self.profile_dir, "conduct_summary_state.json")
        os.makedirs(data_dir, exist_ok=True)

        is_sync_mode = bool(os.listdir(data_dir))
        stop_at_match_id = self._get_latest_local_match_id(data_dir) if is_sync_mode else None

        if is_sync_mode: print(f"\n🔄 Syncing Conduct Summary. Will stop if MatchID '{stop_at_match_id}' is found.")
        else: print("\n🚀 Downloading historical Conduct Summary.")

        continue_token = self._load_state(state_file)
        if continue_token: print(f"   > Resuming download from a previous session.")

        page_count, new_files_count = 0, 0
        while True:
            data = self._fetch_batch(continue_token)

            if not data or not data.get("success") or not data.get("html", "").strip():
                print("\n🏁 Reached the end of the data from the API.")
                break

            page_count += 1
            print(f"  > Fetched page {page_count} (up to 20 records)...")

            if is_sync_mode and stop_at_match_id:
                soup = BeautifulSoup(data.get("html", ""), "html.parser")
                match_ids_on_page = {row.find("td").text.strip() for row in soup.find("table").find_all("tr")[1:]}
                if stop_at_match_id in match_ids_on_page:
                    print("   > Found last known MatchID. Sync is complete.")
                    break

            new_continue_token = data.get("continue_token")
            if not new_continue_token:
                print("\n🏁 No more continue_token found. Download complete.")
                break

            filepath = os.path.join(data_dir, f"{new_continue_token}.json")
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
            
            self._save_state(state_file, new_continue_token)
            continue_token = new_continue_token
            new_files_count += 1
        
        self._clear_state(state_file)
        
        if new_files_count > 0: print(f"\n✅ Success! Saved {new_files_count} new Conduct Summary files.")
        else: print("\n✅ Conduct Summary is already up to date.")


if __name__ == "__main__":
    # This block only runs when you execute the script directly
    # A UI button would import the Downloader class and call the specific method it needs
    downloader = Downloader()
    downloader.download_conduct_summary()
    print("\n--- Download phase finished ---")
