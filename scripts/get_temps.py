import geopandas as gpd
import requests
import json
import pandas as pd
import os
from datetime import datetime

KEY = os.getenv("OPENWEATHER_KEY")

date = datetime.now().strftime("%Y-%m-%d")
print(date)
locations = gpd.read_file("./locations_json.geojson")

def get_temp(lat, lon, name, number):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&units=metric&appid={KEY}"
    high_temp = None
    try:
        r = requests.get(url)
        high_temp = r.json()["daily"][0]["temp"]["max"]
        print(f"{number}/722 {name}: {high_temp}°C")
    except Exception as e:
        print(f"Error fetching {lat}, {lon}, {e}")
    return high_temp

def update_json():
    locations["high_temp"] = locations.apply(lambda row: get_temp(row.geometry.y, row.geometry.x, row["Name"], row["fid"]), axis=1)
    locations["temp_rd"] = (round(locations["high_temp"], 0)).astype(int)
    print(locations)
    locations.to_file("locations_updated.geojson", driver="GeoJSON")
    locations.to_file(f"archive/{date}.geojson", driver="GeoJSON")

def convert_to_csv():
    with open(f"./archive/{date}.geojson", "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data["features"])
    df = df[df["properties.in_europe"] == "yes"]
    columns = ["properties.Name", "properties.Country", "properties.high_temp", "properties.in_europe"]
    df = df[columns].sort_values("properties.high_temp", ascending=False)
    df.to_csv(f"./archive/{date}-table.csv", index=False)

update_json()
convert_to_csv()