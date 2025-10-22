import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Weather Tracker",
    page_icon="ð©ï¸"
)

st.title("ð©ï¸ Weather Forecast")
st.write("This page shows the hourly temperature and wind speed forecast for Denver, CO.")

# --- API Setup (Denver) ---
lat, lon = 39.7392, -104.9903  # Denver

# We modify the URL to get the HOURLY forecast, not just the CURRENT weather.
# This gives us the "over time" data needed for a chart.
# 'forecast_days=3' will give us 3 days of hourly data.
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,wind_speed_10m&forecast_days=3"


# --- Data Fetching Function ---
@st.cache_data(ttl=600)  # Cache data for 10 minutes (600 seconds)
def get_weather():
    """
    Fetches hourly weather forecast data from Open-Meteo.
    """
    try:
        r = requests.get(wurl, timeout=10)
        # Raise an exception if the request was unsuccessful
        r.raise_for_status() 
        
        # Parse the JSON response
        data = r.json()["hourly"]
        
        # Convert the 'hourly' data (which is a dictionary of lists) into a DataFrame
        df = pd.DataFrame(data)
        
        # Convert the 'time' column to datetime objects for proper plotting
        df['time'] = pd.to_datetime(df['time'])
        
        # Rename columns for clearer labels in charts
        df.rename(columns={
            'temperature_2m': 'Temperature (Â°C)',
            'wind_speed_10m': 'Wind Speed (km/h)'
        }, inplace=True)
                
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except KeyError:
        st.error("Received unexpected data format from API.")
        return pd.DataFrame() # Return empty on format error

# --- Main Application ---
st.header(f"Forecast for Denver, CO (Next 3 Days)")

# Get the weather data (either from cache or API)
weather_df = get_weather()

# Check if the DataFrame is not empty (i.e., data was fetched successfully)
if not weather_df.empty:
    
    # --- Display Current Conditions (from the first row of the forecast) ---
    st.subheader("Current Conditions (approx.)")
    col1, col2 = st.columns(2)
    
    # Get the first row of data
    current_temp = weather_df.iloc[0]['Temperature (Â°C)']
    current_wind = weather_df.iloc[0]['Wind Speed (km/h)']
    
    col1.metric("Temperature", f"{current_temp} Â°C")
    col2.metric("Wind Speed", f"{current_wind} km/h")

    # --- Create the Temperature Line Chart ---
    st.subheader("Hourly Temperature Forecast")
    
    # Use Plotly Express for a nice, interactive line chart
    fig_temp = px.line(
        weather_df,
        x='time',
        y='Temperature (Â°C)',
        title='Temperature Over Time',
        markers=True  # Add markers to each data point
    )
    fig_temp.update_layout(xaxis_title="Time", yaxis_title="Temperature (Â°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    # --- Create the Wind Speed Area Chart ---
    st.subheader("Hourly Wind Speed Forecast")
    
    # Use an area chart for wind speed
    fig_wind = px.area(
        weather_df,
        x='time',
        y='Wind Speed (km/h)',
        title='Wind Speed Over Time'
    )
    fig_wind.update_layout(xaxis_title="Time", yaxis_title="Wind Speed (km/h)")
    st.plotly_chart(fig_wind, use_container_width=True)

    # --- Show Raw Data in an Expander ---
    with st.expander("Show Raw Forecast Data"):
        st.dataframe(weather_df)

else:
    # This message will show if the get_weather() function failed
    st.warning("Could not retrieve weather data. Please try again later.")

# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")

# Let user choose how often to refresh (in seconds)
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)

# Toggle to turn automatic refreshing on/off
auto_refresh = st.toggle("Enable auto-refresh", value=False)

# Show current refresh time
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")
