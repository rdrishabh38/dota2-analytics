# modules/download/ranked_hero_stats.py

import requests
import os
from typing import Dict, Any
from modules.common import path_manager

BASE_URL_TEMPLATE = "https://steamcommunity.com/id/{custom_url}/gcpd/570/?category=Stats&tab=GameHeroStandings"

def fetch(session: requests.Session, profile: Dict[str, Any]):
    """
    Downloads the Ranked Hero Standings page for a given profile.
    """
    profile_name = profile['profile_name']
    custom_url = profile['custom_url']
    
    print(f"\n📥 Downloading Ranked Hero Stats for '{profile_name}'...")

    url = BASE_URL_TEMPLATE.format(custom_url=custom_url)
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get the path and ensure the directory exists
        output_path = path_manager.get_raw_ranked_stats_path(profile_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the HTML content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"✅ Success! Raw HTML saved to:\n   {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"❌ FATAL: Failed to download ranked stats page. Error: {e}")
        # Raise the exception so the UI can catch it and display an error
        raise
