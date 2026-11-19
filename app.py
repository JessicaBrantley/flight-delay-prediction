import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "models" / "flight_delay_model.joblib"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

st.title("✈️ Flight Delay Predictor")

st.write(
    "Predict whether a flight is likely to arrive "
    "15 minutes or more behind schedule."
)

st.info(
    "This project uses historical flight data from June 2026. "
    "Predictions are experimental and do not use live flight conditions."
)

st.success("Machine learning model loaded successfully!")

st.subheader("Flight Information")

airlines = {
    "American Airlines": "AA",
    "Alaska Airlines": "AS",
    "JetBlue Airways": "B6",
    "Delta Air Lines": "DL",
    "Frontier Airlines": "F9",
    "Allegiant Air": "G4",
    "United Airlines": "UA",
    "Southwest Airlines": "WN"
}

selected_airline = st.selectbox(
    "Select an airline",
    list(airlines.keys())
)

days = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7
}

selected_day = st.selectbox(
    "Day of the week",
    list(days.keys())
)

airports = {
    "Atlanta (ATL)": "ATL",
    "Charlotte (CLT)": "CLT",
    "Dallas/Fort Worth (DFW)": "DFW",
    "Denver (DEN)": "DEN",
    "Houston (IAH)": "IAH",
    "Las Vegas (LAS)": "LAS",
    "Los Angeles (LAX)": "LAX",
    "Chicago O'Hare (ORD)": "ORD",
    "Phoenix (PHX)": "PHX",
    "Seattle (SEA)": "SEA"
}

origin = st.selectbox(
    "Departure airport",
    list(airports.keys())
)

destination = st.selectbox(
    "Arrival airport",
    list(airports.keys()),
    index=1
)

departure_hour = st.slider(
    "Scheduled departure hour",
    min_value=0,
    max_value=23,
    value=12,
    format="%d:00"
)

flight_duration = st.number_input(
    "Scheduled flight duration (minutes)",
    min_value=1,
    max_value=1000,
    value=120,
    step=5
)

distance = st.number_input(
    "Flight distance (miles)",
    min_value=1,
    max_value=6000,
    value=500,
    step=50
)

if st.button("Predict Flight Delay"):

    if origin == destination:
        st.error("Departure and arrival airports cannot be the same.")

    else:
        flight_data = pd.DataFrame({
            "DAY_OF_WEEK": [days[selected_day]],
            "MKT_UNIQUE_CARRIER": [airlines[selected_airline]],
            "ORIGIN": [airports[origin]],
            "DEST": [airports[destination]],
            "DEP_HOUR": [departure_hour],
            "CRS_ELAPSED_TIME": [flight_duration],
            "DISTANCE": [distance]
        })

        prediction = model.predict(flight_data)[0]

        delay_probability = model.predict_proba(flight_data)[0][1]

        if prediction == 1:
            st.warning("This flight is predicted to be delayed.")
        else:
            st.success("This flight is predicted to arrive on time.")

        st.metric(
            "Estimated Delay Probability",
        )
            f"{delay_probability:.1%}"