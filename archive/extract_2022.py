import pdfplumber
import re
import pandas as pd

PDF = "FINAL2022 landslide report2.pdf"
OUTPUT = "landslides_2022_extracted.csv"

records = []

with pdfplumber.open(PDF) as pdf:
    for page_no, page in enumerate(pdf.pages, 1):
        text = page.extract_text() or ""

        # A record begins with "State ..." and ends just before the next "State ..."
        chunks = re.split(r'(?=State\s+[A-Za-z])', text)

        for chunk in chunks:
            if "Slide ID " not in chunk or "Lat(dd)" not in chunk:
                continue

            def get(pattern):
                m = re.search(pattern, chunk)
                return m.group(1).strip() if m else ""

            record = {
                "DATE": get(r"Date of Event\s+([0-9]{2}-[0-9]{2}-[0-9]{4})"),
                "LATITUDE": get(r"Lat\(dd\)\s+([-0-9.]+)"),
                "LONGITUDE": get(r"Lon\(dd\)\s+([-0-9.]+)"),
                "LOCATION": get(r"Location\s*(.*?)(?=\s+NH/SH affected)"),
                "DISTRICT": get(r"District\s+(.+?)(?=\s+Name\s+)"),
                "STATE": get(r"State\s+(.+?)(?=\s+District\s+)"),
                "LANDSLIDE_TYPE": get(r"Type of Event\s+(\d+)"),
                "SOURCE": get(r"Source\s+(.+?)(?=\s+Slide No)"),
            }

            if record["LATITUDE"] and record["LONGITUDE"] and record["STATE"]:
                records.append(record)

df = pd.DataFrame(records)

# Remove exact duplicate records
df = df.drop_duplicates()

df.to_csv(OUTPUT, index=False)

print("Extracted records:", len(df))
print("Columns:", list(df.columns))
print("\nRecords by state:")
print(df["STATE"].value_counts())
print("\nMissing values:")
print(df.isna().sum())
print("\nSaved:", OUTPUT)
