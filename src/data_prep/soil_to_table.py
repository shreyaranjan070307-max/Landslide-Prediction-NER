import xarray as xr
import pandas as pd

# Process all six years
for year in range(2020, 2026):

    print(f"\n--- Processing {year} ---")

    # Load NER-only soil data
    soil = xr.open_dataarray(
        f"soil_data/NER/soil_{year}_NER.nc"
    )

    # Convert to table
    df = soil.to_dataframe(
        name="Soil_Moisture"
    ).reset_index()

    # Remove cells outside NER
    df = df.dropna(
        subset=["Soil_Moisture"]
    )

    # Rename time column
    df = df.rename(
        columns={"valid_time": "TIME"}
    )

    # Keep only the columns we need
    df = df[
        ["TIME", "LATITUDE", "LONGITUDE", "Soil_Moisture"]
    ]

    # Save as Parquet
    output_file = (
        f"soil_data/tables/soil_{year}.parquet"
    )

    df.to_parquet(output_file, index=False)

    print(f"Rows: {len(df)}")
    print(f"Saved: {output_file}")

print("\nAll six soil tables created successfully!")