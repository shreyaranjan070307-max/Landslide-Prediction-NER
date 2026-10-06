import geopandas as gpd
import xarray as xr
import numpy as np
from shapely.geometry import Point

# --------------------------------------------------
# 1. Load the universal NER boundary
# --------------------------------------------------

ner = gpd.read_file(
    "boundaries/NER_boundary.geojson"
)

# Convert boundary to latitude/longitude
ner = ner.to_crs("EPSG:4326")

# --------------------------------------------------
# 2. Process all six years
# --------------------------------------------------

for year in range(2020, 2026):

    print(f"\n--- Processing {year} ---")

    # Open regridded soil data
    soil = xr.open_dataarray(
        f"soil_data/regridded/soil_{year}_regridded.nc"
    )

    lat = soil["LATITUDE"].values
    lon = soil["LONGITUDE"].values

    # --------------------------------------------------
    # 3. Create NER mask
    # --------------------------------------------------

    mask = np.zeros(
        (len(lat), len(lon)),
        dtype=bool
    )

    for i, latitude in enumerate(lat):

        for j, longitude in enumerate(lon):

            point = Point(
                float(longitude),
                float(latitude)
            )

            mask[i, j] = ner.geometry.contains(point).any()

    # --------------------------------------------------
    # 4. Count NER cells
    # --------------------------------------------------

    ner_cell_count = mask.sum()

    print("NER grid cells:", ner_cell_count)

    # --------------------------------------------------
    # 5. Apply mask
    # --------------------------------------------------

    soil_ner = soil.where(mask)

    # --------------------------------------------------
    # 6. Save NER-only soil dataset
    # --------------------------------------------------

    output_file = (
        f"soil_data/NER/soil_{year}_NER.nc"
    )

    soil_ner.to_netcdf(output_file)

    print(f"Saved: {output_file}")

print("\nAll six years processed successfully!")