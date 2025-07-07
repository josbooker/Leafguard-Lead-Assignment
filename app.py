import streamlit as st
import pandas as pd
import googlemaps
import pydeck as pdk
from datetime import datetime
import io

st.set_page_config(page_title='LeafGuard Lead Assignment Tool', layout='wide')
st.title('📍 LeafGuard Lead Assignment Tool')

API_KEY = st.secrets['API_KEY']
gmaps = googlemaps.Client(key=API_KEY)

def get_drive_time(origin, destination):
    try:
        result = gmaps.distance_matrix(origin, destination, mode='driving')
        duration = result['rows'][0]['elements'][0].get('duration')
        return duration['value'] / 60 if duration else None
    except Exception as e:
        return None

uploaded_file = st.file_uploader('Upload your Excel lead file:', type=['xlsx', 'xls'])
if uploaded_file:
    file_head = uploaded_file.read(4)
    uploaded_file.seek(0)
    if file_head.startswith(b'PK'):  # xlsx format
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    else:
        df = pd.read_excel(uploaded_file)

    df['Full Address'] = df['Address'] + ', ' + df['City'] + ', ' + df['State'] + ' ' + df['ZIP code'].astype(str)
    df['Estimate Time'] = pd.to_datetime(df['Estimate Date'])
    df = df.sort_values('Estimate Time')

    latitudes, longitudes = [], []
    for address in df['Full Address']:
        try:
            geocode = gmaps.geocode(address)
            if geocode:
                location = geocode[0]['geometry']['location']
                latitudes.append(location['lat'])
                longitudes.append(location['lng'])
            else:
                latitudes.append(None)
                longitudes.append(None)
        except Exception as e:
            latitudes.append(None)
            longitudes.append(None)

    df['lat'] = latitudes
    df['lon'] = longitudes

    route_lines = []
    df_result = pd.DataFrame()
    assigned = set()
    rep_counter = 1
    max_drive_time = 60

    for i in range(len(df)):
        if i in assigned:
            continue
        t1 = df.iloc[i]['Estimate Time']
        a1 = df.iloc[i]['Full Address']
        for j in range(i + 1, len(df)):
            if j in assigned:
                continue
            t2 = df.iloc[j]['Estimate Time']
            a2 = df.iloc[j]['Full Address']
            if t1 == t2:
                continue
            drive = get_drive_time(a1, a2)
            if drive is None or drive > max_drive_time:
                continue
            df_result = pd.concat([df_result, pd.DataFrame([{
                'Time1': t1.time(),
                'Address1': a1,
                'Time2': t2.time(),
                'Address2': a2,
                'Drive Time (min)': round(drive),
                'Rep': f'Rep {rep_counter}',
                'Type': 'Paired',
                'Customer Name 1': df.iloc[i]['Customer Name'],
                'Customer Name 2': df.iloc[j]['Customer Name']
            }])])
            assigned.update([i, j])
            rep_counter += 1
            route_lines.append({
                'start': [df.iloc[i]['lon'], df.iloc[i]['lat']],
                'end': [df.iloc[j]['lon'], df.iloc[j]['lat']]
            })
            break

    for i in range(len(df)):
        if i not in assigned:
            df_result = pd.concat([df_result, pd.DataFrame([{
                'Time1': df.iloc[i]['Estimate Time'].time(),
                'Address1': df.iloc[i]['Full Address'],
                'Time2': '',
                'Address2': '',
                'Drive Time (min)': '',
                'Rep': f'Rep {rep_counter}',
                'Type': 'Single',
                'Customer Name 1': df.iloc[i]['Customer Name'],
                'Customer Name 2': ''
            }])])
            rep_counter += 1

    st.subheader('📄 Lead Assignments')
    st.dataframe(df_result)

    map_df = pd.DataFrame({
        'lat': df['lat'],
        'lon': df['lon'],
        'tooltip': df['Customer Name']
    })

    line_layer = pdk.Layer(
        'LineLayer',
        data=pd.DataFrame(route_lines),
        get_source_position='start',
        get_target_position='end',
        get_width=5,
        get_color='[0, 100, 255]',
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=map_df['lat'].mean(),
        longitude=map_df['lon'].mean(),
        zoom=7
    )

    st.pydeck_chart(pdk.Deck(
        layers=[line_layer],
        initial_view_state=view_state,
        tooltip={'text': '{tooltip}'},
        map_style=None
    ))