# app.py

import streamlit as st
from modules.common import config_manager
from ui import conduct_summary_tab, profile_management_tab

# --- Page Configuration (Global) ---
st.set_page_config(
    page_title="Dota 2 Analytics Hub",
    page_icon="📊",
    layout="wide"
)

def main():
    """Main function to run the Streamlit application."""
    st.title("📊 Dota 2 Analytics Hub")
    
    # Ensure config file exists before proceeding
    config_manager.initialize_config()

    # Create the tabs
    tab1, tab2 = st.tabs(["📊 Behaviour Summary", "⚙️ Profile Management"])

    # Render each tab by calling its dedicated function
    with tab1:
        conduct_summary_tab.render()
    
    with tab2:
        profile_management_tab.render()

    # --- Footer (Global) ---
    st.sidebar.markdown("---")
    st.sidebar.caption(
    "This is an unofficial application and is not affiliated with Valve or Steam. "
    "Steam and the Steam logo are trademarks and/or registered trademarks of "
    "Valve Corporation in the U.S. and/or other countries."
    )
    st.markdown("---")
    st.caption(
    "This program is licensed under the GNU General Public License v3.0. "
    "Copyright (C) 2025 Kocha."
    )

if __name__ == "__main__":
    main()
