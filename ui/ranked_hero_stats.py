# ui/ranked_hero_stats_tab.py

import streamlit as st
import pandas as pd
import os

from modules.common import config_manager, path_manager, session_manager
from modules.download import ranked_hero_stats as download_ranked
from modules.process import ranked_hero_stats as process_ranked

@st.cache_data
def load_ranked_data(profile_name: str) -> pd.DataFrame | None:
    """Loads the processed ranked hero stats CSV."""
    if not profile_name:
        return None
    csv_path = path_manager.get_processed_ranked_stats_path(profile_name)
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

def render():
    """Renders the Ranked Hero Statistics tab."""
    config = config_manager.load_config()
    active_profile_name = config.get("active_profile")

    if not active_profile_name:
        st.warning("Please select or add a profile in the 'Profile Management' tab first.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"Ranked Hero Stats for: `{active_profile_name}`")
    with col2:
        if st.button("🔄 Refresh Hero Stats"):
            try:
                active_profile = config_manager.get_active_profile(config)
                with st.spinner("Fetching and processing hero stats..."):
                    # Step 1: Download
                    session = session_manager.create_session(active_profile)
                    download_ranked.fetch(session, active_profile)
                    
                    # Step 2: Process
                    process_ranked.process(active_profile['profile_name'])
                
                st.cache_data.clear()
                st.success("Hero stats refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

    df = load_ranked_data(active_profile_name)
    if df is not None and not df.empty:
        st.markdown("### Hero Performance Overview")
        
        # Display key metrics
        c1, c2, c3 = st.columns(3)
        most_played_hero = df.loc[(df['Wins'] + df['Losses']).idxmax()]
        best_win_rate_hero = df.loc[df['WinRate'].idxmax()]
        
        c1.metric("Most Played Hero", most_played_hero['Hero'], f"{int(most_played_hero['Wins'] + most_played_hero['Losses'])} games")
        c2.metric("Best Win Rate Hero", best_win_rate_hero['Hero'], f"{best_win_rate_hero['WinRate']:.1f}%")
        c3.metric("Total Unique Heroes Played", f"{len(df)}")
        
        st.markdown("### Full Statistics")
        st.dataframe(df)
    else:
        st.info(f"No hero stats found for '{active_profile_name}'. Click 'Refresh Hero Stats' to download them.")
