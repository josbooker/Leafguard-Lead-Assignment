import streamlit as st
import pandas as pd
import googlemaps
from datetime import datetime
import io
from PIL import Image

st.set_page_config(page_title="LeafGuard Lead Assignment Tool")

st.image("leafguard_logo.png", width=180)
st.title("LeafGuard Lead Assignment Tool")

API_KEY = st.secrets["API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

num_reps_available = st.number_input("How many sales reps are available today?", min_value=1, step=1)

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Full Address"] = df["Address"].astype(str) + ", " + df["City"] + ", " + df["State"] + " " + df["ZIP code"].astype(str)
    df["Estimate Time"] = pd.to_datetime(df["Estimate Date"])

    geocodes = []
    for addr in df["Full Address"]:
        try:
            g = gmaps.geocode(addr)
            loc = g[0]["geometry"]["location"]
            geocodes.append((loc["lat"], loc["lng"]))
        except:
            geocodes.append((None, None))

    df["lat"] = [g[0] for g in geocodes]
    df["lon"] = [g[1] for g in geocodes]

    durations = [[None for _ in range(len(df))] for _ in range(len(df))]
    for i in range(len(df)):
        for j in range(len(df)):
            if i != j:
                try:
                    result = gmaps.distance_matrix(df.iloc[i]["Full Address"], df.iloc[j]["Full Address"], mode="driving")
                    sec = result["rows"][0]["elements"][0]["duration"]["value"]
                    durations[i][j] = sec / 60
                except:
                    durations[i][j] = None

    df_result = pd.DataFrame(columns=["Rep", "Lead1", "Customer1", "Time1", "City1",
                                      "Lead2", "Customer2", "Time2", "City2", "Drive Time (mins)", "Type"])

    assigned = set()
    rep_id = 1
    used_reps = 0

    for i in range(len(df)):
        if i in assigned:
            continue
        time1 = df.iloc[i]["Estimate Time"]
        addr1 = df.iloc[i]["Full Address"]
        city1 = df.iloc[i]["City"]
        lead1 = df.iloc[i]["Lead/Invoice #"]
        cust1 = df.iloc[i]["Customer Name"]

        paired = False
        for j in range(i + 1, len(df)):
            if j in assigned:
                continue
            time2 = df.iloc[j]["Estimate Time"]
            lead2 = df.iloc[j]["Lead/Invoice #"]
            cust2 = df.iloc[j]["Customer Name"]
            city2 = df.iloc[j]["City"]
            dur = durations[i][j]
            time_diff = abs((time2 - time1).total_seconds()) / 3600

            # Tiered logic based on appointment gap
            if dur is not None:
                if time_diff >= 3:
                    if dur <= 60:
                        pass  # good
                    elif dur <= 120 and used_reps + 1 >= num_reps_available:
                        pass  # fallback only if no extra reps
                    else:
                        continue
                else:
                    if dur > 60:
                        continue

                if used_reps < num_reps_available:
                    df_result.loc[len(df_result)] = [rep_id, lead1, cust1, time1, city1,
                                                     lead2, cust2, time2, city2, round(dur, 1), "Paired"]
                    assigned.update([i, j])
                    rep_id += 1
                    used_reps += 1
                    paired = True
                    break

        if paired:
            continue

        # Try assigning single
        if used_reps < num_reps_available:
            df_result.loc[len(df_result)] = [rep_id, lead1, cust1, time1, city1,
                                             "", "", "", "", "", "Single"]
            assigned.add(i)
            rep_id += 1
            used_reps += 1
        else:
            df_result.loc[len(df_result)] = ["Reschedule", lead1, cust1, time1, city1,
                                             "", "", "", "", "", "Suggested to Reschedule"]
            assigned.add(i)

    st.success("✅ Assignments complete!")
    st.dataframe(df_result)
    csv = df_result.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "assignments.csv", "text/csv")