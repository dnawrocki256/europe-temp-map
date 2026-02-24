import json
import pandas as pd

date = "2025-11-14"

with open(f"./archive/{date}.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Flatten GeoJSON features
df = pd.json_normalize(data["features"])
df = df[df["properties.in_europe"] == "yes"]
columns = ["properties.Name", "properties.Country", "properties.high_temp", "properties.in_europe"]
df = df[columns].sort_values("properties.high_temp", ascending=False)
df.to_csv(f"./archive/{date}-table.csv", index=False)