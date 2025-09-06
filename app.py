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
    """Loads config. If it doesn't exist, creates a default one."""
    if not os.path.exists("config.json"):
        default_config = {
            "active_profile": "", "profiles": [], "max_retries": 5, "initial_backoff_seconds": 5
        }
        with open("config.json", 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open("config.json", 'r') as f:
        return json.load(f)

def save_config(config_data):
    """Saves the configuration data to the file."""
    with open("config.json", 'w') as f:
        json.dump(config_data, f, indent=2)

@st.cache_data
def load_profile_data(profile_name):
    """Loads the processed CSV data for a given profile."""
    if not profile_name: return None
    csv_path = os.path.join("data", profile_name, "conduct_summary.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=['SummaryDate'])
        return df
    return None

# --- Main Application UI ---

st.title("📊 Dota 2 Analytics Hub")
# --- Adding disclaimer that his app is not associated with Valve ---
st.sidebar.markdown("---")
st.sidebar.caption(
    "This is an unofficial application and is not affiliated with Valve or Steam. "
    "Steam and the Steam logo are trademarks and/or registered trademarks of "
    "Valve Corporation in the U.S. and/or other countries."
)

# Ensure the root 'data' directory exists
if not os.path.exists("data"):
    os.makedirs("data")

tab1, tab2 = st.tabs(["📊 Behaviour Summary", "⚙️ Profile Management"])

# --- TAB 1: Dashboard ---
with tab1:
    config = get_config()
    profile_names = [p['profile_name'] for p in config.get('profiles', [])]
    
    if not profile_names:
        st.warning("👋 Welcome! No profiles found.")
        st.info("Please go to the '⚙️ Profile Management' tab to add your first profile.")
    else:
        st.sidebar.header("Dashboard Controls")
        current_active_profile = config.get('active_profile')
        selected_profile = st.sidebar.selectbox(
            "Select Profile", options=profile_names,
            index=profile_names.index(current_active_profile) if current_active_profile in profile_names else 0
        )
        if selected_profile != current_active_profile:
            config['active_profile'] = selected_profile
            save_config(config)
            st.rerun()

        if st.sidebar.button("Download & Process Behaviour Summary Data"):
            # ... (Rest of the button logic is unchanged)
            st.sidebar.info("Starting data refresh...")
            with st.spinner("Step 1/2: Downloading..."): Downloader().download_conduct_summary()
            with st.spinner("Step 2/2: Processing..."): Processor().process_conduct_summary()
            st.cache_data.clear()
            st.sidebar.success("Data refreshed!")
            st.rerun()
            
        st.header(f"Conduct Summary for: `{selected_profile}`")
        df = load_profile_data(selected_profile)
        if df is not None and not df.empty:
            # ... (Rest of the dashboard display is unchanged)
            st.markdown("### Latest Snapshot")
            latest = df.iloc[0]; c1, c2, c3 = st.columns(3)
            c1.metric("Latest Behavior Score", f"{latest['BehaviorScore']:,}")
            c2.metric("Latest Commends", f"{latest['Commends']}")
            c3.metric("Average Commends", f"{df['Commends'].mean():.1f}")
            st.markdown("### Behavior Score Trend")
            chart_df = df.sort_values(by='SummaryDate').set_index('SummaryDate')
            st.line_chart(chart_df['BehaviorScore'])
            st.markdown("### Complete History"); st.dataframe(df)
        else:
            st.info("No data found for this profile. Click 'Download & Process New Data' in the sidebar.")

# --- TAB 2: Profile Management ---
with tab2:
    st.header("Manage Your Profiles")
    st.error(
        """
        ### ⚠️ Important Security Warning
        Your `steamLoginSecure` cookie is like a temporary password for your account. 
        **Never share this cookie with anyone.** If someone gets this value, they 
        can gain access to your Steam account. Treat it with the same level of 
        security as your actual password.

        To invalidate this cookie, simply log out of Steam on the browser(chrome/firefox/brave etc)
        where you obtained it. This will force the cookie to expire and prevent any unauthorized access.
        """
    )
    config = get_config(); profiles = config.get('profiles', [])
    profile_names = [p['profile_name'] for p in profiles]
    col1, col2 = st.columns([2,1])
    with col1:
        selection_options = ["-- Add New Profile --"] + profile_names
        selected_profile_to_edit = st.selectbox("Select or add a profile", options=selection_options)
    st.markdown("---")
    current_data = {"profile_name": "", "custom_url": "", "cookies": {"sessionid": "", "steamLoginSecure": "", "browserid": "", "steamCountry": "", "steamparental": ""}}
    is_new_profile = selected_profile_to_edit == "-- Add New Profile --"
    if not is_new_profile:
        current_data = next((p for p in profiles if p['profile_name'] == selected_profile_to_edit), current_data)

    with st.form("profile_form"):
        st.subheader("Profile Details")
        new_profile_name = st.text_input("Profile Name", value=current_data['profile_name'])
        new_custom_url = st.text_input("Steam Custom URL", value=current_data['custom_url'])
        st.subheader("Cookie Values")
        cookies = current_data.get('cookies', {})
        new_sessionid = st.text_input("sessionid", value=cookies.get('sessionid'), type="password")
        new_steamLoginSecure = st.text_input("steamLoginSecure", value=cookies.get('steamLoginSecure'), type="password")
        new_browserid = st.text_input("browserid", value=cookies.get('browserid'), type="password")
        new_steamCountry = st.text_input("steamCountry", value=cookies.get('steamCountry'), type="password")
        new_steamparental = st.text_input("steamparental", value=cookies.get('steamparental'), type="password")
        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            if not new_profile_name: st.error("Profile Name cannot be empty.")
            else:
                updated_profile_data = {"profile_name": new_profile_name, "custom_url": new_custom_url, "cookies": {"sessionid": new_sessionid, "steamLoginSecure": new_steamLoginSecure, "browserid": new_browserid, "steamCountry": new_steamCountry, "steamparental": new_steamparental}}
                
                # --- THIS IS THE NEW LOGIC ---
                # Create the data directory for the profile when it's saved
                profile_data_path = os.path.join("data", new_profile_name)
                os.makedirs(profile_data_path, exist_ok=True)
                # --- END NEW LOGIC ---
                
                if is_new_profile:
                    if new_profile_name in profile_names: st.error(f"Profile '{new_profile_name}' already exists.")
                    else:
                        profiles.append(updated_profile_data)
                        config['profiles'] = profiles
                        if len(profiles) == 1: config['active_profile'] = new_profile_name
                        save_config(config)
                        st.success(f"Added profile: '{new_profile_name}'")
                        st.rerun()
                else:
                    idx = next((i for i, p in enumerate(profiles) if p['profile_name'] == selected_profile_to_edit), -1)
                    if idx != -1:
                        profiles[idx] = updated_profile_data
                        config['profiles'] = profiles
                        if config['active_profile'] == selected_profile_to_edit: config['active_profile'] = new_profile_name
                        save_config(config)
                        st.success(f"Updated profile: '{new_profile_name}'")
                        st.rerun()

    if not is_new_profile:
        # ... (Delete Profile section is unchanged) ...
        st.markdown("---"); st.subheader("Delete Profile")
        st.warning(f"⚠️ Deleting a profile is permanent.")
        if st.checkbox(f"I want to permanently delete '{selected_profile_to_edit}'"):
            if st.button("❌ Delete Profile Permanently"):
                profiles_after_deletion = [p for p in profiles if p['profile_name'] != selected_profile_to_edit]
                config['profiles'] = profiles_after_deletion
                if config['active_profile'] == selected_profile_to_edit:
                    config['active_profile'] = profiles_after_deletion[0]['profile_name'] if profiles_after_deletion else ""
                save_config(config)
                st.success(f"Deleted profile: '{selected_profile_to_edit}'")
                st.rerun()
