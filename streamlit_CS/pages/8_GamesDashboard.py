import streamlit as st
import pandas as pd
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="Interactive Dashboard",
    page_icon="🎮",
    layout="wide",
)

# --- Load Data from Session State ---
# Retrieve the pre-loaded dataframe from the main app.py page
df = st.session_state.get('df')

if df is None or df.empty:
    st.error("Data not loaded. Please go to the main 'Home' page to load the data first.")
    st.info("If you are on the 'Home' page and see this, please ensure the `data/sample.csv` file exists in your repository.")
    st.stop()

# --- Page Title ---
st.title("Interactive Game Dashboard")
st.markdown("Filter and explore the game data using the options in the sidebar.")

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

# Get unique values for filters
all_genres = sorted(list(df.explode('genres_list')['genres_list'].dropna().unique()))
all_game_types = sorted(list(df['game_type'].dropna().unique()))

# 1. Genre Filter
selected_genres = st.sidebar.multiselect(
    'Filter by Genre:',
    options=all_genres,
    default=[]  # Start with no genres selected
)

# 2. Price Filter
max_price = int(df['price'].max())
price_range = st.sidebar.slider(
    'Filter by Price Range:',
    min_value=0,
    max_value=max_price,
    value=(0, max_price)
)

# 3. Metacritic Score Filter
score_range = st.sidebar.slider(
    'Filter by Metacritic Score:',
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# 4. Minimum Number of Reviews Filter
max_reviews = int(df['num_reviews_total'].max())
min_reviews = st.sidebar.slider(
    'Minimum Number of Reviews:',
    min_value=0,
    max_value=max_reviews,
    value=100  # Default to a minimum of 100 reviews
)

# 5. Game Type Filter
selected_game_types = st.sidebar.multiselect(
    'Filter by Game Type:',
    options=all_game_types,
    default=all_game_types  # Default to all game types
)

# 6. Sort By
sort_by_options = {
    'Positive Review %': 'Positive Review %',
    'Metacritic Score': 'metacritic_score',
    'Estimated Owners (Lower)': 'owners_lower_bound',
    'Price': 'price',
    'Number of Reviews': 'num_reviews_total'
}
sort_by = st.sidebar.selectbox(
    'Sort By:',
    options=list(sort_by_options.keys()),
    index=0
)

# 7. Sort Order
sort_order = st.sidebar.radio(
    'Sort Order:',
    options=['Descending', 'Ascending'],
    index=0
)
sort_ascending = (sort_order == 'Ascending')

# --- Filtering Logic ---
filtered_df = df.copy()

# Apply filters
filtered_df = filtered_df[
    (filtered_df['price'] >= price_range[0]) &
    (filtered_df['price'] <= price_range[1]) &
    (filtered_df['metacritic_score'] >= score_range[0]) &
    (filtered_df['metacritic_score'] <= score_range[1]) &
    (filtered_df['num_reviews_total'] >= min_reviews)
]

if selected_game_types:
    filtered_df = filtered_df[filtered_df['game_type'].isin(selected_game_types)]

if selected_genres:
    filtered_df = filtered_df[
        filtered_df['genres_list'].apply(lambda genres: any(g in genres for g in selected_genres))
    ]

# --- Sorting Logic ---
sort_column = sort_by_options[sort_by]
filtered_df = filtered_df.sort_values(by=sort_column, ascending=sort_ascending)

# --- Main Page Layout ---

# Top Row: Key Metrics
st.divider()
st.header("Filtered Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Games", value=len(filtered_df))

with col2:
    # Avoid division by zero if no games are selected
    avg_price = filtered_df['price'].mean() if len(filtered_df) > 0 else 0
    st.metric(label="Average Price", value=f"${avg_price:,.2f}")

with col3:
    # Filter out games with 0 Metacritic score for this metric
    valid_metacritic_df = filtered_df[filtered_df['metacritic_score'] > 0]
    avg_metacritic = valid_metacritic_df['metacritic_score'].mean() if len(valid_metacritic_df) > 0 else 0
    st.metric(label="Average Metacritic", value=f"{avg_metacritic:,.0f}")

with col4:
    total_owners = filtered_df['owners_lower_bound'].sum()
    st.metric(label="Total Owners (Lower Bound)", value=f"{total_owners:,}")

# Middle Row: Charts
st.divider()
st.header("Top 10 Games")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader(f"Top 10 by Positive Review %")
    # Get top 10 for this chart
    top_10_reviews_df = filtered_df.nlargest(10, 'Positive Review %')
    
    chart1 = alt.Chart(top_10_reviews_df).mark_bar().encode(
        x=alt.X('Positive Review %:Q'),
        y=alt.Y('name:N', sort='-x'),
        tooltip=['name', 'Positive Review %', 'num_reviews_total']
    ).interactive()
    st.altair_chart(chart1, use_container_width=True)

with chart_col2:
    st.subheader(f"Top 10 by Estimated Owners")
    # Get top 10 for this chart
    top_10_owners_df = filtered_df.nlargest(10, 'owners_lower_bound')
    
    chart2 = alt.Chart(top_10_owners_df).mark_bar().encode(
        x=alt.X('owners_lower_bound:Q', title='Estimated Owners (Lower)'),
        y=alt.Y('name:N', sort='-x'),
        tooltip=['name', 'owners_lower_bound', 'price']
    ).interactive()
    st.altair_chart(chart2, use_container_width=True)

# --- NEW: Narrative & Insights Section ---
st.divider()
st.header("Narrative & Insights")
st.markdown("""
Based on the filtered data and the charts, here are a few key insights:

* **High-Quality Games are Price-Agnostic:** You can find highly-rated games (90%+ positive reviews) at all price points, from under $10 to $60+. Use the "Positive Review %" filter to find them.
* **"Both" is Better:** Games offering both "Single-player & Multi-player" modes consistently show the highest average number of estimated owners in the full dataset.
* **Reviews vs. Critics:** User reviews (`Positive Review %`) and critic scores (`Metacritic Score`) don't always agree. You can use the filters to find "hidden gems" (high user score, low critic score).
* **Limitations:** This dashboard is based on a **static 2000-game sample**. As such, "Total Owners" is an estimate, and trends (especially for "Top 10" charts) may differ significantly when applied to the full, live dataset.
""")
# --- END NEW ---

# Bottom Section: Data Table
st.divider()
st.header(f"Filtered Game Data ({len(filtered_df)} results)")

# Define columns to display
display_columns = [
    'name',
    'price',
    'Positive Review %',
    'metacritic_score',
    'owners_lower_bound',
    'num_reviews_total',
    'game_type',
    'genres'
]
st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)

# --- NEW: Reproducibility Section ---
st.divider()
st.markdown(
    """
    **Data Source:** [Kaggle (Steam Games Dataset)](https://www.kaggle.com/datasets/artermiloff/steam-games-dataset/data)
    """
)
# Get the timestamp from session state
last_refreshed = st.session_state.get('data_last_refreshed', 'N/A')
st.caption(f"Data last refreshed: {last_refreshed}")
# --- END NEW ---
