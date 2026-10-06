import cdsapi

client = cdsapi.Client()

years = ["2020", "2021", "2022", "2023", "2024", "2025"]

for year in years:

    print(f"\nDownloading soil moisture for {year}...")

    client.retrieve(
        "reanalysis-era5-land",
        {
            "variable": "volumetric_soil_water_layer_1",
            "year": year,
            "month": [
                "01", "02", "03", "04", "05", "06",
                "07", "08", "09", "10", "11", "12"
            ],
            "day": [
                "01", "02", "03", "04", "05", "06", "07",
                "08", "09", "10", "11", "12", "13", "14",
                "15", "16", "17", "18", "19", "20", "21",
                "22", "23", "24", "25", "26", "27", "28",
                "29", "30", "31"
            ],
            "time": "12:00",
            "area": [30, 88, 21, 98],
            "data_format": "netcdf",
            "download_format": "unarchived",
        },
        f"soil_{year}.nc",
    )

    print(f"{year} download complete!")

print("\nAll soil moisture downloads complete!")