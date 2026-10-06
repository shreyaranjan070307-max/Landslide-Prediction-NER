import pandas as pd

# ============================================================
# 1. READ THE TWO HISTORICAL LANDSLIDE FILES
# ============================================================

file_2020 = "SLI2020_records (1).csv"
file_other = "sih_historical_landslide_records.csv"

df2020 = pd.read_csv(file_2020)
df_other = pd.read_csv(file_other)

print("2020 records:", len(df2020))
print("2021/2025 records:", len(df_other))


# ============================================================
# 2. CONVERT 2020 DATA TO OUR COMMON FORMAT
# ============================================================

df2020_clean = pd.DataFrame({
    "DATE": pd.to_datetime(
        df2020["Date_of_Event"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d"),

    "LATITUDE": pd.to_numeric(
        df2020["Lat"],
        errors="coerce"
    ),

    "LONGITUDE": pd.to_numeric(
        df2020["Long"],
        errors="coerce"
    ),

    "LOCATION": df2020["Name"],

    "DISTRICT": df2020["District"],

    "STATE": df2020["State"],

    "LANDSLIDE_TYPE": df2020["Type"].astype(str),

    "SOURCE": df2020["Source"]
})


# ============================================================
# 3. STANDARDIZE 2021/2025 DATA
# ============================================================

df_other_clean = df_other[
    [
        "DATE",
        "LATITUDE",
        "LONGITUDE",
        "LOCATION",
        "DISTRICT",
        "STATE",
        "LANDSLIDE_TYPE",
        "SOURCE"
    ]
].copy()


# ============================================================
# 4. COMBINE EVERYTHING
# ============================================================

master = pd.concat(
    [df2020_clean, df_other_clean],
    ignore_index=True
)


# ============================================================
# 5. REMOVE TRUE DUPLICATES
#    Ignore SOURCE when determining duplicates
# ============================================================

duplicate_columns = [
    "DATE",
    "LATITUDE",
    "LONGITUDE",
    "LOCATION",
    "DISTRICT",
    "STATE",
    "LANDSLIDE_TYPE"
]

duplicate_count = master.duplicated(
    subset=duplicate_columns,
    keep="first"
).sum()

master = master.drop_duplicates(
    subset=duplicate_columns,
    keep="first"
)


# ============================================================
# 6. CHECK NORTHEAST INDIA STATES
# ============================================================

ner_states = {
    "Arunachal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura"
}

ner_mask = master["STATE"].isin(ner_states)


# ============================================================
# 7. CHECK MISSING VALUES
# ============================================================

missing_values = master.isna().sum()


# ============================================================
# 8. CHECK COORDINATES
# ============================================================

bad_latitude = (
    (master["LATITUDE"] < 6) |
    (master["LATITUDE"] > 37) |
    master["LATITUDE"].isna()
)

bad_longitude = (
    (master["LONGITUDE"] < 68) |
    (master["LONGITUDE"] > 98) |
    master["LONGITUDE"].isna()
)

bad_coordinates = bad_latitude | bad_longitude


# ============================================================
# 9. SAVE MASTER DATASET
# ============================================================

output_file = "historical_landslides_master.csv"

master.to_csv(
    output_file,
    index=False
)


# ============================================================
# 10. PRINT AUDIT REPORT
# ============================================================

print("\n" + "=" * 55)
print("HISTORICAL LANDSLIDE MASTER DATASET AUDIT")
print("=" * 55)

print("\nTotal records before duplicate removal:")
print(len(df2020_clean) + len(df_other_clean))

print("\nDuplicate rows:")
print(duplicate_count)

print("\nTotal records after duplicate removal:")
print(len(master))

print("\nNortheast India records:")
print(ner_mask.sum())

print("\nYearly distribution:")
print(
    pd.to_datetime(master["DATE"]).dt.year
    .value_counts()
    .sort_index()
)

print("\nMissing values:")
print(missing_values)

print("\nRecords with malformed/out-of-range coordinates:")
print(bad_coordinates.sum())

print("\nCoordinate rules:")
print("Latitude  : 6 to 37")
print("Longitude : 68 to 98")

print("\nState distribution:")
print(master["STATE"].value_counts())

print("\nSource distribution:")
print(master["SOURCE"].value_counts())

print("\nSaved:")
print(output_file)

print("\n" + "=" * 55)
print("DONE")
print("=" * 55)
