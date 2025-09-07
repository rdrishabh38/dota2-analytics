# modules/download/conduct_summary.py

import requests
import json
import os
import time
from bs4 import BeautifulSoup
from typing import Dict, Any

# Import from our new common modules
from modules.common import path_manager

# --- Helper functions (previously methods of the Downloader class) ---

BASE_URL_TEMPLATE = "https://steamcommunity.com/id/{custom_url}/gcpd/570"

def _load_state(state_file: str) -> str | None:
    if not os.path.exists(state_file): return None
    try:
        with open(state_file, 'r') as f: return json.load(f).get("next_continue_token")
    except (IOError, json.JSONDecodeError): return None

def _save_state(state_file: str, token: str):
    with open(state_file, 'w') as f: json.dump({"next_continue_token": token}, f)

def _clear_state(state_file: str):
    if os.path.exists(state_file): os.remove(state_file)

def _get_latest_local_match_id(data_dir: str) -> str | None:
    if not os.path.exists(data_dir) or not os.listdir(data_dir): return None
    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.json')]
    if not files: return None
    latest_file = max(files, key=os.path.getctime)
    try:
        with open(latest_file, 'r', encoding='utf-8') as f: data = json.load(f)
        soup = BeautifulSoup(data.get("html", ""), "html.parser")
        first_row = soup.find("table").find("tr").find_next_sibling("tr")
        return first_row.find("td").text.strip() if first_row else None
    except Exception as e:
        print(f"⚠️ Could not read last MatchID from '{latest_file}': {e}")
        return None

def _fetch_batch(session: requests.Session, custom_url: str, session_id: str, config: Dict[str, Any], continue_token: str = None) -> Dict | None:
    base_url = BASE_URL_TEMPLATE.format(custom_url=custom_url)
    params = {"ajax": 1, "tab": "MatchPlayerReportIncoming", "sessionid": session_id}
    if continue_token: params["continue_token"] = continue_token
    
    retries, backoff = config.get("max_retries", 5), config.get("initial_backoff_seconds", 5)
    
    for i in range(retries):
        try:
            time.sleep(2) # Be respectful to the API
            response = session.get(base_url, params=params, timeout=30)
            if response.status_code == 200: return response.json()
            if response.status_code in [401, 403]: print("❌ FATAL: Authentication failed (401/403). Check cookies."); return None
            print(f"⚠️ Warning: Received status {response.status_code}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ An error occurred: {e}. Retrying...")
        time.sleep(backoff * (2 ** i))
        
    print(f"❌ FATAL: Failed to fetch data after {retries} retries.")
    return None

# --- Main public function ---

def fetch(session: requests.Session, profile: Dict[str, Any], config: Dict[str, Any]):
    """
    Downloads all conduct summary data for a given profile.
    Handles historical, incremental, and resumed downloads.
    """
    profile_name = profile['profile_name']
    custom_url = profile['custom_url']
    session_id = profile['cookies'].get('sessionid')

    # Get paths from our path manager
    data_dir = path_manager.get_raw_conduct_summary_dir(profile_name)
    state_file = path_manager.get_conduct_summary_state_path(profile_name)
    os.makedirs(data_dir, exist_ok=True)

    is_sync_mode = bool(os.listdir(data_dir))
    stop_at_match_id = _get_latest_local_match_id(data_dir) if is_sync_mode else None

    if is_sync_mode: print(f"\n🔄 Syncing Conduct Summary for '{profile_name}'. Will stop if MatchID '{stop_at_match_id}' is found.")
    else: print(f"\n🚀 Downloading historical Conduct Summary for '{profile_name}'.")

    continue_token = _load_state(state_file)
    if continue_token: print(f"   > Resuming download from a previous session.")

    page_count, new_files_count = 0, 0
    while True:
        data = _fetch_batch(session, custom_url, session_id, config, continue_token)

        if not data or not data.get("success") or not data.get("html", "").strip():
            print("\n🏁 Reached the end of the data from the API.")
            break

        page_count += 1
        print(f"   > Fetched page {page_count}...")

        if is_sync_mode and stop_at_match_id:
            soup = BeautifulSoup(data.get("html", ""), "html.parser")
            rows = soup.find("table").find_all("tr")[1:]
            match_ids_on_page = {row.find("td").text.strip() for row in rows}
            if stop_at_match_id in match_ids_on_page:
                print("   > Found last known MatchID. Sync is complete.")
                break

        new_continue_token = data.get("continue_token")
        filepath = os.path.join(data_dir, f"{new_continue_token or 'final_page'}.json")
        with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
        
        new_files_count += 1
        
        if not new_continue_token:
            print("\n🏁 No more continue_token found. Download complete.")
            break

        _save_state(state_file, new_continue_token)
        continue_token = new_continue_token

    _clear_state(state_file)
    
    if new_files_count > 0: print(f"\n✅ Success! Saved {new_files_count} new Conduct Summary file(s) for '{profile_name}'.")
    else: print(f"\n✅ Conduct Summary for '{profile_name}' is already up to date.")
