# ui/conduct_summary_tab.py

import streamlit as st
import pandas as pd
import os

from modules.common import config_manager, path_manager, session_manager
from modules.download import conduct_summary as download_conduct
from modules.process import conduct_summary as process_conduct

@st.cache_data
def load_profile_data(profile_name: str) -> pd.DataFrame | None:
    """Loads the processed CSV data for a given profile."""
    if not profile_name:
        return None
    csv_path = path_manager.get_processed_conduct_summary_path(profile_name)
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path, parse_dates=['SummaryDate'])
    return None

def render():
    """Renders the main dashboard tab for behavior summaries."""
    config = config_manager.load_config()
    profile_names = [p['profile_name'] for p in config.get('profiles', [])]
    
    if not profile_names:
        st.warning("👋 Welcome! No profiles found.")
        st.info("Please go to the '⚙️ Profile Management' tab to add your first profile.")
        return

    st.sidebar.header("Dashboard Controls")
    current_active_profile = config.get('active_profile')
    
    try:
        active_profile_index = profile_names.index(current_active_profile)
    except ValueError:
        active_profile_index = 0

    selected_profile = st.sidebar.selectbox(
        "Select Profile", 
        options=profile_names,
        index=active_profile_index
    )
    
    if selected_profile != current_active_profile:
        config['active_profile'] = selected_profile
        config_manager.save_config(config)
        st.rerun()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"Conduct Summary for: `{selected_profile}`")
    with col2:
        if st.button("Download & Process Data"):
            try:
                active_profile_details = config_manager.get_active_profile(config)
                with st.spinner("Step 1/2: Downloading new data..."):
                    session = session_manager.create_session(active_profile_details)
                    download_conduct.fetch(session, active_profile_details, config)
                
                with st.spinner("Step 2/2: Processing local files..."):
                    process_conduct.process(active_profile_details['profile_name'])
                
                st.cache_data.clear()
                st.success("Data refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

    df = load_profile_data(selected_profile)
    if df is not None and not df.empty:
        st.markdown("### Latest Snapshot")
        latest = df.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest Behavior Score", f"{latest['BehaviorScore']:,}")
        c2.metric("Latest Commends", f"{latest['Commends']}")
        c3.metric("Average Commends", f"{df['Commends'].mean():.1f}")
        
        st.markdown("### Behavior Score Trend")
        chart_df = df.sort_values(by='SummaryDate').set_index('SummaryDate')
        st.line_chart(chart_df['BehaviorScore'])
        
        st.markdown("### Complete History")
        st.dataframe(df)
    else:
        st.info(f"No data found for '{selected_profile}'. Click 'Download & Process Data' to get started.")
