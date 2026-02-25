import geopandas as gpd
from datetime import datetime
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import folium

date = datetime.now().strftime("%Y-%m-%d")
locations = gpd.read_file("./locations_updated.geojson")

def create_idw_map():
    # 1. Prepare data
    lons = locations.geometry.x
    lats = locations.geometry.y
    temps = locations['high_temp']

    # 2. Create a grid (the "canvas" to paint on)
    grid_x, grid_y = np.mgrid[lons.min():lons.max():500j, lats.min():lats.max():500j]

    # 3. Interpolate (Linear is often smoother than Cubic for weather)
    grid_z = griddata((lons, lats), temps, (grid_x, grid_y), method='linear')

    # 4. Create the Map
    m = folium.Map(location=[48, 10], zoom_start=4, tiles='CartoDB positron')

    # 5. Save the interpolation as a transparent image
    # We use the 'Spectral_r' or 'RdYlGn_r' cmap to match your QGIS style
    plt.figure(figsize=(10, 10))
    plt.imshow(grid_z.T, extent=(lons.min(), lons.max(), lats.min(), lats.max()), 
               origin='lower', cmap='Spectral_r', alpha=0.6)
    plt.axis('off')
    plt.savefig('overlay.png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()

    # 6. Overlay the image on the Folium map
    folium.raster_layers.ImageOverlay(
        image='overlay.png',
        bounds=[[lats.min(), lons.min()], [lats.max(), lons.max()]],
        opacity=0.6,
        interactive=False,
        cross_origin=False,
        zindex=1
    ).add_to(m)

    # 7. Add your text labels on top (same as your previous code)
    for idx, row in locations.iterrows():
        label_html = f"""<div style="font-family: sans-serif; color: black; font-weight: bold; 
                        font-size: 8pt; text-shadow: 1px 1px 1px #fff;">{int(row['temp_rd'])}</div>"""
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            icon=folium.DivIcon(html=label_html)
        ).add_to(m)

    m.save("index.html")