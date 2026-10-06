
import xarray as xr
import geopandas as gpd
import numpy as np
import glob
from shapely.geometry import Point

files = sorted(glob.glob("rainfall_data/RF25_ind20*.nc"))
datasets = [xr.open_dataset(file) for file in files]

rain_data = xr.concat(datasets, dim="TIME")

rain = rain_data["RAINFALL"]

states = gpd.read_file(
    "boundaries/state_NWIC.GeoJSON"
)

states = states.to_crs("EPSG:4326")

ner_names = [
    "Arunanchal Pradesh",
    "Assam",
    "Meghalaya",
    "Manipur",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura"
]

ner = states[
    states["state_name"].isin(ner_names)
].copy()

ner_boundary = ner.geometry.union_all()

lat = rain.LATITUDE.values
lon = rain.LONGITUDE.values

lon_grid, lat_grid = np.meshgrid(lon, lat)

points = [
    Point(x, y)
    for x, y in zip(
        lon_grid.ravel(),
        lat_grid.ravel()
    )
]

inside = np.array([
    ner_boundary.contains(point)
    for point in points
])

ner_mask = inside.reshape(
    len(lat),
    len(lon)
)

ner_rainfall = rain.where(ner_mask)

# ============================================================
# CALCULATE CUMULATIVE RAINFALL FEATURES
# ============================================================

rain_3day = ner_rainfall.rolling(TIME=3).sum()
rain_7day = ner_rainfall.rolling(TIME=7).sum()
rain_15day = ner_rainfall.rolling(TIME=15).sum()
rain_30day = ner_rainfall.rolling(TIME=30).sum()

print("Rainfall features calculated:")
print("- Daily rainfall")
print("- 3-day cumulative rainfall")
print("- 7-day cumulative rainfall")
print("- 15-day cumulative rainfall")
print("- 30-day cumulative rainfall")


print("NER rainfall dataset ready.")
print(f"Time period: {rain.TIME.values[0]} → {rain.TIME.values[-1]}")
print(f"NER states: {len(ner)}")
print(f"NER grid cells: {int(ner_mask.sum())}")
print(f"Rainfall unit: {rain.attrs.get('units', 'unknown')}")
print("3-day cumulative rainfall calculated.")
# ============================================================
# VIEW ALL RAINFALL FEATURES FOR ONE GRID CELL
# ============================================================

sample = ner_rainfall.sel(
    LATITUDE=27.25,
    LONGITUDE=88.5
)

sample_3day = rain_3day.sel(
    LATITUDE=27.25,
    LONGITUDE=88.5
)

sample_7day = rain_7day.sel(
    LATITUDE=27.25,
    LONGITUDE=88.5
)

sample_15day = rain_15day.sel(
    LATITUDE=27.25,
    LONGITUDE=88.5
)

sample_30day = rain_30day.sel(
    LATITUDE=27.25,
    LONGITUDE=88.5
)


# Convert each rainfall series into a pandas table

sample_table = sample.to_dataframe(
    name="Daily_Rain_mm"
)

sample_3day_table = sample_3day.to_dataframe(
    name="Rain_3Day_mm"
)

sample_7day_table = sample_7day.to_dataframe(
    name="Rain_7Day_mm"
)

sample_15day_table = sample_15day.to_dataframe(
    name="Rain_15Day_mm"
)

sample_30day_table = sample_30day.to_dataframe(
    name="Rain_30Day_mm"
)


# Keep only rainfall columns and join them by TIME

sample_table = sample_table[["Daily_Rain_mm"]].join(
    sample_3day_table[["Rain_3Day_mm"]]
)

sample_table = sample_table.join(
    sample_7day_table[["Rain_7Day_mm"]]
)

sample_table = sample_table.join(
    sample_15day_table[["Rain_15Day_mm"]]
)

sample_table = sample_table.join(
    sample_30day_table[["Rain_30Day_mm"]]
)


# Convert TIME from index into a normal column

sample_table = sample_table.reset_index()


# Round rainfall values to 2 decimal places

rainfall_columns = [
    "Daily_Rain_mm",
    "Rain_3Day_mm",
    "Rain_7Day_mm",
    "Rain_15Day_mm",
    "Rain_30Day_mm"
]

sample_table[rainfall_columns] = (
    sample_table[rainfall_columns].round(2)
)


# Display first 35 days

print("\n--- SAMPLE RAINFALL TABLE ---")

print(
    sample_table[
        [
            "TIME",
            "Daily_Rain_mm",
            "Rain_3Day_mm",
            "Rain_7Day_mm",
            "Rain_15Day_mm",
            "Rain_30Day_mm"
        ]
    ].head(35).to_string(index=False)
)
# ============================================================
# 12. SAVE RAINFALL FEATURES AS PARQUET
# ============================================================

# Convert the rainfall data into a table
rainfall_table = ner_rainfall.to_dataframe(
    name="Daily_Rain_mm"
).reset_index()

# Add the cumulative rainfall features
rainfall_table["Rain_3Day_mm"] = (
    rain_3day.to_dataframe(name="Rain_3Day_mm")
    .reset_index()["Rain_3Day_mm"]
)

rainfall_table["Rain_7Day_mm"] = (
    rain_7day.to_dataframe(name="Rain_7Day_mm")
    .reset_index()["Rain_7Day_mm"]
)

rainfall_table["Rain_15Day_mm"] = (
    rain_15day.to_dataframe(name="Rain_15Day_mm")
    .reset_index()["Rain_15Day_mm"]
)

rainfall_table["Rain_30Day_mm"] = (
    rain_30day.to_dataframe(name="Rain_30Day_mm")
    .reset_index()["Rain_30Day_mm"]
)

# Save the table
rainfall_table.to_parquet(
    "ner_rainfall_features.parquet",
    index=False
)

print("\nRainfall feature dataset saved.")
print("File: ner_rainfall_features.parquet")
print("Rows:", len(rainfall_table))
print("Columns:", list(rainfall_table.columns))

