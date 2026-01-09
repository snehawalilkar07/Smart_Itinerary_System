import streamlit as st
import pandas as pd
from helpers import parse_time, clean_text
from itinerary import build_itinerary
from map_utils import create_map
from pdf_utils import export_pdf
from streamlit_folium import st_folium

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="🧭 Smart Multi-Day Itinerary Planner",
    layout="wide"
)

# ================== HEADING ==================
st.title("🧭 Smart Multi-Day Itinerary Planner")

# ================== LOAD DATA ==================
df = pd.read_csv("Maharashtra_POI.csv", encoding="latin1")
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df.dropna(subset=["lat", "lon"], inplace=True)

# ================== SESSION STATE ==================
if "start" not in st.session_state:
    st.session_state.start = {"lat": 19.0760, "lon": 72.8777}  # Mumbai default
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

# ================== SIDEBAR ==================
st.sidebar.header("Trip Settings")

# Default city Mumbai
city_index = list(sorted(df.city.unique())).index("Mumbai ") if "Mumbai " in df.city.unique() else 0
city = st.sidebar.selectbox("City", sorted(df.city.unique()), index=city_index)

# Default interest = second index only
interests_list = sorted(df.category.unique())
default_interest = [interests_list[1]] if len(interests_list) > 1 else [interests_list[0]]
interests = st.sidebar.multiselect(
    "Interests",
    interests_list,
    default=default_interest
)

days = st.sidebar.slider("Days", 1, 7, 2)

# Default start time = 08:00 AM, end time = 08:00 PM
start_time = parse_time(st.sidebar.selectbox("Start Time", ["07:00 AM","08:00 AM","09:00 AM"], index=1))
end_time = parse_time(st.sidebar.selectbox("End Time", ["05:00 PM","06:00 PM","07:00 PM","08:00 PM"], index=3))

mode = st.sidebar.selectbox("Travel Mode", ["Car", "Auto", "Bike", "Walk"])
speed = {"Car": 45, "Auto": 35, "Bike": 30, "Walk": 5}[mode]

if st.sidebar.button("🔁 Reset Location"):
    st.session_state.start = {"lat": 19.0760, "lon": 72.8777}
    st.session_state.itinerary = None

generate = st.sidebar.button("🧭 Generate Itinerary")

# Filter city & interest
df_city = df[(df.city == city) & (df.category.isin(interests))].copy()

# ================== GENERATE ITINERARY ==================
if generate:
    st.session_state.itinerary = build_itinerary(df_city, st.session_state.start, days, start_time, end_time, speed)

# ================== DISPLAY MAP ==================
if st.session_state.itinerary:
    st.subheader("🗺️ Your Generated Itinerary is Here")
else:
    st.subheader("🗺️ Select Starting Location")

m = create_map(st.session_state.start, st.session_state.itinerary)

st_data = st_folium(
    m,
    height=600,
    width=None,  # full container width
    returned_objects=["last_clicked"]
)

if st_data and st_data.get("last_clicked"):
    st.session_state.start = {
        "lat": st_data["last_clicked"]["lat"],
        "lon": st_data["last_clicked"]["lng"]
    }

# ================== DISPLAY ITINERARY ==================
if st.session_state.itinerary:
    st.header("📅 Your Itinerary")
    for i, day in enumerate(st.session_state.itinerary, 1):
        st.subheader(f"Day {i}")
        for s, e, p in day:
            st.write(f"{s.strftime('%I:%M %p')} - {e.strftime('%I:%M %p')} — {p['name']} ({p['category']})")
        st.markdown("---")

    # ================== PDF EXPORT ==================
    pdf_output = export_pdf(st.session_state.itinerary)
    st.download_button(
        label="📤 Export Itinerary as PDF",
        data=pdf_output,
        file_name="itinerary.pdf",
        mime="application/pdf"
    )
