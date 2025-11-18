import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Future Works",
    page_icon="🚀",
    layout="wide",
)

st.title("Future Works")

st.markdown("""
This project provides a strong foundation for further analysis. Below are two 
potential directions I would pursue next to expand this dashboard into a more 
comprehensive analytics tool.
""")

# --- Project 1: Sentiment Analysis ---
st.header("1. Sentiment Analysis on User Reviews")
st.markdown("""
**The Concept:**
Currently, the dataset categorizes reviews simply as 'Mixed', 'Positive', or 'Negative'. 
By accessing the *actual text* of user reviews (potentially via the Steam API), we could 
unlock a deeper layer of insight using Natural Language Processing (NLP).

**Implementation Plan:**
* **Data Collection:** Scrape or query the Steam API to get the text body of the top 100 reviews for each game.
* **NLP Processing:** Use libraries like `NLTK` or `spaCy` to perform sentiment scoring and keyword extraction.
* **Visualization:** Create word clouds for specific games (e.g., "Why do people love *Elden Ring*?") and analyze sentiment trends over time (e.g., did a patch fix the negative reviews?).

**Value Add:**
This would allow developers to identify *specific* pain points (e.g., "buggy," "lag," "crash") 
versus content complaints, rather than just seeing a raw score.
""")

st.divider()

# --- Project 2: Predictive Modeling ---
st.header("2. Predictive Modeling for Game Success")
st.markdown("""
**The Concept:**
Using the historical data in this dataset, we could build a machine learning model to 
predict the potential success of a future game based on its pre-launch characteristics.

**Implementation Plan:**
* **Feature Engineering:** Select key features such as `genre`, `price`, `developer history`, `tags`, and `support for controllers`.
* **Target Variable:** Define "success" as reaching a certain threshold of `estimated_owners` or achieving a `Positive Review %` above 80%.
* **Modeling:** Train a classification model (like Random Forest or XGBoost) to predict the probability of success.

**Value Add:**
This tool could help indie developers benchmark their game ideas. For example, a user could input: 
*"I'm making a $20 Puzzle-Platformer for Mac and PC,"* and the model could output the historical probability of that specific combination succeeding.
""")
