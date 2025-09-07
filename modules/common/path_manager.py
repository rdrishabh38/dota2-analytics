# modules/common/path_manager.py

import os
import shutil

BASE_DATA_DIR = "data"


def get_profile_dir(profile_name: str) -> str:
    """Returns the main directory path for a given profile."""
    return os.path.join(BASE_DATA_DIR, profile_name)


def get_raw_conduct_summary_dir(profile_name: str) -> str:
    """Returns the path for raw conduct summary JSONs."""
    return os.path.join(get_profile_dir(profile_name), "raw_conduct_summary")


def get_conduct_summary_state_path(profile_name: str) -> str:
    """Returns the path for the conduct summary download state file."""
    return os.path.join(get_profile_dir(profile_name), "conduct_summary_state.json")


def get_raw_ranked_stats_path(profile_name: str) -> str:
    """Returns the file path for the raw ranked stats HTML."""
    profile_dir = get_profile_dir(profile_name)
    # The file is saved in the root of the profile's data folder
    return os.path.join(profile_dir, "raw_ranked_stats.html")


# --- Processed Data Paths  ---


def get_processed_dir(profile_name: str) -> str:
    """Returns the directory path for processed data files."""
    return os.path.join(get_profile_dir(profile_name), "processed")


def get_processed_conduct_summary_path(profile_name: str) -> str:
    """Returns the full CSV file path for processed conduct summaries."""
    return os.path.join(get_processed_dir(profile_name), "conduct_summary.csv")


def delete_profile_data_dir(profile_name: str):
    """Safely removes the entire data directory for a given profile."""
    profile_dir = get_profile_dir(profile_name)
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)


def get_processed_ranked_stats_path(profile_name: str) -> str:
    """Returns the CSV file path for processed ranked stats."""
    return os.path.join(get_processed_dir(profile_name), "ranked_hero_stats.csv")
