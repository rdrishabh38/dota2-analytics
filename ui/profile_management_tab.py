# ui/profile_management_tab.py

import streamlit as st
import os
from modules.common import config_manager, path_manager

def render():
    """Renders the profile management tab."""
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
    
    config = config_manager.load_config()
    profiles = config.get('profiles', [])
    profile_names = [p['profile_name'] for p in profiles]
    
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
            if not new_profile_name:
                st.error("Profile Name cannot be empty.")
            else:
                updated_profile_data = {
                    "profile_name": new_profile_name, 
                    "custom_url": new_custom_url, 
                    "cookies": {
                        "sessionid": new_sessionid, "steamLoginSecure": new_steamLoginSecure, 
                        "browserid": new_browserid, "steamCountry": new_steamCountry, 
                        "steamparental": new_steamparental
                    }
                }
                
                os.makedirs(path_manager.get_profile_dir(new_profile_name), exist_ok=True)
                
                if is_new_profile:
                    if new_profile_name in profile_names:
                        st.error(f"Profile '{new_profile_name}' already exists.")
                    else:
                        profiles.append(updated_profile_data)
                        config['profiles'] = profiles
                        if len(profiles) == 1:
                            config['active_profile'] = new_profile_name
                        config_manager.save_config(config)
                        st.success(f"Added profile: '{new_profile_name}'")
                        st.rerun()
                else:
                    idx = next((i for i, p in enumerate(profiles) if p['profile_name'] == selected_profile_to_edit), -1)
                    if idx != -1:
                        profiles[idx] = updated_profile_data
                        config['profiles'] = profiles
                        if config['active_profile'] == selected_profile_to_edit:
                            config['active_profile'] = new_profile_name
                        config_manager.save_config(config)
                        st.success(f"Updated profile: '{new_profile_name}'")
                        st.rerun()

    if not is_new_profile:
        st.markdown("---")
        st.subheader("Delete Profile")
        st.warning(f"⚠️ This is permanent and will delete all data in 'data/{selected_profile_to_edit}'.")
        if st.checkbox(f"I want to permanently delete '{selected_profile_to_edit}'"):
            if st.button("❌ Delete Profile Permanently"):
                path_manager.delete_profile_data_dir(selected_profile_to_edit)
                config['profiles'] = [p for p in profiles if p['profile_name'] != selected_profile_to_edit]
                if config['active_profile'] == selected_profile_to_edit:
                    config['active_profile'] = config['profiles'][0]['profile_name'] if config['profiles'] else ""
                config_manager.save_config(config)
                st.success(f"Deleted profile: '{selected_profile_to_edit}'")
                st.rerun()
