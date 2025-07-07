
import streamlit as st
import pandas as pd
import googlemaps
from datetime import datetime, timedelta
from itertools import combinations
import pydeck as pdk

# Load your Google Maps API key
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

st.set_page_config(layout="wide", page_title="LeafGuard Lead Assignment")
st.title("🛠️ LeafGuard Lead Assignment Optimizer")

# File upload
uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx", "xls"])

def parse_time(t):
    try:
        if isinstance(t, datetime):
            return t.time()
        elif isinstance(t, str):
            for fmt in ("%I:%M", "%H:%M", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(t.strip(), fmt).time()
                except ValueError:
                    continue
    except Exception:
        pass
    return None

def get_coordinates(address):
    try:
        geocode_result = gmaps.geocode(address)
        if not geocode_result:
            return None, None
        loc = geocode_result[0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    except Exception:
        return None, None

def sort_leads(row):
    try:
        time1 = pd.to_datetime(row['Time1'])
        time2 = pd.to_datetime(row['Time2'])
        if time2 < time1:
            row['Lead1'], row['Customer1'], row['Time1'], row['City1'], row['Lead2'], row['Customer2'], row['Time2'], row['City2'] = (
                row['Lead2'], row['Customer2'], row['Time2'], row['City2'],
                row['Lead1'], row['Customer1'], row['Time1'], row['City1']
            )
    except Exception as e:
        print('Error sorting leads:', e)
    return row

if uploaded_file:
    file_head = uploaded_file.read(4)
    uploaded_file.seek(0)

    if file_head[:2] == b"PK":
        leads = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        leads = pd.read_excel(uploaded_file, engine="xlrd")

    # Build full address
    leads["Full Address"] = (
        leads["Address"].astype(str).str.strip() + ", " +
        leads["City"].astype(str).str.strip() + ", " +
        leads["State"].astype(str).str.strip() + " " +
        leads["ZIP code"].astype(str).str.strip()
    )

    leads["Parsed Time"] = leads["Estimate Date"].apply(parse_time)

    # Coordinates
    coords = leads["Full Address"].apply(get_coordinates)
    leads["Latitude"] = coords.apply(lambda x: x[0])
    leads["Longitude"] = coords.apply(lambda x: x[1])

    # Continue with assignment logic...
    st.success("✅ File processed. Assignment logic would continue here.")
