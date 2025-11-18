import streamlit as st
import pandas as pd
import ast
import os
import datetime 

# --- Page Configuration ---
# This must be the first Streamlit command
st.set_page_config(
    page_title="Data Analyst Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Data Loading and Caching ---
@st.cache_data  # Cache the data to avoid reloading
def load_data(filepath):
    """
    Loads and pre-processes the Steam games data from a given filepath.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        # This error will show on the Streamlit page if the file isn't found
        st.error(f"Error: The data file was not found at the expected path: '{filepath}'.")
        st.info("Please ensure you have a 'data' folder in your repository, and 'sample.csv' is placed inside it.")
        return pd.DataFrame() # Return an empty DataFrame on failure

    # --- Data Pre-processing (inside the load function) ---
    
    # Fill NaNs in list-like columns with a string of an empty list
    df['categories'] = df['categories'].fillna('[]')
    df['genres'] = df['genres'].fillna('[]')
    
    # Fill NaNs in other key columns
    df['estimated_owners'] = df['estimated_owners'].fillna('0 - 0')
    
    # --- FIXES: Convert to numeric and fill NaN/coerce errors ---
    for col in ['metacritic_score', 'pct_pos_total', 'num_reviews_total', 'average_playtime_forever', 'price']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # --- FIX: Platform Columns ---
    # Ensure windows, mac, linux are numeric (0 or 1) to allow summing.
    for col in ['windows', 'mac', 'linux']:
        if col in df.columns:
            val_map = {'True': 1, 'true': 1, 'False': 0, 'false': 0}
            df[col] = df[col].astype(str).map(val_map).fillna(0).astype(int)
    # --- END FIXES ---
    
    # --- Helper Functions for Parsing ---
    
    def safe_literal_eval(s):
        """Safely evaluate a string representation of a list."""
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError, TypeError):
            return []  # Return an empty list on failure

    def classify_game_type(cat_list):
        """Classify game as Single-player, Multi-player, or both."""
        if not isinstance(cat_list, list):
             cat_list = [] # Ensure it's a list
        in_cat = set(cat_list)
        is_single = 'Single-player' in in_cat
        is_multi = 'Multi-player' in in_cat
        
        if is_single and is_multi:
            return 'Single-player & Multi-player'
        elif is_single:
            return 'Single-player Only'
        elif is_multi:
            return 'Multi-player Only'
        else:
            return 'Other/Unknown'

    def parse_owners(owners_string):
        """Get the lower bound of estimated owners."""
        try:
            lower_bound_str = str(owners_string).split(' - ')[0].replace(',', '')
            return int(lower_bound_str)
        except:
            return 0

    # --- Apply Pre-processing ---
    
    # Parse list-like strings
    df['categories_list'] = df['categories'].apply(safe_literal_eval)
    df['genres_list'] = df['genres'].apply(safe_literal_eval)
    
    # Classify game type
    df['game_type'] = df['categories_list'].apply(classify_game_type)
    
    # Parse owners
    df['owners_lower_bound'] = df['estimated_owners'].apply(parse_owners)
    
    # Create a 'Positive Review %' for clarity
    df['Positive Review %'] = df['pct_pos_total']

    return df

# --- Main App Execution ---

# ** THE FIX: Build a robust, absolute file path **
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample.csv')

# Load the data using the robust path
df = load_data(DATA_PATH)

# Store the loaded data in Streamlit's session state
if not df.empty:
    st.session_state['df'] = df
    
    # --- Get file modification time for 'last refreshed' timestamp ---
    try:
        mod_time_timestamp = os.path.getmtime(DATA_PATH)
        mod_time = datetime.datetime.fromtimestamp(mod_time_timestamp).strftime("%Y-%m-%d %H:%M %Z")
        st.session_state['data_last_refreshed'] = mod_time
    except FileNotFoundError:
        st.session_state['data_last_refreshed'] = "N/A (File not found)"
else:
    st.session_state['df'] = pd.DataFrame()


# --- Home Page Content (Aesthetic Update) ---
st.markdown(
    """
    # 📊 Data Analyst Portfolio: Steam Games Analysis 🎮
    ---
    """
)

col_img, col_text = st.columns([1, 2.5])

with col_img:
    st.image(
        "https://placehold.co/400x250/2E86C1/FFFFFF?text=Controller\nImage", 
        caption="Analyzing the Gaming Market",
        use_column_width=True
    )

with col_text:
    st.header("Welcome!")
    st.markdown("""
    This application serves as a **professional portfolio** and an interactive **mini analytics product**. 
    
    It showcases my ability to clean raw data, perform exploratory analysis, and deploy 
    interactive dashboards using Python, Pandas, and Streamlit. The analysis focuses 
    on the relationships between price, user reception, playtime, and game category 
    across the vast Steam game library.
    
    Use the sidebar to navigate to my **Professional Bio**, the **EDA Gallery**, or the 
    live **Interactive Dashboard** to explore the dataset yourself.
    """)

st.divider()

# --- NEW SECTION: Quick Data Highlights ---
st.header("Quick Data Highlights")

if not df.empty:
    # Calculate metrics for the highlights
    total_games = len(df)
    max_price = df['price'].max()
    avg_metacritic = df[df['metacritic_score'] > 0]['metacritic_score'].mean()
    total_owners = df['owners_lower_bound'].sum()
    
    # Get the single most common genre
    try:
        # Explode list of genres, count, and get the mode (most frequent)
        common_genre = df.explode('genres_list')['genres_list'].mode()[0]
    except Exception:
        common_genre = "Action" # Default fallback
    
    highlight_col1, highlight_col2, highlight_col3, highlight_col4 = st.columns(4)
    
    with highlight_col1:
        st.metric(label="Total Games Analyzed", value=f"{total_games:,}")
    
    with highlight_col2:
        st.metric(label="Maximum Game Price", value=f"${max_price:,.2f}")
    
    with highlight_col3:
        st.metric(label="Total Estimated Owners (Lower)", value=f"{total_owners:,}")

    with highlight_col4:
        st.metric(label="Most Common Genre", value=common_genre)
else:
    st.warning("Data highlights are unavailable because the 'sample.csv' file failed to load.")

st.divider()

# --- NEW SECTION: Technology Stack ---
st.header("Technology Stack")

st.markdown(
    """
    This project was built from the ground up using the following tools, demonstrating proficiency 
    in core data science and application development principles:
    
    * **Python:** The core programming language for the entire application.
    * **Pandas:** Used exclusively for **data ingestion, cleaning, transformation, and feature engineering** (e.g., parsing genres, calculating playtime-per-dollar).
    * **Altair:** Utilized for all **data visualizations** across the EDA Gallery and Dashboard, ensuring interactive and responsive charts.
    * **Streamlit:** The framework used to **deploy the application**, manage the multi-page structure, and create all interactive widgets (sliders, multiselects).
    """
)

st.divider()

# Final status box
st.header("Project Status")
if df.empty:
    st.error("Data loading failed. See error message above. The other pages will not work until this is resolved.")
else:
    last_refreshed_time = st.session_state.get('data_last_refreshed', 'N/A')
    st.success(f"✅ Data for {len(df)} games loaded successfully! (Last Refreshed: {last_refreshed_time}) You can now explore the other pages.")
