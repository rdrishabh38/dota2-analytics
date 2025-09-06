import streamlit as st
import pandas as pd
import json
import os
from download_data import Downloader
from process_data import Processor

# --- Page Configuration ---
st.set_page_config(
    page_title="Dota 2 Analytics Hub",
    page_icon="📊",
    layout="wide"
)

# --- Helper Functions ---

def get_config():
    """Loads the main configuration file."""
    with open("config.json", 'r') as f:
        return json.load(f)

def update_active_profile(profile_name):
    """Updates the active_profile in the config file."""
    config = get_config()
    config['active_profile'] = profile_name
    with open("config.json", 'w') as f:
        json.dump(config, f, indent=2)

@st.cache_data
def load_profile_data(profile_name):
    """Loads the processed CSV data for a given profile, caching the result."""
    csv_path = os.path.join("data", profile_name, "conduct_summary.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=['SummaryDate'])
        return df
    return None

# --- Main Application ---

st.title("📊 Dota 2 Analytics Hub")
st.markdown("Your personal dashboard for Dota 2 conduct summary data.")

# --- Sidebar Controls ---
st.sidebar.header("Controls")

config = get_config()
profile_names = [p['profile_name'] for p in config.get('profiles', [])]
current_active_profile = config.get('active_profile')

# Dropdown to select the profile
selected_profile = st.sidebar.selectbox(
    "Select Profile",
    options=profile_names,
    index=profile_names.index(current_active_profile) if current_active_profile in profile_names else 0
)

# Update config if selection changes
if selected_profile != current_active_profile:
    update_active_profile(selected_profile)
    st.rerun()

# Button to refresh data
if st.sidebar.button("Download & Process New Data"):
    st.sidebar.info("Starting data refresh... This may take a moment.")
    
    with st.spinner("Step 1/2: Downloading new data..."):
        try:
            downloader = Downloader()
            downloader.download_conduct_summary()
            st.success("Download complete!")
        except Exception as e:
            st.error(f"An error occurred during download: {e}")

    with st.spinner("Step 2/2: Processing data..."):
        try:
            processor = Processor()
            processor.process_conduct_summary()
            st.success("Processing complete!")
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
    
    # Clear the cache to force data reload
    st.cache_data.clear()
    st.sidebar.success("Data refreshed successfully!")


# --- Dashboard Display ---
st.header(f"Conduct Summary for: `{selected_profile}`")

df = load_profile_data(selected_profile)

if df is not None and not df.empty:
    # --- Key Metrics (KPIs) ---
    st.markdown("### Latest Snapshot")
    latest_summary = df.iloc[0] # Data is sorted descending by date
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Behavior Score", f"{latest_summary['BehaviorScore']:,}")
    col2.metric("Latest Commends", f"{latest_summary['Commends']}")
    col3.metric("Average Commends", f"{df['Commends'].mean():.1f}")

    # --- Behavior Score Over Time Chart ---
    st.markdown("### Behavior Score Trend")
    
    # Prepare data for charting
    chart_df = df.sort_values(by='SummaryDate').set_index('SummaryDate')
    st.line_chart(chart_df['BehaviorScore'])

    # --- Full Data Table ---
    st.markdown("### Complete History")
    st.dataframe(df)

else:
    st.warning("No data found for this profile.")
    st.info("Click the 'Download & Process New Data' button in the sidebar to get started.")
