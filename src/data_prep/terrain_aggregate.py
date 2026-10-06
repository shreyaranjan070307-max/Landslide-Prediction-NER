import pandas as pd
import xarray as xr
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

# --------------------------------------------------
# 1. Load terrain datasets
# --------------------------------------------------

print("Loading terrain data...")

dem = xr.open_dataset("terrain_data/gebco_ner.nc")
slope = xr.open_dataarray("terrain_data/slope_gebco.nc")
tri = xr.open_dataarray("terrain_data/tri_gebco.nc")

elevation = dem["elevation"]

print("Terrain loaded!")

# --------------------------------------------------
# 2. Get the exact 380 NER target cells
# --------------------------------------------------

rainfall = pd.read_parquet(
    "ner_rainfall_features.parquet"
)

cells = rainfall[
    ["LATITUDE", "LONGITUDE"]
].drop_duplicates()

ner = gpd.read_file(
    "boundaries/NER_boundary.geojson"
).to_crs("EPSG:4326")

cells["inside"] = cells.apply(
    lambda row: ner.geometry.contains(
        Point(row.LONGITUDE, row.LATITUDE)
    ).any(),
    axis=1
)

cells = cells[cells["inside"]].drop(
    columns="inside"
).reset_index(drop=True)

print("Target NER cells:", len(cells))

# --------------------------------------------------
# 3. Aggregate terrain into 0.25° cells
# --------------------------------------------------

results = []

for n, row in cells.iterrows():

    lat_center = row["LATITUDE"]
    lon_center = row["LONGITUDE"]

    # Each target cell is 0.25° × 0.25°
    lat_min = lat_center - 0.125
    lat_max = lat_center + 0.125

    lon_min = lon_center - 0.125
    lon_max = lon_center + 0.125

    # Select native-resolution terrain pixels
    elev_cell = elevation.sel(
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max)
    )

    slope_cell = slope.sel(
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max)
    )

    tri_cell = tri.sel(
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max)
    )

    elev_values = elev_cell.values.ravel()
    slope_values = slope_cell.values.ravel()
    tri_values = tri_cell.values.ravel()

    # Remove invalid values
    elev_values = elev_values[
        np.isfinite(elev_values)
    ]

    slope_values = slope_values[
        np.isfinite(slope_values)
    ]

    tri_values = tri_values[
        np.isfinite(tri_values)
    ]

    # --------------------------------------------------
    # Terrain features
    # --------------------------------------------------

    result = {
        "LATITUDE": lat_center,
        "LONGITUDE": lon_center,

        # Elevation
        "elevation_mean":
            np.mean(elev_values),

        "elevation_range":
            np.max(elev_values) - np.min(elev_values),

        "elevation_std":
            np.std(elev_values),

        # Slope
        "slope_mean":
            np.mean(slope_values),

        "slope_max":
            np.max(slope_values),

        "slope_std":
            np.std(slope_values),

        "slope_pct_above_30":
            np.mean(slope_values > 30) * 100,

        # TRI
        "tri_mean":
            np.mean(tri_values),

        "tri_p95":
            np.percentile(tri_values, 95),

        "tri_std":
            np.std(tri_values)
    }

    results.append(result)

    if (n + 1) % 25 == 0:
        print(
            f"Processed {n + 1}/{len(cells)} cells"
        )

# --------------------------------------------------
# 4. Create final terrain table
# --------------------------------------------------

terrain_features = pd.DataFrame(results)

print("\nTerrain aggregation complete!")

print(
    "Shape:",
    terrain_features.shape
)

print("\nColumns:")
print(
    terrain_features.columns.tolist()
)

print("\nFirst 5 cells:")
print(
    terrain_features.head()
)

# --------------------------------------------------
# 5. Save
# --------------------------------------------------

output_file = (
    "terrain_data/terrain_features_380.parquet"
)

terrain_features.to_parquet(
    output_file,
    index=False
)

print(
    f"\nSaved: {output_file}"
)