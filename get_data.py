import csv
import json

import requests

resorts = [
    {"name": "Vail, CO", "lat": 39.6397, "lon": -106.3740},
    {"name": "Breckenridge, CO", "lat": 39.4803, "lon": -106.0665},
    {"name": "Jackson Hole, WY", "lat": 43.5879, "lon": -110.821},
    {"name": "Park City, UT", "lat": 40.6514, "lon": -111.5070},
    {"name": "Aspen Mountain, CO", "lat": 39.1867, "lon": -106.8180},
    {"name": "Big Sky, MT", "lat": 45.2848, "lon": -111.4011},
    {"name": "Bridger Bowl, MT", "lat": 45.8163, "lon": -110.8835},
    {"name": "Telluride, CO", "lat": 37.9375, "lon": -107.8123},
    {"name": "Snowbird, UT", "lat": 40.5865, "lon": -111.6565},
    {"name": "Mammoth Mountain, CA", "lat": 37.6485, "lon": -119.0320},
    {"name": "Heavenly, CA/NV", "lat": 38.9351, "lon": -119.9394},
    {"name": "Killington, VT", "lat": 43.6256, "lon": -72.7900},
    {"name": "Stowe, VT", "lat": 44.4654, "lon": -72.6884},
    {"name": "Okemo, VT", "lat": 43.3898, "lon": -72.6684},
    {"name": "Copper Mountain, CO", "lat": 39.5021, "lon": -106.1510},
    {"name": "Keystone, CO", "lat": 39.6050, "lon": -105.9545},
    {"name": "Winter Park, CO", "lat": 39.8876, "lon": -105.7631},
    {"name": "Deer Valley, UT", "lat": 40.6315, "lon": -111.4753},
    {"name": "Alta, UT", "lat": 40.5884, "lon": -111.6379},
    {"name": "Whitefish, MT", "lat": 48.4547, "lon": -114.3658},
    {"name": "Grand Targhee, WY", "lat": 43.8400, "lon": -110.9650},
    {"name": "Snowshoe, WV", "lat": 38.3959, "lon": -79.9962},
    {"name": "Taos Ski Valley, NM", "lat": 36.7061, "lon": -105.4874},
    {"name": "Crystal Mountain, WA", "lat": 46.9708, "lon": -121.5411},
    {"name": "Whistler Blackcomb, BC", "lat": 50.1163, "lon": -122.9574},
    {"name": "Mont Tremblant, QC", "lat": 46.1160, "lon": -74.5391},
    {"name": "Cypress Mountain, BC", "lat": 49.3950, "lon": -123.2030},
    {"name": "Kicking Horse, BC", "lat": 51.2990, "lon": -116.0403},
    {"name": "Mont‑Sainte‑Anne, QC", "lat": 47.0667, "lon": -70.8333},
    {"name": "Mont Sutton, QC", "lat": 45.0000, "lon": -72.2833},
]


def get_forecast_for_resort(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=snowfall_sum"
        f"&timezone=America/Denver"
    )
    resp = requests.get(url)
    data = resp.json()
    try:

        snow = data["daily"]["snowfall_sum"]
        total_7d = sum(snow)
        total_24h = snow[0]
        return total_7d, total_24h
    except KeyError:
        return None


forecast_results = {}
for r in resorts:
    snow_7d, snow_24h = get_forecast_for_resort(r["lat"], r["lon"])
    forecast_results[r["name"]] = {"7d_snow": snow_7d, "24h_snow": snow_24h}

print(forecast_results)

with open("dataset/ski_resorts.json") as f:
    resorts = json.load(f)["ski_resorts"]

coords = ";".join(f"{r['lon']},{r['lat']}" for r in resorts)

url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=duration,distance"
resp = requests.get(url)
data = resp.json()

names = [r["name"] for r in resorts]
distances_miles = [[m / 1609.34 for m in row] for row in data["distances"]]

with open("dataset/resort_distances.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([""] + names)
    for name, row in zip(names, distances_miles):
        writer.writerow([name] + row)
