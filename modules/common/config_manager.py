# modules/common/config_manager.py

import json
import os
from typing import Dict, Any

CONFIG_PATH = "config.json"


def initialize_config():
    """Creates a default config file if one doesn't exist."""
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "active_profile": "",
            "profiles": [],
            "max_retries": 5,
            "initial_backoff_seconds": 5
        }
        save_config(default_config)


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Loads the main JSON configuration file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"FATAL: Config file '{config_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"FATAL: Could not decode JSON from '{config_path}'.")


def save_config(config_data: Dict[str, Any]):
    """Saves the configuration data to the file."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config_data, f, indent=2)


def get_active_profile(config: Dict[str, Any]) -> Dict[str, Any]:
    """Finds and returns the active profile dictionary from the config."""
    active_profile_name = config.get("active_profile")
    if not active_profile_name:
        raise ValueError("FATAL: 'active_profile' not found in config.json.")

    for profile in config.get("profiles", []):
        if profile.get("profile_name") == active_profile_name:
            if "YOUR_CUSTOM_URL" in profile.get("custom_url", ""):
                raise ValueError(f"FATAL: Update 'custom_url' for profile '{active_profile_name}'.")
            return profile
            
    raise ValueError(f"FATAL: Active profile '{active_profile_name}' not found.")
