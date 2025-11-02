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
# NEW: Schedule data URL
SCHEDULE_DATA_URL = 'https://github.com/nflverse/nflverse-data/releases/download/schedules/schedules_2023.csv'


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

@st.cache_data
def load_schedule_data(url):
    """
    Loads the 2023 season schedule data from the specified nflverse URL.
    """
    try:
        schedule = pd.read_csv(url)
        # We only care about regular season games
        schedule = schedule[schedule['game_type'] == 'REG']
        return schedule
    except Exception as e:
        st.error(f"Error loading schedule data: {e}")
        return None

# Load both dataframes
df = load_data(DATA_URL)
schedule_df = load_schedule_data(SCHEDULE_DATA_URL)

if df is not None:
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
    
    # We need to declare 'team' here so we can use it for the schedule
    team = None 
    
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
        
        else:
            st.sidebar.error("Could not find stats for this player.")
    
    # --- Game Schedule (Dynamic) ---
    st.sidebar.header("Team Schedule (2023)")
    if team and schedule_df is not None:
        # Find all games (home or away) for the selected player's team
        team_schedule = schedule_df[
            (schedule_df['home_team'] == team) | (schedule_df['away_team'] == team)
        ].sort_values(by='week')
        
        if not team_schedule.empty:
            # Create Opponent column
            team_schedule['Opponent'] = np.where(
                team_schedule['home_team'] == team, 
                "vs " + team_schedule['away_team'], 
                "@ " + team_schedule['home_team']
            )
            
            # Create Result column
            team_schedule['Result'] = np.where(
                team_schedule['result'] > 0, 
                f"W {team_schedule['home_score']}-{team_schedule['away_score']}", 
                np.where(
                    team_schedule['result'] < 0,
                    f"L {team_schedule['home_score']}-{team_schedule['away_score']}",
                    "T" # For ties, though rare
                )
            )
            # Fix result string for away team
            team_schedule['Result'] = np.where(
                (team_schedule['away_team'] == team) & (team_schedule['result'] < 0),
                f"W {team_schedule['away_score']}-{team_schedule['home_score']}",
                np.where(
                    (team_schedule['away_team'] == team) & (team_schedule['result'] > 0),
                    f"L {team_schedule['away_score']}-{team_schedule['home_score']}",
                    team_schedule['Result'] # Keep W/L string from home team logic
                )
            )
            
            
            # Select and display
            display_cols = ['week', 'Opponent', 'Result']
            st.sidebar.dataframe(
                team_schedule[display_cols].set_index('week'), 
                use_container_width=True
            )
        else:
            st.sidebar.warning(f"No schedule data found for team: {team}")
    
    elif not team:
        st.sidebar.info("Select a player to see their team's schedule.")
    else:
        st.sidebar.error("Schedule data could not be loaded.")


    # --- Main Content Area ---
    col1, col2 = st.columns([2, 1])

    with col1:
        # --- Weekly Performance (Dynamic) ---
        st.subheader(f"Weekly Performance (2023)")
        if selected_player:
            player_data = df[df['Player'] == selected_player]
            
            # Define columns to display for the weekly log
            cols_to_show = [
                'week', 
                'opponent_team', 
                'TotalFantasyPoints', 
                'passing_yards', 
                'passing_tds', 
                'rushing_yards', 
                'rushing_tds', 
                'receiving_yards', 
                'receiving_tds'
            ]
            
            # Filter for columns that actually exist in our dataframe
            existing_cols_to_show = [col for col in cols_to_show if col in player_data.columns]
            
            weekly_display_df = player_data[existing_cols_to_show].sort_values(by='week').set_index('week')
            
            # Rename for a cleaner display
            weekly_display_df = weekly_display_df.rename(columns={
                'opponent_team': 'Opponent',
                'TotalFantasyPoints': 'Fantasy Points (PPR)'
            })
            
            st.dataframe(weekly_display_df, use_container_width=True)
            
            # --- UPDATED: Weekly Points Bar Chart ---
            st.subheader("Weekly Points Chart")
            
            # We need to reset the index so 'week' becomes a column for Altair
            # We also need 'Opponent' for the tooltip, so let's grab it
            chart_data = weekly_display_df.reset_index()[['week', 'Fantasy Points (PPR)', 'Opponent']]

            # Create the Altair chart
            chart = alt.Chart(chart_data).mark_bar().encode(
                # Use 'week:O' to treat the week number as an Ordinal (categorical) value
                # This fixes the x-axis to only show weeks with data.
                # We also add a title for the axis.
                x=alt.X('week:O', title='Week', axis=alt.Axis(labelAngle=0)), # labelAngle=0 keeps week numbers horizontal
                
                # Use 'Fantasy Points (PPR):Q' to treat the points as a Quantitative value
                # And add a title for the y-axis.
                y=alt.Y('Fantasy Points (PPR):Q', title='Fantasy Points (PPR)'),
                
                # Add tooltips for interactivity
                tooltip=['week', 'Opponent', 'Fantasy Points (PPR)']
            ).interactive() # Make the chart interactive (zoom/pan)
            
            # Display the chart
            st.altair_chart(chart, use_container_width=True)
            # --- End of Updated Section ---
            
        # --- Dynamic "Player vs Player" section ---
        st.subheader("Player vs. Player Comparison (2023)")
        
        # Add a selectbox for the second player
        # Use index 1 to select the second player in the list as a default
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
                    if 'passing_yards' in p1_stats and p1_stats['passing_yards'] > 0:
                        st.metric("Passing Yards", f"{int(p1_stats['passing_yards'])}")
                    if 'rushing_yards' in p1_stats and p1_stats['rushing_yards'] > 0:
                        st.metric("Rushing Yards", f"{int(p1_stats['rushing_yards'])}")
                    if 'receiving_yards' in p1_stats and p1_stats['receiving_yards'] > 0:
                        st.metric("Receiving Yards", f"{int(p1_stats['receiving_yards'])}")
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
                    if 'passing_yards' in p2_stats and p2_stats['passing_yards'] > 0:
                        st.metric("Passing Yards", f"{int(p2_stats['passing_yards'])}")
                    if 'rushing_yards' in p2_stats and p2_stats['rushing_yards'] > 0:
                        st.metric("Rushing Yards", f"{int(p2_stats['rushing_yards'])}")
                    if 'receiving_yards' in p2_stats and p2_stats['receiving_yards'] > 0:
                        st.metric("Receiving Yards", f"{int(p2_stats['receiving_yards'])}")
                else:
                    st.error(f"No data for {selected_player_2}")
        
        # --- End of Player vs Player section ---

    with col2:
        # Static "Top Fantasy Players" section
        st.subheader("Top Fantasy Players (2023)")
        
        try:
            # Aggregate points by player and get the top 15
            player_points = df.groupby('Player')['TotalFantasyPoints'].sum().nlargest(15).reset_index()
            player_points['TotalFantasyPoints'] = player_points['TotalFantasyPoints'].round(2)
            player_points.index = player_points.index + 1 # Start index at 1
            st.dataframe(player_points, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Could not calculate top players: {e}")

else:
    st.error("Failed to load data. The dashboard cannot be displayed.")
    st.info("Please check the DATA_URL or your internet connection.")

