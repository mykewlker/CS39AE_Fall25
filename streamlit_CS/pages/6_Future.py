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
potential directions I would pursue next.
""")

st.header("1. TBD: [Future Work Idea 1]")
st.info("ℹ️ **Placeholder:** The body of this section is to be determined (TBD).")

st.header("2. TBD: [Future Work Idea 2]")
st.info("ℹ️ **Placeholder:** The body of this section is to be determined (TBD).")

st.divider()

st.subheader("My Suggestions for Future Work:")
st.markdown("""
Here are a couple of ideas I would be excited to explore:

* **1. Sentiment Analysis on User Reviews:**
    The dataset includes a `reviews` column (which is 'Mixed' or 'Positive' in the sample). 
    If we were to pull the *actual text* of user reviews using the Steam API, 
    we could apply Natural Language Processing (NLP) to perform sentiment analysis. 
    This would allow us to move beyond a simple 'positive' or 'negative' score 
    and identify *why* players like or dislike a game (e.g., "great story," 
    "buggy," "fun with friends").

* **2. Predictive Modeling for Game Success:**
    Using the full, larger dataset, we could build a machine learning model 
    to predict a game's "success." We could define success as its 
    `estimated_owners` or `Positive Review %`. Features for the model 
    could include `price`, `genre`, `dlc_count`, and whether it's 
    `Single-player` or `Multi-player`. This could help publishers understand 
    what factors are most predictive of a successful launch.
""")
