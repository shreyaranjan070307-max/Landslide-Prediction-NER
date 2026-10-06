import pandas as pd

# ==========================================
# LOAD MAIN DAILY DATA
# ==========================================

main_df = pd.read_parquet(
    "rainfall_soil_2020_2025.parquet"
)

print("Original dataset:", main_df.shape)


# ==========================================
# LOAD AND MERGE NDVI
# ==========================================

ndvi_df = pd.read_csv("NER_NDVI_2020_2025.csv")

# Keep only useful columns
ndvi_df = ndvi_df[
    ["DATE", "LATITUDE", "LONGITUDE", "NDVI"]
]

# Convert TIME to datetime
main_df["TIME"] = pd.to_datetime(main_df["TIME"])

# Create monthly merge key
main_df["YEAR_MONTH"] = (
    main_df["TIME"].dt.strftime("%Y-%m")
)

# Rename NDVI date column
ndvi_df = ndvi_df.rename(
    columns={"DATE": "YEAR_MONTH"}
)

# Merge NDVI
merged_df = main_df.merge(
    ndvi_df,
    on=["YEAR_MONTH", "LATITUDE", "LONGITUDE"],
    how="left"
)

# Remove temporary column
merged_df = merged_df.drop(columns=["YEAR_MONTH"])

print("After NDVI merge:", merged_df.shape)


# ==========================================
# LOAD AND MERGE TERRAIN
# ==========================================

terrain_df = pd.read_parquet(
    "terrain_data/terrain_features_380.parquet"
)

print("Terrain dataset:", terrain_df.shape)

# Merge static terrain features
merged_df = merged_df.merge(
    terrain_df,
    on=["LATITUDE", "LONGITUDE"],
    how="left"
)

print("After terrain merge:", merged_df.shape)


# ==========================================
# FINAL CHECKS
# ==========================================

print("\nFinal columns:")
print(merged_df.columns.tolist())

print("\nMissing values:")
print(merged_df.isna().sum())


# ==========================================
# SAVE FINAL ENVIRONMENTAL DATASET
# ==========================================

merged_df.to_parquet(
    "rainfall_soil_ndvi_terrain_2020_2025.parquet",
    index=False
)

print("\nSaved successfully!")
