import streamlit as st
import pandas as pd
import ast
import os  # <-- This is the key import for the fix

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
    df['metacritic_score'] = df['metacritic_score'].fillna(0)
    df['pct_pos_total'] = df['pct_pos_total'].fillna(0)
    df['num_reviews_total'] = df['num_reviews_total'].fillna(0)
    
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
# This gets the directory where this script (app.py) is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This joins that directory path with 'data' and 'sample.csv'
DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample.csv')

# Load the data using the robust path
df = load_data(DATA_PATH)

# Store the loaded data in Streamlit's session state
# This allows all other pages (in the 'pages' folder) to access the same data
if not df.empty:
    st.session_state['df'] = df
else:
    # If loading failed, store an empty DF to prevent KeyErrors on other pages
    st.session_state['df'] = pd.DataFrame()


# --- Home Page Content ---
st.title("Welcome to my Data Analytics Portfolio!")
st.image("https://placehold.co/1200x300/3498db/ffffff?text=Welcome+to+my+Portfolio", use_column_width=True)

st.header("About This Project")
st.markdown("""
This application is a multi-page Streamlit dashboard built to showcase my data analysis 
and visualization skills. It serves as both my professional portfolio and an interactive 
analytics product based on a **Steam Games Dataset**.

**What you can do here:**

* **Professional Bio:** Learn more about my background and skills.
* **EDA Gallery:** View a static exploratory data analysis of the Steam dataset, 
    complete with chart explainers and my key observations.
* **Interactive Dashboard:** (Work in Progress) An interactive dashboard to filter 
    and explore the game data yourself.
* **Future Works:** Read about the potential next steps for this project.

Please use the navigation on the left to explore the different pages.
""")

st.info("This app and all its pages are built using **Streamlit**. The data is loaded 
and processed with **Pandas**, and the visualizations are created with **Altair**.")

# Add a status box to the home page for easy debugging
if df.empty:
    st.error("Data loading failed. See error message above. The other pages will not work until this is resolved.")
else:
    st.success(f"Data for {len(df)} games loaded successfully! You can now explore the other pages.")
