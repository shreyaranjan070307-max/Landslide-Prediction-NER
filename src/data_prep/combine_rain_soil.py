import pandas as pd

all_years = []

for year in range(2020, 2026):

    print(f"\n--- Processing {year} ---")

    # Load rainfall features
    rain = pd.read_parquet(
        "ner_rainfall_features.parquet"
    )

    # Keep only this year's rainfall data
    rain["TIME"] = pd.to_datetime(rain["TIME"])
    rain = rain[
        rain["TIME"].dt.year == year
    ].copy()

    # Load soil data
    soil = pd.read_parquet(
        f"soil_data/tables/soil_{year}.parquet"
    )

    # Normalize time to the calendar day
    rain["TIME"] = rain["TIME"].dt.normalize()
    soil["TIME"] = pd.to_datetime(
        soil["TIME"]
    ).dt.normalize()

    # Merge rainfall + soil
    merged = rain.merge(
        soil,
        on=["TIME", "LATITUDE", "LONGITUDE"],
        how="inner"
    )

    print("Rainfall rows:", len(rain))
    print("Soil rows:", len(soil))
    print("Merged rows:", len(merged))

    all_years.append(merged)

# Combine all six years
combined = pd.concat(
    all_years,
    ignore_index=True
)

# Save final rainfall + soil dataset
combined.to_parquet(
    "rainfall_soil_2020_2025.parquet",
    index=False
)

print("\n================================")
print("COMBINATION COMPLETE!")
print("Total rows:", len(combined))
print("Columns:", combined.columns.tolist())
print("================================")