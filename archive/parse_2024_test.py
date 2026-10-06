import pdfplumber
import re
import pandas as pd

pdf = "ls25.pdf"
page_no = 27

records = []

with pdfplumber.open(pdf) as pdf_file:
    words = pdf_file.pages[page_no].extract_words()

rows = []
current = []

for w in words:
    if w["x0"] < 70 and re.fullmatch(r"\d+", w["text"]):
        if current:
            rows.append(current)
        current = [w]
    elif current:
        current.append(w)

if current:
    rows.append(current)

for row in rows:
    sno = row[0]["text"]
    row_text = " ".join(w["text"] for w in row)

    source_match = re.search(
        r"Newspapers\s*&\s*Media/2024/([^/]+/\d+)",
        row_text
    )
    source = (
        "Newspapers & Media/2024/" + source_match.group(1)
        if source_match else ""
    )

    district = " ".join(
        w["text"] for w in row
        if 300 <= w["x0"] < 350
        and w["text"] not in {"Newspapers", "&", "Media"}
    )

    name = " ".join(
        w["text"] for w in row
        if 350 <= w["x0"] < 407
    )

    location = " ".join(
        w["text"] for w in row
        if 407 <= w["x0"] < 470
    )

    lat = lon = date = event_type = ""

    for w in row:
        if re.fullmatch(r"-?\d+\.\d+", w["text"]):
            if lat == "":
                lat = w["text"]
            elif lon == "":
                lon = w["text"]

    for w in row:
        if re.fullmatch(r"\d{2}-\d{2}-\d{4}", w["text"]):
            date = w["text"]

    for i, w in enumerate(row):
        if w["text"].isdigit() and i + 2 < len(row):
            if (
                row[i+1]["text"].isdigit()
                and re.fullmatch(r"[\d.]+", row[i+2]["text"])
            ):
                event_type = w["text"]

    records.append({
        "S_NO": sno,
        "DATE": date,
        "LATITUDE": lat,
        "LONGITUDE": lon,
        "LOCATION": location,
        "DISTRICT": district,
        "LANDSLIDE_TYPE": event_type,
        "SOURCE": source
    })

df = pd.DataFrame(records)

print(df.to_string(index=False))
df.to_csv("test_2024_page28.csv", index=False)
print("\nSaved:", len(df), "records")
