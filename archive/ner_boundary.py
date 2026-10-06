import geopandas as gpd

# --------------------------------------------------
# 1. Load the India state boundaries
# --------------------------------------------------

gdf = gpd.read_file(
    "boundaries/state_NWIC.GeoJSON"
)

# --------------------------------------------------
# 2. Northeast Indian states
# --------------------------------------------------

ner_states = [
    "Arunanchal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura"
]

# --------------------------------------------------
# 3. Select only the NER states
# --------------------------------------------------

ner = gdf[gdf["state_name"].isin(ner_states)].copy()

# --------------------------------------------------
# 4. Combine the 8 states into one NER boundary
# --------------------------------------------------

ner_boundary = ner.dissolve()

# --------------------------------------------------
# 5. Save the universal NER boundary
# --------------------------------------------------

ner_boundary.to_file(
    "boundaries/NER_boundary.geojson",
    driver="GeoJSON"
)

print("NER boundary created successfully!")
print("States included:", len(ner))
print("Saved to: boundaries/NER_boundary.geojson")