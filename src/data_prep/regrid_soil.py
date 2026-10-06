import xarray as xr

years = range(2020, 2026)

for year in years:

    print(f"\n--- Processing {year} ---")

    # Open ERA5-Land soil moisture
    soil = xr.open_dataset(f"soil_{year}.nc")
    soil_moisture = soil["swvl1"]

    # Open corresponding IMD rainfall file
    rainfall = xr.open_dataset(
        f"rainfall_data/RF25_ind{year}_rfp25.nc"
    )

    # Interpolate ERA5-Land onto IMD grid
    soil_regridded = soil_moisture.interp(
        latitude=rainfall["LATITUDE"],
        longitude=rainfall["LONGITUDE"],
        method="linear"
    )

    # Save regridded soil moisture
    output_file = f"soil_{year}_regridded.nc"

    soil_regridded.to_netcdf(output_file)

    print(f"{year} regridding complete!")
    print(f"Saved: {output_file}")

print("\nAll years regridded successfully!")