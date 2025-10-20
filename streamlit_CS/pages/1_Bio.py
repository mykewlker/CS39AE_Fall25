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

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
