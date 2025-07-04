
import streamlit as st
import pandas as pd
import googlemaps
from itertools import combinations
from datetime import datetime
import io

st.set_page_config(page_title="LeafGuard Lead Assignment Tool", layout="centered")
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/LeafGuard_Logo.png/800px-LeafGuard_Logo.png", width=200)
st.title("LeafGuard Lead Assignment Tool")
st.markdown("Upload your Excel file with daily leads and download a smart assignment pairing sheet.")

API_KEY = st.secrets["API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:

    import zipfile
    uploaded_file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    # Check for XLSX (ZIP-based format)
    if uploaded_file_bytes[:2] == b'PK':
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

    def get_city(address):
        try:
            geocode_result = gmaps.geocode(address)
            for comp in geocode_result[0]["address_components"]:
                if "locality" in comp["types"]:
                    return comp["long_name"]
            return "Unknown"
        except:
            return "Unknown"

    with st.spinner("🔍 Resolving cities..."):
        leads["Resolved City"] = leads["Full Address"].apply(get_city)

    from datetime import timedelta
    pairs = list(combinations(range(len(leads)), 2))
    results = []
    with st.spinner("🚗 Calculating drive times..."):
        for i, j in pairs:
            addr_i = leads.loc[i, "Full Address"]
            addr_j = leads.loc[j, "Full Address"]
            try:
                tm = gmaps.distance_matrix(addr_i, addr_j, mode="driving")
                dur = tm["rows"][0]["elements"][0].get("duration", {}).get("value", None)
                if dur:
                    results.append((i, j, dur / 60))
            except:
                continue

    df_dur = pd.DataFrame(results, columns=["i", "j", "mins"])

    valid_pairs = []
    for i, j, mins in df_dur.itertuples(index=False):
        t1 = leads.loc[i, "Parsed Time"]
        t2 = leads.loc[j, "Parsed Time"]
        appt1 = leads.loc[i, "Estimate Date"]
        appt2 = leads.loc[j, "Estimate Date"]

        if t1 == t2:
            continue

        delta_hours = abs(datetime.combine(datetime.today(), t1) - datetime.combine(datetime.today(), t2)).seconds / 3600
        max_drive = 120 if delta_hours >= 3 else 60

        if mins <= max_drive:
            valid_pairs.append((i, j, mins))

    suggestions = []
    used = set()
    for i, j, mins in sorted(valid_pairs, key=lambda x: x[2]):
        if i not in used and j not in used:
            suggestions.append({
                "Lead 1": leads.loc[i, "Lead/Invoice #"],
                "Customer 1": leads.loc[i, "Customer Name"],
                "Time 1": leads.loc[i, "Estimate Date"],
                "City 1": leads.loc[i, "Resolved City"],
                "Lead 2": leads.loc[j, "Lead/Invoice #"],
                "Customer 2": leads.loc[j, "Customer Name"],
                "Time 2": leads.loc[j, "Estimate Date"],
                "City 2": leads.loc[j, "Resolved City"],
                "Drive Time (min)": round(mins),
                "Assignment Type": "Paired"
            })
            used.update([i, j])

    for idx in range(len(leads)):
        if idx not in used:
            suggestions.append({
                "Lead 1": leads.loc[idx, "Lead/Invoice #"],
                "Customer 1": leads.loc[idx, "Customer Name"],
                "Time 1": leads.loc[idx, "Estimate Date"],
                "City 1": leads.loc[idx, "Resolved City"],
                "Lead 2": "",
                "Customer 2": "",
                "Time 2": "",
                "City 2": "",
                "Drive Time (min)": "",
                "Assignment Type": "Unpaired (Single Lead)"
            })

    df_out = pd.DataFrame(suggestions)
    df_out = df_out.sort_values(by=["Assignment Type", "Time 1"])

    st.success("✅ All done! Download your file below:")
    csv = df_out.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Assignments CSV", data=csv, file_name="LeafGuard_Assignments.csv", mime="text/csv")
