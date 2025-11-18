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

st.header("1. [Expand on current system]")
st.info(""""
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
"""")

st.header("2. [Relations in reviews]")
st.info("I would love to do a deeper dive on the words used in each review, 
along with the sentiment review above, This could provide valuable insight on the thoughts and ideas present in reviews")

st.divider()


