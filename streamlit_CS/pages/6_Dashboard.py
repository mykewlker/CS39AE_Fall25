import streamlit as st
import pandas as pd

# --- Page Setup ---
# Set the page configuration to be wide
st.set_page_config(layout="wide")

# --- Data Loading ---
# NEW, more reliable URL from the nflverse *releases* page
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

# Load the data
df = load_data(DATA_URL)

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
    if selected_player:
        # Filter the dataframe for the selected player
        player_data = df[df['Player'] == selected_player]
        
        if not player_data.empty:
            # Get season totals by summing all weekly stats
            season_stats = player_data.sum(numeric_only=True)
            
            # Get non-numeric info from the first available week
            position = player_data['Position'].iloc[0]
            team = player_data['Team'].iloc[0]
            
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
        
    # Game Schedule placeholder
    st.sidebar.header("Game Schedule")
    st.sidebar.info("Full league schedule coming in a future step!")


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
            
            # --- ADDED: Weekly Points Bar Chart ---
            st.subheader("Weekly Points Chart")
            # We already have the data in weekly_display_df, let's just plot the points
            # We select just the column we want to plot. The index ('week') is used for the x-axis.
            st.bar_chart(weekly_display_df['Fantasy Points (PPR)'])
            # --- End of Added Section ---
            
        # Dynamic "Player vs Player" section
        st.subheader("Player vs. Player / Future Matchups")
        st.info("In-depth matchup analysis will go here.")
        # (This is a more advanced feature for a later step)

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

