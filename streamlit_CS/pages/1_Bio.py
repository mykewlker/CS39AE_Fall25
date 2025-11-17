import streamlit as st

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Myke Walker"
PROGRAM = "Computer Science Major"
INTRO = (
    "I am a data nerd that is looking to analyze, access, and anonymize data structures.  "
    "I believe in data privacy and preservation so that we can be a more educated world"
)
FUN_FACTS = [
    "I love video games",
    "I’m learning to program better data structures",
    "I want to build a personalized large language model",
]
PHOTO_PATH = "https://www.shutterstock.com/shutterstock/photos/98021261/display_1500/stock-vector-afro-smiley-face-98021261.jpg"  # Put a file in repo root or set a URL

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    try:
        st.image(PHOTO_PATH, caption=NAME, use_container_width=True)
    except Exception:
        st.info("Add a photo named `your_photo.jpg` to the repo root, or change PHOTO_PATH.")
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)
    st.write("""
    Welcome to my professional portfolio and analytics dashboard! 
    
    I am a data-driven problem solver with a passion for uncovering insights 
    and turning complex data into actionable stories. With experience in Python, 
    SQL, and data visualization, I specialize in exploratory data analysis (EDA) 
    and building interactive dashboards that empower decision-making.
    
    This application is a demonstration of my skills, built entirely in Python 
    using Streamlit. Please explore the EDA Gallery for an analysis of a 
    Steam games dataset, or check out the interactive dashboard.
    """)
st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
