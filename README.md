
# LeafGuard Lead Assignment Tool

This Streamlit web app intelligently assigns leads to your sales reps based on time, location, and drive time.

## How to Use

1. Upload your Excel file (.xlsx) with these columns:
   - Lead/Invoice #
   - Estimate Date (includes time)
   - Customer Name
   - Address, City, State, ZIP code

2. The app will:
   - Parse lead info
   - Use Google Maps to calculate drive times
   - Match up to two leads per rep intelligently

3. Download a clean CSV report

## Deploy the App

1. Upload these files to a GitHub repo
2. Go to https://streamlit.io/cloud and log in with GitHub
3. Click “New App” and select your repo
4. In **Settings > Secrets**, add this:

```
API_KEY = "your-google-maps-api-key"
```

Done! Now your team can use it daily.
