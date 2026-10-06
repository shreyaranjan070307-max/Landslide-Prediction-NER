import xarray as xr
import numpy as np
from scipy.ndimage import generic_filter


# --------------------------------------------------
# 1. Load the regional GEBCO DEM
# --------------------------------------------------

dem = xr.open_dataset(
    "terrain_data/gebco_ner.nc"
)

elevation = dem["elevation"]

print("Elevation loaded!")
print("Shape:", elevation.shape)
print(
    "Resolution:",
    elevation.lat.diff("lat").mean().item()
)


# --------------------------------------------------
# 2. Calculate slope
# --------------------------------------------------

lat = elevation.lat.values
lon = elevation.lon.values
elevation_values = elevation.values

# Calculate elevation gradients with respect to degrees
dz_dlat, dz_dlon = np.gradient(
    elevation_values,
    lat,
    lon
)

# Convert degrees to metres.
# Latitude distance is approximately constant.
meters_per_degree_lat = 111320

# Longitude distance changes with latitude.
meters_per_degree_lon = (
    111320 * np.cos(np.radians(lat))
)

# Convert gradients from metres/degree
# to metres/metre.
dz_dy = dz_dlat / meters_per_degree_lat

dz_dx = (
    dz_dlon
    / meters_per_degree_lon[:, np.newaxis]
)

# Calculate slope
slope_radians = np.arctan(
    np.sqrt(dz_dx**2 + dz_dy**2)
)

slope_degrees = np.degrees(
    slope_radians
)

print("\nSlope calculated!")
print(
    "Minimum slope:",
    np.nanmin(slope_degrees)
)
print(
    "Maximum slope:",
    np.nanmax(slope_degrees)
)
print(
    "Mean slope:",
    np.nanmean(slope_degrees)
)


# --------------------------------------------------
# 3. Save slope
# --------------------------------------------------

slope = xr.DataArray(
    slope_degrees,
    coords={
        "lat": elevation.lat,
        "lon": elevation.lon
    },
    dims=["lat", "lon"],
    name="slope"
)

slope.attrs["units"] = "degrees"

slope.attrs["description"] = (
    "Terrain slope calculated from GEBCO "
    "elevation with latitude-dependent "
    "longitude distance correction"
)

slope.to_netcdf(
    "terrain_data/slope_gebco.nc"
)

print("\nSlope saved!")
print(
    "File: terrain_data/slope_gebco.nc"
)


# --------------------------------------------------
# 4. Calculate Terrain Ruggedness Index (TRI)
# --------------------------------------------------

def tri_function(window):

    center = window[4]

    neighbors = np.delete(
        window,
        4
    )

    return np.sqrt(
        np.mean(
            (neighbors - center) ** 2
        )
    )


tri_values = generic_filter(
    elevation_values,
    tri_function,
    size=3,
    mode="nearest"
)

tri = xr.DataArray(
    tri_values,
    coords={
        "lat": elevation.lat,
        "lon": elevation.lon
    },
    dims=["lat", "lon"],
    name="tri"
)

tri.attrs["units"] = "metres"

tri.attrs["description"] = (
    "RMS-based Terrain Ruggedness Index "
    "calculated from GEBCO elevation"
)

print("\nTRI calculated!")

print(
    "Minimum TRI:",
    np.nanmin(tri_values)
)

print(
    "Maximum TRI:",
    np.nanmax(tri_values)
)

print(
    "Mean TRI:",
    np.nanmean(tri_values)
)


# --------------------------------------------------
# 5. Check TRI distribution
# --------------------------------------------------

print("\nTRI percentiles:")

for p in [50, 75, 90, 95, 99, 99.9]:

    print(
        f"{p}th percentile:",
        np.nanpercentile(
            tri_values,
            p
        )
    )


# --------------------------------------------------
# 6. Save TRI
# --------------------------------------------------

tri.to_netcdf(
    "terrain_data/tri_gebco.nc"
)

print("\nTRI saved!")
print(
    "File: terrain_data/tri_gebco.nc"
)