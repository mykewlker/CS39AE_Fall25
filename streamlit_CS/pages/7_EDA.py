import streamlit as st
import pandas as pd
import altair as alt
import ast

# Page Configuration
st.set_page_config(
    page_title="EDA Gallery",
    page_icon="📊",
    layout="wide",
)

st.title("EDA Gallery: Steam Games Dataset")

# --- Load Data from Session State ---
# Retrieve the pre-loaded dataframe from the main app.py page
df = st.session_state.get('df')

if df is None or df.empty:
    st.error("Data not loaded. Please go to the main 'Home' page to load the data first.")
    st.info("If you are on the 'Home' page and see this, please ensure the `data/sample.csv` file exists in your repository.")
    st.stop()

# --- Page Content ---
st.markdown("""
This gallery contains an exploratory data analysis (EDA) of a sample dataset 
of 100 Steam games. Each section includes a question, a visualization 
to answer it, an explainer on how to read the chart, and my observations.
""")

# --- Chart 1: Price vs. Reception (Scatter Plot) ---
st.divider()
st.header("Chart 1: Price vs. User Reception")

st.subheader("The Question")
st.write("Is there a relationship between a game’s price and its reception? Does a higher price mean a better-rated game?")

st.subheader("How to Read This Chart")
st.markdown("""
This is a **scatter plot**.
* **X-axis (Horizontal):** Represents the game's `Price (USD)`.
* **Y-axis (Vertical):** Represents the `Positive User Review %`.
* **Each Dot:** Represents a single game.
* **Red Line (Trendline):** Shows the general trend. A flat line means little to no relationship, 
    an upward slope means positive correlation (higher price = higher reviews), and 
    a downward slope means negative correlation.
""")

# Prepare data for this chart
chart1_df = df[(df['price'] > 0) & (df['Positive Review %'] > 0)].copy()

if not chart1_df.empty:
    # Create the chart
    base = alt.Chart(chart1_df).mark_circle(opacity=0.7).encode(
        x=alt.X('price', title='Price (USD)'),
        y=alt.Y('Positive Review %', title='Positive User Review %', scale=alt.Scale(zero=False)),
        tooltip=['name', 'price', 'Positive Review %']
    ).interactive()
    
    # Add regression line
    regression_line = base.transform_regression(
        'price', 'Positive Review %'
    ).mark_line(color='red')
    
    st.altair_chart(base + regression_line, use_container_width=True)
else:
    st.warning("No data available to display this chart (e.g., no paid games with reviews in the sample).")

st.subheader("My Observations")
st.markdown("""
The trendline is almost perfectly flat. This suggests that **there is little to no correlation 
between a game's price and its user reception.** We can see highly-rated (90%+) and poorly-rated games at all price points, from under $20 
to the full $60. This indicates that price is not a reliable predictor of a game's quality, 
according to user reviews.
""")

# --- Chart 2: 'Hidden Gems' - Critic vs. User Scores (Scatter Plot) ---
st.divider()
st.header("Chart 2: 'Hidden Gems' - Critic vs. User Scores")

st.subheader("The Question")
st.write("What are some 'hidden gem' games that were critically panned but loved by users?")

st.subheader("How to Read This Chart")
st.markdown("""
This is another **scatter plot**, used here for quadrant analysis.
* **X-axis (Horizontal):** The `Metacritic Score` (from 0 to 100).
* **Y-axis (Vertical):** The `Positive User Review %`.
* **Red Lines:** These divide the chart into four quadrants.
    * **Top-Right:** High Critic Score, High User Score (Critically Acclaimed Hits)
    * **Bottom-Right:** High Critic Score, Low User Score (Critically Overrated?)
    * **Bottom-Left:** Low Critic Score, Low User Score (Universally Panned)
    * **Top-Left:** Low Critic Score, High User Score (The "Hidden Gems")
""")

# Prepare data for this chart
chart2_df = df[
    (df['metacritic_score'] > 0) & 
    (df['Positive Review %'] > 0) &
    (df['num_reviews_total'] > 100) # Filter for games with at least 100 reviews
].copy()

if not chart2_df.empty:
    # Base scatter plot
    scatter = alt.Chart(chart2_df).mark_circle(size=80, opacity=0.8).encode(
        x=alt.X('metacritic_score', title='Metacritic Score', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('Positive Review %', title='Positive User Review %', scale=alt.Scale(domain=[0, 100])),
        tooltip=['name', 'metacritic_score', 'Positive Review %', 'num_reviews_total']
    ).interactive()
    
    # Add quadrant lines
    vertical_line = alt.Chart(pd.DataFrame({'x': [60]})).mark_rule(color='red', strokeDash=[5,5]).encode(x='x')
    horizontal_line = alt.Chart(pd.DataFrame({'y': [80]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y')
    
    st.altair_chart(scatter + vertical_line + horizontal_line, use_container_width=True)
else:
    st.warning("No data available to display this chart (e.g., no games with both critic and user scores).")

st.subheader("My Observations")
st.markdown("""
Using this chart, we can specifically hunt for games in the **top-left quadrant** (Metacritic < 60, User Reviews > 80%). 

In this small sample, there aren't many clear examples, but any dot appearing in that quadrant would be 
a prime candidate for a "hidden gem" — a game that professional critics disliked, but 
the player base thoroughly enjoyed.
""")

# --- Chart 3: Average Owners by Game Type (Bar Chart) ---
st.divider()
st.header("Chart 3: Average Owners by Game Type")

st.subheader("The Question")
st.write("Do multiplayer games sell better (i.e., have more owners) than single-player games?")

st.subheader("How to Read This Chart")
st.markdown("""
This is a **bar chart**.
* **X-axis (Horizontal):** Shows the game categories we defined: 'Single-player Only', 
    'Multi-player Only', 'Single-player & Multi-player', and 'Other/Unknown'.
* **Y-axis (Vertical):** Represents the `Average Estimated Owners (Lower Bound)`.
* **Bar Height:** A taller bar means a higher average number of owners for that category.
""")

# Prepare data for this chart
chart3_df = df.groupby('game_type')['owners_lower_bound'].mean().reset_index()

if not chart3_df.empty:
    # Create the chart
    chart3 = alt.Chart(chart3_df).mark_bar().encode(
        x=alt.X('game_type', title='Game Type', sort='-y'),
        y=alt.Y('owners_lower_bound', title='Average Estimated Owners (Lower Bound)'),
        tooltip=['game_type', 'owners_lower_bound']
    ).properties(
        title='Average Estimated Owners by Game Type'
    )
    st.altair_chart(chart3, use_container_width=True)
else:
    st.warning("No data available to display this chart.")

st.subheader("My Observations")
st.markdown("""
Based on this sample, games that feature **both Single-player & Multi-player** modes have the highest average number of owners, by a significant margin.

'Single-player Only' games come in second. This suggests that while single-player 
games are very popular, the most successful games (by ownership) tend to 
offer content for both types of players.
""")

# --- Chart 4: Value Proposition by Genre (Bar Chart) ---
st.divider()
st.header("Chart 4: Value Proposition by Genre")

st.subheader("The Question")
st.write("What is the 'value proposition' of different genres? (i.e., which genres give the most playtime per dollar?)")

st.subheader("How to Read This Chart")
st.markdown("""
This is another **bar chart**.
* **X-axis (Horizontal):** Shows the different game genres.
* **Y-axis (Vertical):** Represents the `Average Playtime (Minutes) per Dollar`.
* **Bar Height:** A taller bar means a better value, indicating more average minutes 
    of playtime for every dollar spent on games in that genre.
""")

# Prepare data for this chart
# 1. Explode the 'genres_list'
df_exploded = df.explode('genres_list')
df_exploded = df_exploded.rename(columns={'genres_list': 'Genre'})

# 2. Filter for paid games and valid genres
paid_exploded = df_exploded[
    (df_exploded['price'] > 0) & 
    (df_exploded['Genre'].notna()) &
    (df_exploded['Genre'] != 'Free To Play')
].copy()

# 3. Calculate 'Playtime (Minutes) per Dollar'
paid_exploded['Playtime (Minutes) per Dollar'] = paid_exploded['average_playtime_forever'] / paid_exploded['price']

# 4. Group by Genre
chart4_df = paid_exploded.groupby('Genre')['Playtime (Minutes) per Dollar'].mean().reset_index()
chart4_df = chart4_df.sort_values(by='Playtime (Minutes) per Dollar', ascending=False)

if not chart4_df.empty:
    # Create the chart
    chart4 = alt.Chart(chart4_df.head(15)).mark_bar().encode(
        x=alt.X('Genre', sort=None, title='Game Genre'), # Use 'sort=None' because it's pre-sorted
        y=alt.Y('Playtime (Minutes) per Dollar', title='Average Playtime (Minutes) per Dollar'),
        tooltip=['Genre', 'Playtime (Minutes) per Dollar']
    ).properties(
        title='Value Proposition: Playtime per Dollar (Top 15 Genres)'
    )
    st.altair_chart(chart4, use_container_width=True)
else:
    st.warning("No data available to display this chart (e.g., no paid games with genres and playtime).")

st.subheader("My Observations")
st.markdown("""
This chart highlights which genres offer the most "bang for your buck." 

In our sample, **'Massively Multiplayer' (MMO)** and **'RPG' (Role-Playing Game)** genres are clear winners, offering a very high number of average playtime minutes 
for every dollar spent. This makes sense, as these genres are known for 
long-running content and high replayability.
""")
