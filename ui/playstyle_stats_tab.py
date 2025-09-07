# ui/playstyle_stats_tab.py

import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

from modules.common import config_manager, path_manager, session_manager
from modules.download import playstyle_stats as download_playstyle
from modules.process import playstyle_stats as process_playstyle

@st.cache_data
def load_playstyle_data(profile_name: str) -> pd.DataFrame | None:
    """Loads the processed playstyle stats CSV."""
    if not profile_name: return None
    csv_path = path_manager.get_processed_playstyle_stats_path(profile_name)
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

def create_playstyle_pentagon(df: pd.DataFrame) -> go.Figure:
    """Creates a custom Plotly pentagon chart based on the Dota 2 in-game UI."""
    
    # 1. Define the five categories in the correct order
    categories = ['FIGHTING', 'FARMING', 'SUPPORTING', 'PUSHING', 'VERSATILITY']
    
    # 2. Calculate average scores from the data
    avg_scores = {
        'FIGHTING': df['FightScore'].mean(),
        'FARMING': df['FarmScore'].mean(),
        'PUSHING': df['PushScore'].mean(),
        'VERSATILITY': df['Versatility'].mean(),
        'ASSISTS': df['Assists'].mean(),
        'HEALS': df['Heals'].mean()
    }

    # 3. Create a composite "SUPPORTING" score
    # We normalize assists and heals against reasonable maximums and average them.
    norm_assists = min(avg_scores['ASSISTS'] / 30, 1.0) # Cap at 30 assists avg
    norm_heals = min(avg_scores['HEALS'] / 8000, 1.0)  # Cap at 8k healing avg
    avg_scores['SUPPORTING'] = (norm_assists + norm_heals) / 2

    # 4. Normalize all scores to a 0-1 scale for plotting
    # These max values are estimates and can be tweaked for better visualization.
    normalized_values = [
        min(avg_scores['FIGHTING'], 1.0),                  # Already 0-1
        min(avg_scores['FARMING'] / 200, 1.0),             # Max estimated at 200
        min(avg_scores['SUPPORTING'], 1.0),                # Already calculated as 0-1
        min(avg_scores['PUSHING'] / 20000, 1.0),           # Max estimated at 20k tower damage
        min(avg_scores['VERSATILITY'], 1.0)                # Versatility
    ]
    
    # 5. Create the Plotly figure
    fig = go.Figure()

    # Add the grey background pentagon (maximum values)
    fig.add_trace(go.Scatterpolar(
        r=[1, 1, 1, 1, 1], # Full pentagon
        theta=categories,
        fill='toself',
        fillcolor='rgba(100, 100, 100, 0.4)',
        line=dict(color='rgba(150, 150, 150, 0.8)'),
        name='Max Range'
    ))

    # Add the player's actual data trace
    fig.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(230, 126, 34, 0.5)',
        name='Your Playstyle',
        line=dict(color='rgba(230, 126, 34, 1.0)'),
        marker=dict(color='rgba(230, 126, 34, 1.0)', size=10, symbol='circle')
    ))

    # Customize the layout to look like the in-game UI
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),
            angularaxis=dict(showline=False, tickfont=dict(size=14))
        ),
        showlegend=False,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', # Transparent background
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def render():
    """Renders the User Playstyle Statistics tab."""
    config = config_manager.load_config()
    active_profile_name = config.get("active_profile")

    if not active_profile_name:
        st.warning("Please select or add a profile first.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"Playstyle Stats for: `{active_profile_name}`")
        st.caption("Based on your last 50 games(ranked + unranked + turbo).")
    with col2:
        if st.button("🔄 Refresh Playstyle Stats"):
            # ... (button logic is unchanged) ...
            try:
                active_profile = config_manager.get_active_profile(config)
                with st.spinner("Fetching and processing playstyle stats..."):
                    session = session_manager.create_session(active_profile)
                    download_playstyle.fetch(session, active_profile)
                    process_playstyle.process(active_profile['profile_name'])
                st.cache_data.clear()
                st.success("Playstyle stats refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

    df = load_playstyle_data(active_profile_name)
    if df is not None and not df.empty:
        st.markdown("### Playstyle Pentagon")
        
        # --- NEW: Call the function to create the custom chart ---
        pentagon_fig = create_playstyle_pentagon(df)
        st.plotly_chart(pentagon_fig, use_container_width=True)

        st.markdown("### Full Match History")
        st.dataframe(df)
    else:
        st.info("No playstyle stats found. Click 'Refresh Playstyle Stats' to download them.")
