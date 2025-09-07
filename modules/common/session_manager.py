# modules/common/session_manager.py

import requests
from typing import Dict, Any

def create_session(profile: Dict[str, Any]) -> requests.Session:
    """Creates and configures a requests session with user cookies."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    })
    session.cookies.update(profile["cookies"])
    return session
