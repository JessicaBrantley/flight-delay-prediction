import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from datetime import time
from math import radians, sin, cos, sqrt, atan2

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
airport_coordinates = {
    "ATL": (33.6407, -84.4277),
    "CLT": (35.2140, -80.9431),
    "DFW": (32.8998, -97.0403),
    "DEN": (39.8561, -104.6737),
    "IAH": (29.9902, -95.3368),
    "LAS": (36.0840, -115.1537),
    "LAX": (33.9416, -118.4085),
    "ORD": (41.9742, -87.9073),
    "PHX": (33.4342, -112.0116),
    "SEA": (47.4502, -122.3088)
}
def calculate_distance(origin, destination):
    lat1, lon1 = airport_coordinates[origin]
    lat2, lon2 = airport_coordinates[destination]

    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    earth_radius = 3959

    return round(earth_radius * c)

def calculate_duration(distance):
    average_speed = 500
    extra_minutes = 30

    flight_minutes = (distance / average_speed) * 60

    return round(flight_minutes + extra_minutes)

origin = st.selectbox(
    "Departure airport",
    list(airports.keys())
)

destination = st.selectbox(
    "Arrival airport",
    list(airports.keys()),
    index=1
)
origin_code = airports[origin]
destination_code = airports[destination]

if origin_code == destination_code:
    st.error("Departure and arrival airports must be different.")
    st.stop()

calculated_distance = calculate_distance(
    origin_code,
    destination_code
)

calculated_duration = calculate_duration(calculated_distance)

departure_time = st.time_input(
    "Scheduled departure time",
    value=time(12, 0),
    step=900
)

departure_hour = departure_time.hour

if origin_code != destination_code:
    if st.session_state.get("previous_duration_route") != (origin_code, destination_code):
        st.session_state["duration_input"] = calculated_duration
        st.session_state["previous_duration_route"] = (origin_code, destination_code)

flight_duration = st.number_input(
    "Estimated flight duration (minutes)",
    min_value=0,
    step=1,
    key="duration_input"
)

if origin_code != destination_code:
    if st.session_state.get("previous_route") != (origin_code, destination_code):
        st.session_state["distance_input"] = calculated_distance
        st.session_state["previous_route"] = (origin_code, destination_code)

distance = st.number_input(
    "Flight distance (miles)",
    min_value=0,
    step=1,
    key="distance_input"
)

st.caption(
    "Distance and flight duration are automatically estimated based on "
    "the selected airports. You can edit these values to match your flight itinerary."
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
            f"{delay_probability:.1%}"
        )