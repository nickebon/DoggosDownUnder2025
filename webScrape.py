#Nic - trying to parameterise (in progress)

import pandas as pd
import requests
import time

# Define search parameters
states = ["Western Australia", "South Australia"]

# Get search term with fallback
try:
    search_term = input("Enter search term (default: 'veterinary'): ").strip()
    if not search_term:
        print("No input detected. Using default: 'veterinary'")
        search_term = "veterinary"
except Exception as e:
    print("Input failed, using default search term. Error:", e)
    search_term = "veterinary"

print(f"Searching for: '{search_term}'")

# Create a list to store all the results
data = []

# Function to search with OpenStreetMap's Nominatim API
def search_osm(state):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{search_term}, {state}, Australia",
        "format": "json",
        "addressdetails": 1,
        "limit": 50
    }
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MyScraper/1.0; +http://yourwebsite.com)"}

    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch for {state}")
        return

    results = response.json()
    print(f"Found {len(results)} results for {state}")

    for place in results:
        name = place.get("display_name", "Unknown")
        lat = place.get("lat", "")
        lon = place.get("lon", "")
        address = place.get("address", {}).get("suburb", place.get("address", {}).get("city", "Unknown"))

        data.append({
            "Name": name,
            "Latitude": lat,
            "Longitude": lon,
            "Location": address,
            "State": state
        })

# Scrape both states
for state in states:
    search_osm(state)
    time.sleep(2)  # Be gentle to servers

# Save to CSV
df = pd.DataFrame(data)

if not df.empty:
    print("Data found!")
    try:
        fileName = input("Scrape Complete! Name your file: ").strip()
        if not fileName:
            fileName = f"{search_term.replace(' ', '_')}_results"
    except Exception:
        fileName = f"{search_term.replace(' ', '_')}_results"

    fileName += ".csv"
    df.to_csv(fileName, index=False)
    print("File saved as:", fileName)
else:
    print("No data found - error during scrape")

print("Process complete")