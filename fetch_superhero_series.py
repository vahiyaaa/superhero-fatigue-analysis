import pandas as pd
import requests

API_KEY = "b5a040de73e0bd642128f5472fc12c09"

# strict TMDB Universe Keyword IDs
franchise_keywords = {"MCU": 180547, "DC": 229266}

# Filter to keep actual sci-fi/fantasy/adventure subgenres
VALID_GENRES = [10759, 10765]

# STRICT BLACKLIST: Eliminates animated spin-offs AND unrelated Star Wars crossovers
excluded_keywords = [
    "Animated", "Animation", "LEGO", "Spidey", "Meet Spidey", "Chibi", 
    "Super Hero High", "DC Super Hero Girls", "Teen Titans", "Toddler", "Shorts",
    "Star Wars", "Mandalorian", "Andor", "Ahsoka", "Obi-Wan", "Acolyte", "Book of Boba"
]

all_series_data = []

for franchise_name, keyword_id in franchise_keywords.items():
    print(f"Connecting to TMDB... Fetching verified superhero series for {franchise_name}...")
    
    for page in range(1, 5):
        url = f"https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&with_keywords={keyword_id}&page={page}&language=en-US"
        response = requests.get(url)
        
        if response.status_code == 200:
            series_list = response.json().get("results", [])
            if not series_list:
                break
                
            for show in series_list:
                show_id = show["id"]
                name = show.get("name", "")
                genre_ids = show.get("genre_ids", [])
                
                # Check 1: Ensure it's in a valid action/adventure/fantasy genre loop
                if not any(g_id in VALID_GENRES for g_id in genre_ids):
                    continue
                
                # Check 2: Skip immediately if it contains any blacklisted words (Star Wars, etc.)
                if any(bad_word.lower() in name.lower() for bad_word in excluded_keywords):
                    print(f"   Skipped non-relevant title: {name}")
                    continue
                
                # Fetch detailed metrics
                details_url = f"https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US"
                details_response = requests.get(details_url)
                
                if details_response.status_code == 200:
                    details = details_response.json()
                    
                    # Double check to verify no animation genres sneak past
                    genres = [g["name"] for g in details.get("genres", [])]
                    if "Animation" in genres:
                        continue
                        
                    first_air_date = details.get("first_air_date", "")
                    if first_air_date:
                        year = int(first_air_date.split("-")[0])
                        
                        # Apply your 2012 - 2026 thesis window
                        if 2012 <= year <= 2026:
                            show_metrics = {
                                "Franchise": franchise_name,
                                "Series Title": name,
                                "First Air Date": first_air_date,
                                "Year": year,
                                "Total Seasons": details.get("number_of_seasons", 1),
                                "Total Episodes": details.get("number_of_episodes", 0),
                                "Vote Average": details.get("vote_average"),
                                "Popularity": details.get("popularity")
                            }
                            all_series_data.append(show_metrics)
        else:
            break

# Format, drop duplicates, and clean index tracking
df_series = pd.DataFrame(all_series_data)
df_series = df_series.drop_duplicates(subset=["Series Title"])
df_series = df_series.sort_values(by="Year").reset_index(drop=True)

# Export the clean television table
df_series.to_csv("superhero_series_data.csv", index=False)

print("\n--- MASTER TV SUCCESS! ---")
print("Pruned superhero series data saved to: 'superhero_series_data.csv'")
print(f"Total verified superhero live-action series remaining: {len(df_series)}")