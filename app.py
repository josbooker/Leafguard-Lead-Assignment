
import streamlit as st
import pandas as pd
import googlemaps
from itertools import combinations
from datetime import datetime
import pydeck as pdk
import base64

# === CONFIGURATION ===
st.set_page_config(page_title="LeafGuard Lead Assignment Tool", layout="wide")
st.markdown("## 🛠️ LeafGuard Lead Assignment Tool")
st.markdown("Upload your Excel file with daily leads and assign them to reps smartly.")

# === EMBEDDED LOGO ===
logo = "data:image/png;base64,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"
st.markdown(f"<img src='{logo}' width='200'>", unsafe_allow_html=True)

# === USER INPUT ===
rep_count = st.number_input("How many sales reps are available today?", min_value=1, max_value=50, step=1)
uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:
    file_head = uploaded_file.read(4)
    uploaded_file.seek(0)
    if file_head[:2] == b"PK":
        leads = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        leads = pd.read_excel(uploaded_file, engine="xlrd")

    leads["Full Address"] = leads["Address"].astype(str).str.strip() + ", " + \
                            leads["City"].astype(str).str.strip() + ", " + \
                            leads["State"].astype(str).str.strip() + " " + \
                            leads["ZIP code"].astype(str).str.strip()

    def parse_time(t):
        if isinstance(t, datetime):
            return t.time()
        elif isinstance(t, str):
            try:
                return datetime.strptime(t.strip(), "%I:%M").time()
            except:
                return datetime.strptime(t.strip(), "%Y-%m-%d %H:%M:%S").time()
        else:
            raise ValueError(f"Unsupported time format: {t}")

    leads["Parsed Time"] = leads["Estimate Date"].apply(parse_time)

    gmaps = googlemaps.Client(key=st.secrets["API_KEY"])

    def get_coordinates(address):
        try:
            geocode_result = gmaps.geocode(address)
            loc = geocode_result[0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        except:
            return None, None

    with st.spinner("📍 Geocoding addresses..."):
        leads[["lat", "lon"]] = leads["Full Address"].apply(lambda addr: pd.Series(get_coordinates(addr)))

    from itertools import combinations
    pairs = list(combinations(range(len(leads)), 2))
    results = []
    with st.spinner("🚗 Calculating drive times..."):
        for i, j in pairs:
            a1 = leads.loc[i, "Full Address"]
            a2 = leads.loc[j, "Full Address"]
            try:
                tm = gmaps.distance_matrix(a1, a2, mode="driving")
                dur = tm["rows"][0]["elements"][0].get("duration", {}).get("value", None)
                if dur:
                    mins = dur / 60
                    t1 = leads.loc[i, "Parsed Time"]
                    t2 = leads.loc[j, "Parsed Time"]
                    delta_hours = abs(datetime.combine(datetime.today(), t1) - datetime.combine(datetime.today(), t2)).seconds / 3600
                    results.append((i, j, mins, delta_hours))
            except:
                continue

    short_pairs = [(i, j, mins) for i, j, mins, h in results if mins <= 60]
    long_pairs = [(i, j, mins) for i, j, mins, h in results if 60 < mins <= 120 and h >= 3]

    total_leads = len(leads)
    max_capacity = rep_count * 2
    assignments = []
    used = set()
    rep = 1

    for i, j, mins in sorted(short_pairs, key=lambda x: x[2]):
        if i not in used and j not in used and len(used) + 2 <= max_capacity and leads.at[i, 'Parsed Time'] != leads.at[j, 'Parsed Time']:
            assignments.append((rep, i, j, mins))
            used.update([i, j])
            rep += 1
            if rep > rep_count:
                rep = 1

    remaining_slots = max_capacity - len(used)
    remaining_leads = [idx for idx in range(len(leads)) if idx not in used]
    long_pairs_needed = max(0, len(remaining_leads) - remaining_slots)

    for i, j, mins in sorted(long_pairs, key=lambda x: x[2]):
        if i not in used and j not in used and long_pairs_needed > 0 and leads.at[i, 'Parsed Time'] != leads.at[j, 'Parsed Time']:
            assignments.append((rep, i, j, mins))
            used.update([i, j])
            rep += 1
            long_pairs_needed -= 2
            if rep > rep_count:
                rep = 1

    single_leads = [idx for idx in range(len(leads)) if idx not in used]
    reschedules = set()
    if len(used) + len(single_leads) > max_capacity:
        excess = len(used) + len(single_leads) - max_capacity
        reschedules = set(single_leads[-excess:])
        single_leads = single_leads[:-excess]

    data_rows = []
    for rep_num, i, j, mins in assignments:
        data_rows.append({
            "Rep": rep_num,
            "Lead1": leads.loc[i, "Lead/Invoice #"],
            "Customer1": leads.loc[i, "Customer Name"],
            "Time1": leads.loc[i, "Estimate Date"],
            "City1": leads.loc[i, "City"],
            "lat1": leads.loc[i, "lat"],
            "lon1": leads.loc[i, "lon"],
            "Lead2": leads.loc[j, "Lead/Invoice #"],
            "Customer2": leads.loc[j, "Customer Name"],
            "Time2": leads.loc[j, "Estimate Date"],
            "City2": leads.loc[j, "City"],
            "lat2": leads.loc[j, "lat"],
            "lon2": leads.loc[j, "lon"],
            "Drive Time (mins)": round(mins),
            "Type": "Paired"
        })

    for idx in single_leads:
        data_rows.append({
            "Rep": "Unpaired",
            "Lead1": leads.loc[idx, "Lead/Invoice #"],
            "Customer1": leads.loc[idx, "Customer Name"],
            "Time1": leads.loc[idx, "Estimate Date"],
            "City1": leads.loc[idx, "City"],
            "lat1": leads.loc[idx, "lat"],
            "lon1": leads.loc[idx, "lon"],
            "Lead2": "",
            "Customer2": "",
            "Time2": "",
            "City2": "",
            "lat2": None,
            "lon2": None,
            "Drive Time (mins)": "",
            "Type": "Single"
        })

    for idx in reschedules:
        data_rows.append({
            "Rep": "Reschedule",
            "Lead1": leads.loc[idx, "Lead/Invoice #"],
            "Customer1": leads.loc[idx, "Customer Name"],
            "Time1": leads.loc[idx, "Estimate Date"],
            "City1": leads.loc[idx, "City"],
            "lat1": leads.loc[idx, "lat"],
            "lon1": leads.loc[idx, "lon"],
            "Lead2": "",
            "Customer2": "",
            "Time2": "",
            "City2": "",
            "lat2": None,
            "lon2": None,
            "Drive Time (mins)": "",
            "Type": "Suggested to Reschedule"
        })

    df_result = pd.DataFrame(data_rows)
    df_display = df_result.drop(columns=["lat1", "lon1", "lat2", "lon2"])
    st.success("✅ Assignments complete!")
    st.dataframe(df_display)

    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="LeadAssignments.csv", mime="text/csv")

    st.subheader("🗺️ Map of Assignments")
    map_df = []
    color_palette = [[255,0,0],[0,128,0],[0,0,255],[255,165,0],[128,0,128],[0,206,209],[255,20,147],[50,205,50],[70,130,180],[210,105,30]]
    rep_colors = {}

    for row in df_result.itertuples():
        rep_id = row.Rep
        if rep_id not in rep_colors:
            rep_colors[rep_id] = color_palette[len(rep_colors)%len(color_palette)]
        color = rep_colors[rep_id]
        if pd.notna(row.lat1) and pd.notna(row.lon1):
            map_df.append({"lat": row.lat1, "lon": row.lon1, "tooltip": f"Rep: {rep_id}, Lead: {row.Lead1}", "color": color})
        if pd.notna(row.lat2) and pd.notna(row.lon2):
            map_df.append({"lat": row.lat2, "lon": row.lon2, "tooltip": f"Rep: {rep_id}, Lead: {row.Lead2}", "color": color})

    if map_df:
        map_df = pd.DataFrame(map_df)
        map_df = map_df.dropna(subset=["lat", "lon"])
        map_df = map_df[map_df["lat"] != ""]
        map_df["color"] = map_df["color"].apply(lambda x: [int(c) for c in x])

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius=600,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=7
        )
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{tooltip}"},
            map_style=None
        ))

    assigned = set()
        rep_id = 1
        results = []
    
        for i in range(len(df)):
            if i in assigned:
                continue
            lead1 = df.iloc[i]
            best_pair = None
            best_drive = None
    
            for j in range(i+1, len(df)):
                if j in assigned:
                    continue
                lead2 = df.iloc[j]
    
                time_diff = abs((lead1['Estimate Date'] - lead2['Estimate Date']).total_seconds()) / 3600
                drive = duration_matrix[i][j]
    
                if pd.isna(drive):
                    continue
    
                # Drive-time logic
                if time_diff < 3 and drive > 60:
                    continue
                if time_diff >= 3 and drive > 120:
                    continue
    
                if best_drive is None or drive < best_drive:
                    best_pair = j
                    best_drive = drive
    
            if best_pair is not None:
                j = best_pair
                lead2 = df.iloc[j]
                results.append({
                    "Rep": rep_id,
                    "Lead1": lead1["Lead/Invoice #"],
                    "Customer1": lead1["Customer Name"],
                    "Time1": lead1["Estimate Date"],
                    "City1": lead1["City"],
                    "Lead2": lead2["Lead/Invoice #"],
                    "Customer2": lead2["Customer Name"],
                    "Time2": lead2["Estimate Date"],
                    "City2": lead2["City"],
                    "Drive Time (mins)": round(best_drive, 1),
                    "Type": "Paired"
                })
                assigned.update([i, j])
                rep_id += 1
            else:
                results.append({
                    "Rep": rep_id,
                    "Lead1": lead1["Lead/Invoice #"],
                    "Customer1": lead1["Customer Name"],
                    "Time1": lead1["Estimate Date"],
                    "City1": lead1["City"],
                    "Lead2": "",
                    "Customer2": "",
                    "Time2": "",
                    "City2": "",
                    "Drive Time (mins)": "",
                    "Type": "Single"
                })
                assigned.add(i)
                rep_id += 1
    
        df_result = pd.DataFrame(results)