import pandas as pd
import requests

# 1. PASTE YOUR API KEY HERE
API_KEY = "b5a040de73e0bd642128f5472fc12c09"
# Universe Keyword IDs: 180547 = MCU, 229266 = DCEU (Snyderverse, Wonder Woman, etc.)
franchise_keywords = {"MCU": 180547, "DC": 229266}

# YOUR BLACKLIST: Exclude irrelevant animated/Lego spin-offs
excluded_titles = [
    "Lego Batman",
    "Teen Titans Go",
    "Batman and Harley Quinn",
    "LEGO DC",
    "Teen Titans",
]

all_movies_data = []

for franchise_name, keyword_id in franchise_keywords.items():
    print(
        f"Connecting to TMDB... Fetching live titles for {franchise_name}..."
    )

    for page in range(1, 6):
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_keywords={keyword_id}&page={page}&language=en-US"
        response = requests.get(url)

        if response.status_code == 200:
            movies_list = response.json().get("results", [])
            if not movies_list:
                break

            for movie in movies_list:
                movie_id = movie["id"]
                title = movie.get("title", "")

                # CRUCIAL STEP: Skip the movie if it contains any of our blacklisted words
                if any(
                    blacklisted.lower() in title.lower()
                    for blacklisted in excluded_titles
                ):
                    print(f"   Skipping excluded title: {title}")
                    continue

                # Fetch deep financial details for the valid movies
                movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
                movie_response = requests.get(movie_url)

                if movie_response.status_code == 200:
                    details = movie_response.json()

                    release_date = details.get("release_date", "")
                    if release_date:
                        year = int(release_date.split("-")[0])

                        # Timeframe window: 2012 to 2026
                        if 2012 <= year <= 2026:
                            movie_metrics = {
                                "Franchise": franchise_name,
                                "Title": details.get("title"),
                                "Release Date": release_date,
                                "Budget": details.get("budget", 0),
                                "Revenue": details.get("revenue", 0),
                                "Vote Average": details.get("vote_average"),
                                "Vote Count": details.get("vote_count"),
                                "Popularity": details.get("popularity"),
                                "Year": year,
                            }
                            all_movies_data.append(movie_metrics)
        else:
            break

# Process into DataFrame
df = pd.DataFrame(all_movies_data)

# Clean: Only keep movies with real, reported financials
df = df[(df["Budget"] > 0) & (df["Revenue"] > 0)]
df = df.drop_duplicates(subset=["Title"])

# Calculate core metrics for your thesis
df["Net Profit"] = df["Revenue"] - df["Budget"]
df["ROI Multiplier"] = round(df["Revenue"] / df["Budget"], 2)
df = df.sort_values(by="Year")

# Export to CSV
df.to_csv("superhero_fatigue_data.csv", index=False)
print(f"\n--- SUCCESS! ---")
print(f"Filtered data saved to: 'superhero_fatigue_data.csv'")
print(f"Total valid cinematic universe movies pulled: {len(df)}")