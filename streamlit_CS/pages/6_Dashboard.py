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
        # The new data source uses 'player_name' and 'fantasy_points_ppr'
        
        if 'player_name' not in data.columns:
            st.error("Data source is missing 'player_name' column. Cannot proceed.")
            return None
            
        if 'fantasy_points_ppr' in data.columns:
            # Rename for simplicity and consistency with old code
            data = data.rename(columns={
                'fantasy_points_ppr': 'TotalFantasyPoints',
                'player_name': 'Player'
            })
        elif 'fantasy_points' in data.columns:
            # Fallback to standard fantasy points
            data = data.rename(columns={
                'fantasy_points': 'TotalFantasyPoints',
                'player_name': 'Player'
            })
        else:
            # Create a very simple fantasy point calculation if none exists
            # This is just a fallback for demonstration
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
            data = data.rename(columns={'player_name': 'Player'})

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
    # This will contain all the widgets from the left side of your mockup
    
    st.sidebar.header("Player Selection")
    # Get a unique, sorted list of player names
    try:
        # Use the 'Player' column (which we renamed from 'player_name')
        players = sorted(df['Player'].unique())
        selected_player = st.sidebar.selectbox("Select a Player", players)
    except Exception as e:
        st.sidebar.error(f"Could not load player list: {e}")
        selected_player = None

    # Player Stats placeholder
    st.sidebar.header("Player Stats")
    if selected_player:
        st.sidebar.markdown(f"Stats for **{selected_player}** will appear here.")
        # (We will build this in Step 2)
        st.sidebar.info("Dynamic player stats card coming in Step 2!")
        
    # Game Schedule placeholder
    st.sidebar.header("Game Schedule")
    st.sidebar.markdown("Full league schedule will go here.")
    # (We can build this in a later step)
    st.sidebar.info("Upcoming game schedule coming soon!")


    # --- Main Content Area ---
    # This will be split into two columns as per your mockup
    col1, col2 = st.columns([2, 1]) # Main area (2/3), Right sidebar (1/3)

    with col1:
        # Dynamic "Stats Today / Upcoming Game" section
        st.subheader("Upcoming Game & Matchup Analysis")
        if selected_player:
            st.markdown(f"Details for **{selected_player}**'s next game.")
            # (We will build this in Step 2)
            st.info("Dynamic matchup details coming in Step 2!")

        # Dynamic "Player vs Player" section
        st.subheader("Player vs. Player / Future Matchups")
        st.info("In-depth matchup analysis will go here.")
        # (This is a more advanced feature for a later step)

    with col2:
        # Static "Top Fantasy Players" section
        st.subheader("Top Fantasy Players (2023)")
        
        try:
            # Aggregate points by player and get the top 15
            # This data is weekly, so summing is the correct approach
            player_points = df.groupby('Player')['TotalFantasyPoints'].sum().nlargest(15).reset_index()
            player_points.index = player_points.index + 1 # Start index at 1
            st.dataframe(player_points, use_container_width=True)
        except Exception as e:
            st.error(f"Could not calculate top players: {e}")

else:
    st.error("Failed to load data. The dashboard cannot be displayed.")
    st.info("Please check the DATA_URL or your internet connection.")

