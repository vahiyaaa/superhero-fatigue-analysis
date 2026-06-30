import time
import pandas as pd
import requests

# 1. PASTE YOUR OMDb API KEY HERE
OMDB_API_KEY = "14fd8ca8"
csv_filename = "superhero_fatigue_data.csv"

try:
    df = pd.read_csv(csv_filename)
    print(f"Loaded {len(df)} movies from '{csv_filename}'.")
except FileNotFoundError:
    print(f"Error: Could not find '{csv_filename}'.")
    exit()

rt_scores = []

print("\nConnecting to OMDb with dual-matching fallback system...")

for index, row in df.iterrows():
    title = row["Title"]
    imdb_id = row["IMDb ID"]
    year = row["Year"]

    # --- STEP 1: TRY WITH IMDB ID FIRST ---
    movie_found = False
    movie_data = {}

    if not pd.isna(imdb_id) and str(imdb_id).startswith("tt"):
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            movie_data = response.json()
            if movie_data.get("Response") == "True":
                movie_found = True

    # --- STEP 2: FALLBACK TO TITLE + YEAR IF ID FAILS ---
    if not movie_found:
        print(f"   ⚠️ ID look-up failed for '{title}'. Trying fallback Title search...")
        # Clean title by removing trailing subtitles in parentheses if any exist
        clean_title = title.split("(")[0].strip()
        url = f"http://www.omdbapi.com/?t={clean_title}&y={year}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            movie_data = response.json()
            if movie_data.get("Response") == "True":
                movie_found = True

    # --- STEP 3: EXTRACT THE ROTTEN TOMATOES SCORE ---
    if movie_found:
        ratings = movie_data.get("Ratings", [])
        rt_score = "N/A"
        for rating in ratings:
            if rating["Source"] == "Rotten Tomatoes":
                rt_score = int(rating["Value"].replace("%", ""))
                break

        rt_scores.append(rt_score)
        print(f"   Success! {title}: RT Score = {rt_score}%")
    else:
        rt_scores.append("N/A")
        print(f"   ❌ Final Match Failed for: {title}")

    time.sleep(0.2)

# Save the final values
df["Rotten Tomatoes"] = rt_scores
df.to_csv(csv_filename, index=False)

print("\n--- DATA PROCESSING COMPLETE ---")
print("Your master spreadsheet is completely optimized and ready for Power BI!")