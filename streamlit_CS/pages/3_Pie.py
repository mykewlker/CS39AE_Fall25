import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Pie Chart Demo",
    page_icon="ð "
)

st.title("ð  Pie Chart Page")
st.write("This page reads data from `data/pie_demo.csv` and displays it as a pie chart.")

# --- Define Data Path ---
# This relative path works whether the script is in the root or in a 'pages' folder,
# as long as the 'data' folder is in the root.
DATA_FILE_PATH = "streamlit_CS/data/pie_demo.csv"

# --- Load and Display Data ---
try:
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(DATA_FILE_PATH)

    st.header("Raw Data from CSV")
    st.dataframe(df)

    # --- Create and Display Pie Chart ---
    st.header("Data Distribution")

    # Check if the required columns exist
    if 'Category' in df.columns and 'Value' in df.columns:
        # Create a Plotly Express pie chart
        fig = px.pie(
            df,
            values='Value',
            names='Category',
            title='Distribution of Categories'
        )
        
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("The CSV file must have 'Category' and 'Value' columns to plot the pie chart.")

except FileNotFoundError:
    st.error(f"Error: The data file was not found.")
    st.info(f"""
        Please make sure a folder named `data` exists in your project's root directory,
        and it contains a file named `pie_demo.csv`.

        **Example `data/pie_demo.csv` content:**
        ```csv
        Category,Value
        Item A,30
        Item B,25
        Item C,15
        Item D,20
        Item E,10
        ```
    """)
except Exception as e:
    st.error(f"An error occurred while loading or processing the data: {e}")

