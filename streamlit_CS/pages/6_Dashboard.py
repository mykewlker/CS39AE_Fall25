import streamlit as st
import pandas as pd
import altair as alt  # Import the altair library
import numpy as np # Import numpy for conditional logic

# --- Page Setup ---
# Set the page configuration to be wide
st.set_page_config(layout="wide")

# --- Data Loading ---
# Player stats URL
DATA_URL = 'https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_2023.csv'

@st.cache_data  # Cache the data so it doesn't re-load on every interaction
def load_data(url):
    """
    Loads weekly player stats data from the specified nflverse URL.
    """
    try:
        data = pd.read_csv(url)
        
        # --- Column Name Standardization ---
        if 'player_name' not in data.columns:
            st.error("Data source is missing 'player_name' column. Cannot proceed.")
            return None
        
        # We need these columns for our display
        required_cols = {
            'player_name': 'Player',
            'position': 'Position',
            'recent_team': 'Team'
        }
        
        # Check for fantasy points columns
        if 'fantasy_points_ppr' in data.columns:
            required_cols['fantasy_points_ppr'] = 'TotalFantasyPoints'
        elif 'fantasy_points' in data.columns:
            required_cols['fantasy_points'] = 'TotalFantasyPoints'
            
        data = data.rename(columns=required_cols)

        # Calculate simple points if no fantasy points column was found
        if 'TotalFantasyPoints' not in data.columns:
            st.warning("Could not find 'fantasy_points_ppr', calculating simple points.")
            data['TotalFantasyPoints'] = (
                data.get('passing_yards', 0) / 25 +
                data.get('passing_tds', 0) * 4 +
                data.get('rushing_yards', 0) / 10 +
                data.get('rushing_tds', 0) * 6 +
                data.get('receiving_yards', 0) / 10 +
                data.get('receiving_tds', 0) * 6 -
                data.get('interceptions', 0) * 2 -
                data.get('fumbles_lost', 0) * 2
            )
            
        # Fill NaN values in key columns to prevent errors
        key_stat_cols = ['TotalFantasyPoints', 'passing_yards', 'passing_tds', 'rushing_yards', 'rushing_tds', 'receiving_yards', 'receiving_tds']
        for col in key_stat_cols:
            if col in data.columns:
                data[col] = data[col].fillna(0)
            else:
                data[col] = 0 # Create column if it doesn't exist

        return data
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load the main dataframe
df = load_data(DATA_URL)

if df is not None:
    # --- Pre-calculate season totals for rankings ---
    # We group by Player and Position to get total points, then rank them within their position
    season_totals_df = df.groupby(['Player', 'Position'])['TotalFantasyPoints'].sum().reset_index()
    season_totals_df['Pos. Rank'] = season_totals_df.groupby('Position')['TotalFantasyPoints'].rank(ascending=False, method='min').astype(int)

    # --- Main Page Title ---
    st.title("Fantasy Football Dashboard")

    # --- Sidebar ---
    st.sidebar.header("Player Selection")
    
    try:
        players = sorted(df['Player'].unique())
        selected_player = st.sidebar.selectbox("Select a Player", players)
    except Exception as e:
        st.sidebar.error(f"Could not load player list: {e}")
        selected_player = None

    # --- Player Stats (Dynamic) ---
    st.sidebar.header("Player Season Stats (2023)")
    
    if selected_player:
        # Filter the dataframe for the selected player
        player_data = df[df['Player'] == selected_player]
        
        if not player_data.empty:
            # Get season totals by summing all weekly stats
            season_stats = player_data.sum(numeric_only=True)
            
            # Get non-numeric info from the first available week
            position = player_data['Position'].iloc[0]
            team = player_data['Team'].iloc[0] # Get the player's team
            
            st.sidebar.markdown(f"### {selected_player}")
            st.sidebar.write(f"**Position:** {position} | **Team:** {team}")
            
            st.sidebar.divider()
            
            # Display key metrics in columns
            m_col1, m_col2 = st.sidebar.columns(2)
            
            total_tds = int(season_stats.get('rushing_tds', 0) + 
                            season_stats.get('receiving_tds', 0) + 
                            season_stats.get('passing_tds', 0))
            
            m_col1.metric("Total Points (PPR)", f"{season_stats.get('TotalFantasyPoints', 0):.2f}")
            m_col2.metric("Total TDs", f"{total_tds}")

            st.sidebar.markdown("---")
            st.sidebar.subheader("Offensive Yards")
            
            if 'passing_yards' in season_stats and season_stats['passing_yards'] > 0:
                st.sidebar.metric("Passing Yards", f"{int(season_stats['passing_yards'])}")
                
            if 'rushing_yards' in season_stats and season_stats['rushing_yards'] > 0:
                st.sidebar.metric("Rushing Yards", f"{int(season_stats['rushing_yards'])}")
                
            if 'receiving_yards' in season_stats and season_stats['receiving_yards'] > 0:
                st.sidebar.metric("Receiving Yards", f"{int(season_stats['receiving_yards'])}")
            
            # --- Season Snapshot Section ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Season Snapshot")
            
            # Get rank info from our pre-calculated dataframe
            player_rank_info = season_totals_df[season_totals_df['Player'] == selected_player]
            positional_rank = player_rank_info['Pos. Rank'].iloc[0]
            
            # Get games played
            games_played = len(player_data)
            
            # Calculate average points
            avg_points = season_stats.get('TotalFantasyPoints', 0) / games_played if games_played > 0 else 0
            
            # Display snapshot metrics
            r_col1, r_col2 = st.sidebar.columns(2)
            r_col1.metric("Positional Rank", f"#{positional_rank} {position}")
            r_col2.metric("Games Played", f"{games_played}")
            
            st.sidebar.metric("Avg Points / Game", f"{avg_points:.2f}")

        else:
            st.sidebar.error("Could not find stats for this player.")

    # --- Main Content Area (2x2 Grid) ---
    
    # Create the two main columns for the grid
    main_col1, main_col2 = st.columns(2)

    with main_col1:
        # --- Top-Left: Weekly Chart ---
        if selected_player:
            player_data = df[df['Player'] == selected_player]
            
            st.subheader("Weekly Points Chart")
            
            chart_cols = ['week', 'TotalFantasyPoints', 'opponent_team']
            existing_chart_cols = [col for col in chart_cols if col in player_data.columns]
            weekly_chart_df = player_data[existing_chart_cols].sort_values(by='week')
            
            weekly_chart_df = weekly_chart_df.rename(columns={
                'opponent_team': 'Opponent',
                'TotalFantasyPoints': 'Fantasy Points (PPR)'
            })

            chart_data = weekly_chart_df.reset_index()[['week', 'Fantasy Points (PPR)', 'Opponent']]

            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('week:O', title='Week', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Fantasy Points (PPR):Q', title='Fantasy Points (PPR)'),
                tooltip=['week', 'Opponent', 'Fantasy Points (PPR)']
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        
        else:
             st.info("Select a player from the sidebar to see their weekly stats and chart.")

    with main_col2:
        # --- Top-Right: Top Fantasy Players ---
        st.subheader("Top Fantasy Players (2023)")
        
        try:
            # Aggregate points by player and get the top 30
            player_points = df.groupby('Player')['TotalFantasyPoints'].sum().nlargest(30).reset_index()
            player_points['TotalFantasyPoints'] = player_points['TotalFantasyPoints'].round(2)
            player_points.index = player_points.index + 1 # Start index at 1
            # Give the dataframe a fixed height to make it scrollable
            st.dataframe(player_points, use_container_width=True, hide_index=True, height=500)
        except Exception as e:
            st.error(f"Could not calculate top players: {e}")

    # --- Bottom Row ---
    # Create two columns for the bottom row
    bottom_col1, bottom_col2 = st.columns(2)

    with bottom_col1:
        # --- Bottom-Left: Weekly Stats Table ---
        if selected_player:
            player_data = df[df['Player'] == selected_player]
            st.subheader(f"Weekly Stats Table (2023)")
            
            cols_to_show = [
                'week', 'opponent_team', 'TotalFantasyPoints', 'passing_yards', 
                'passing_tds', 'rushing_yards', 'rushing_tds', 'receiving_yards', 'receiving_tds'
            ]
            
            existing_cols_to_show = [col for col in cols_to_show if col in player_data.columns]
            weekly_display_df = player_data[existing_cols_to_show].sort_values(by='week').set_index('week')
            
            weekly_display_df = weekly_display_df.rename(columns={
                'opponent_team': 'Opponent',
                'TotalFantasyPoints': 'Fantasy Points (PPR)'
            })
            
            # Give the dataframe a fixed height
            st.dataframe(weekly_display_df, use_container_width=True, height=350)
        
        else:
            st.info("Select a player to see their weekly stats.")

    with bottom_col2:
        # --- Bottom-Right: Player vs. Player ---
        st.subheader("Player vs. Player Comparison (2023)")
        
        selected_player_2 = st.selectbox("Select a comparison player", players, index=1)

        if selected_player and selected_player_2:
            # Create two columns for the side-by-side comparison
            comp_col1, comp_col2 = st.columns(2)
            
            # --- Player 1 (from sidebar) ---
            with comp_col1:
                player_1_data = df[df['Player'] == selected_player]
                
                if not player_1_data.empty:
                    p1_stats = player_1_data.sum(numeric_only=True)
                    p1_pos = player_1_data['Position'].iloc[0]
                    p1_team = player_1_data['Team'].iloc[0]
                    p1_tds = int(p1_stats.get('rushing_tds', 0) + p1_stats.get('receiving_tds', 0) + p1_stats.get('passing_tds', 0))

                    st.markdown(f"#### {selected_player}")
                    st.write(f"**{p1_pos} | {p1_team}**")
                    st.divider()
                    st.metric("Total Points (PPR)", f"{p1_stats.get('TotalFantasyPoints', 0):.2f}")
                    st.metric("Total TDs", f"{p1_tds}")
                    
                else:
                    st.error(f"No data for {selected_player}")

            # --- Player 2 (from new selectbox) ---
            with comp_col2:
                player_2_data = df[df['Player'] == selected_player_2]
                
                if not player_2_data.empty:
                    p2_stats = player_2_data.sum(numeric_only=True)
                    p2_pos = player_2_data['Position'].iloc[0]
                    p2_team = player_2_data['Team'].iloc[0]
                    p2_tds = int(p2_stats.get('rushing_tds', 0) + p2_stats.get('receiving_tds', 0) + p2_stats.get('passing_tds', 0))

                    st.markdown(f"#### {selected_player_2}")
                    st.write(f"**{p2_pos} | {p2_team}**")
                    st.divider()
                    st.metric("Total Points (PPR)", f"{p2_stats.get('TotalFantasyPoints', 0):.2f}")
                    st.metric("Total TDs", f"{p2_tds}")
                    
                else:
                    st.error(f"No data for {selected_player_2}")
        
        elif not selected_player:
            st.info("Select a player from the sidebar to enable comparison.")

else:
    st.error("Failed to load data. The dashboard cannot be displayed.")
    st.info("Please check the DATA_URL or your internet connection.")

