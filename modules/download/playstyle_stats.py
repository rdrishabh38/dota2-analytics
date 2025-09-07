# modules/download/playstyle_stats.py

import requests
import json
import os
import time
import shutil
from typing import Dict, Any
from modules.common import path_manager

BASE_URL_TEMPLATE = "https://steamcommunity.com/id/{custom_url}/gcpd/570"

def fetch(session: requests.Session, profile: Dict[str, Any]):
    """
    Downloads all playstyle stats data for a given profile by looping through the API.
    """
    profile_name = profile['profile_name']
    custom_url = profile['custom_url']
    session_id = profile['cookies'].get('sessionid')
    
    print(f"\n📥 Downloading Playstyle Stats for '{profile_name}'...")

    data_dir = path_manager.get_raw_playstyle_stats_dir(profile_name)
    
    # Clean up old data before fetching new data
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    
    continue_token = None
    page_count = 0
    
    while True:
        page_count += 1
        params = {
            "ajax": 1,
            "tab": "PlayerPlaystyleStats",
            "sessionid": session_id
        }
        if continue_token:
            params["continue_token"] = continue_token

        try:
            time.sleep(1) # Be respectful to the API
            response = session.get(BASE_URL_TEMPLATE.format(custom_url=custom_url), params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data or not data.get("success") or not data.get("html", "").strip():
                print("🏁 No more data from the API.")
                break
            
            print(f"   > Fetched page {page_count}...")
            
            new_continue_token = data.get("continue_token")
            
            # Save the file using the token as a unique name
            filename = f"{new_continue_token or 'final_page'}.json"
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            if not new_continue_token:
                print("🏁 Reached the last page.")
                break
                
            continue_token = new_continue_token

        except requests.exceptions.RequestException as e:
            print(f"❌ FATAL: Failed during download. Error: {e}")
            raise
            
    print(f"✅ Success! Saved {page_count} file(s) for Playstyle Stats.")
