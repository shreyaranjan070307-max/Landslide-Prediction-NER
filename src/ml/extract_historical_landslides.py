import os
import re
import math
import pandas as pd
import numpy as np
import pdfplumber

def clean_str(val):
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    return " ".join(s.split())

def standardize_state(raw_state, source_str=""):
    s = clean_str(raw_state).lower()
    src = clean_str(source_str).lower()

    state_map = {
        "arunachal pradesh": "Arunachal Pradesh",
        "aarunachal pradesh": "Arunachal Pradesh",
        "arunachal": "Arunachal Pradesh",
        "assam": "Assam",
        "manipur": "Manipur",
        "meghalaya": "Meghalaya",
        "meghalaya jaintia": "Meghalaya",
        "mizoram": "Mizoram",
        "nagaland": "Nagaland",
        "sikkim": "Sikkim",
        "tripura": "Tripura"
    }

    if s in state_map:
        return state_map[s]

    for key, official in state_map.items():
        if key in s or key in src:
            return official

    return clean_str(raw_state)

def extract_2020():
    print("Extracting 2020 data...")
    df = pd.read_csv("SLI2020_records (1).csv")
    records = []
    for idx, row in df.iterrows():
        d_raw = clean_str(row.get("Date_of_Event", ""))
        d_val = ""
        if d_raw:
            try:
                dt = pd.to_datetime(d_raw, dayfirst=True)
                d_val = dt.strftime("%Y-%m-%d")
            except Exception:
                d_val = ""

        lat_val = float(row["Lat"]) if pd.notna(row.get("Lat")) else None
        lon_val = float(row["Long"]) if pd.notna(row.get("Long")) else None

        loc_val = clean_str(row.get("Name", ""))
        if not loc_val:
            loc_val = clean_str(row.get("Location", ""))

        dist_val = clean_str(row.get("District", ""))
        st_raw = clean_str(row.get("State", ""))
        src_val = clean_str(row.get("Slide_ID", ""))
        if not src_val:
            src_val = clean_str(row.get("Source", ""))

        st_val = standardize_state(st_raw, src_val)
        ltype_val = clean_str(row.get("Type", ""))

        records.append({
            "DATE": d_val,
            "LATITUDE": lat_val,
            "LONGITUDE": lon_val,
            "LOCATION": loc_val,
            "DISTRICT": dist_val,
            "STATE": st_val,
            "LANDSLIDE_TYPE": ltype_val,
            "SOURCE": src_val,
            "RAW_DATE": d_raw,
            "YEAR": 2020,
            "ORIGINAL_INDEX": idx + 1
        })
    print(f"2020 total records extracted: {len(records)}")
    return records

def extract_2021():
    print("Extracting 2021 data...")
    df_sih = pd.read_csv("sih_historical_landslide_records.csv")
    df2021 = df_sih[pd.to_datetime(df_sih["DATE"], errors="coerce").dt.year == 2021].copy()
    records = []
    for idx, row in df2021.iterrows():
        records.append({
            "DATE": clean_str(row["DATE"]),
            "LATITUDE": float(row["LATITUDE"]) if pd.notna(row["LATITUDE"]) else None,
            "LONGITUDE": float(row["LONGITUDE"]) if pd.notna(row["LONGITUDE"]) else None,
            "LOCATION": clean_str(row["LOCATION"]),
            "DISTRICT": clean_str(row["DISTRICT"]),
            "STATE": standardize_state(clean_str(row["STATE"]), clean_str(row["SOURCE"])),
            "LANDSLIDE_TYPE": clean_str(row["LANDSLIDE_TYPE"]),
            "SOURCE": clean_str(row["SOURCE"]),
            "RAW_DATE": clean_str(row["DATE"]),
            "YEAR": 2021,
            "ORIGINAL_INDEX": idx + 1
        })
    print(f"2021 total records extracted: {len(records)}")
    return records

def extract_2022():
    print("Extracting 2022 data from FINAL2022 landslide report2.pdf...")
    pdf_path = "FINAL2022 landslide report2.pdf"
    summary_recs = []
    with pdfplumber.open(pdf_path) as pdf:
        for p_num in range(16, 28):
            text = pdf.pages[p_num-1].extract_text() or ""
            for line in text.splitlines():
                line_str = line.strip()
                m = re.search(r'([A-Za-z0-9_&]+(?:/[A-Za-z0-9_& ]+)+/\d+)\s+([A-Za-z0-9_& ]+?)\s+([A-Za-z ]+?)\s+([A-Za-z0-9 ]+?)\s+(\d{2}-\d{2}-\d{4})\s+(\d+)', line_str)
                if m:
                    sid = " ".join(m.group(1).strip().split())
                    src = m.group(2).strip()
                    st = m.group(3).strip()
                    dist = m.group(4).strip()
                    dt_str = m.group(5).strip()
                    ltype = m.group(6).strip()
                    summary_recs.append({
                        "id": sid,
                        "source": src,
                        "state": st,
                        "district": dist,
                        "date_raw": dt_str,
                        "type": ltype
                    })

    cards = {}
    with pdfplumber.open(pdf_path) as pdf:
        for p_num in range(29, 52):
            words = pdf.pages[p_num-1].extract_words()
            for col_name, x_min, x_max in [('left', 0, 300), ('right', 300, 1000)]:
                col_words = [w for w in words if x_min <= w['x0'] < x_max]
                col_words.sort(key=lambda w: (w['top'], w['x0']))
                
                lines_dict = {}
                for w in col_words:
                    top_round = round(w['top'] / 3) * 3
                    lines_dict.setdefault(top_round, []).append(w['text'])
                
                col_text = '\n'.join(' '.join(lines_dict[top_val]) for top_val in sorted(lines_dict.keys()))
                chunks = re.split(r'(?=Slide\s+ID)', col_text)
                for chunk in chunks:
                    if 'Slide ID' not in chunk:
                        continue
                    m = re.search(r'Slide\s+ID\s+(.*?)(?=\s+Source|\s+Slide No|\n\s*Source|\n\s*Slide No)', chunk, re.DOTALL)
                    if m:
                        sid = " ".join(m.group(1).strip().split())
                        
                        def get_card_field(pattern):
                            cm = re.search(pattern, chunk, re.IGNORECASE)
                            return cm.group(1).strip() if cm else ""
                            
                        cards[sid] = {
                            "lat": get_card_field(r'Lat\(dd\)\s+([-0-9.]+)'),
                            "lon": get_card_field(r'Lon\(dd\)\s+([-0-9.]+)'),
                            "location": get_card_field(r'Location\s+(.*?)(?=\s+NH/SH|\s+Lat|\n|$)'),
                            "name": get_card_field(r'Name\s+(.*?)(?=\s+Location|\s+NH/SH|\n|$)'),
                            "district": get_card_field(r'District\s+(.*?)(?=\s+Name|\s+Location|\n|$)'),
                            "state": get_card_field(r'State\s+(.*?)(?=\s+District|\n|$)'),
                            "date": get_card_field(r'Date of Event\s+(\d{2}-\d{2}-\d{4})'),
                            "type": get_card_field(r'Type of Event\s+(\d+)')
                        }

    records = []
    for idx, s in enumerate(summary_recs):
        sid = s["id"]
        card = cards.get(sid, {})
        
        d_raw = s["date_raw"]
        d_val = ""
        try:
            dt = pd.to_datetime(d_raw, format="%d-%m-%Y")
            d_val = dt.strftime("%Y-%m-%d")
        except Exception:
            d_val = d_raw

        lat_val = float(card["lat"]) if card.get("lat") else None
        lon_val = float(card["lon"]) if card.get("lon") else None
        
        name_str = card.get("name", "")
        loc_str = card.get("location", "")
        loc_val = f"{name_str} {loc_str}".strip() if name_str and loc_str else (name_str or loc_str)
        
        dist_val = card.get("district", "") or s["district"]
        st_raw = card.get("state", "") or s["state"]
        st_val = standardize_state(st_raw, sid)
        type_val = card.get("type", "") or s["type"]
        
        records.append({
            "DATE": d_val,
            "LATITUDE": lat_val,
            "LONGITUDE": lon_val,
            "LOCATION": loc_val,
            "DISTRICT": dist_val,
            "STATE": st_val,
            "LANDSLIDE_TYPE": type_val,
            "SOURCE": sid,
            "RAW_DATE": d_raw,
            "YEAR": 2022,
            "ORIGINAL_INDEX": idx + 1
        })
    print(f"2022 total records extracted: {len(records)}")
    return records

def extract_2023():
    print("Extracting 2023 data from Seasonal_LS_Inventory_2023_Report.pdf...")
    pdf_path = "Seasonal_LS_Inventory_2023_Report.pdf"
    summary_recs = []
    with pdfplumber.open(pdf_path) as pdf:
        for p_num in range(22, 34):
            text = pdf.pages[p_num-1].extract_text() or ""
            for line in text.splitlines():
                line_str = line.strip()
                m = re.search(r'(Newspapers\s*&\s*Media/2023/([^/]+)/(\d+))\s+(.*?)\s+([A-Za-z0-9 ]+?)\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+(\d+)', line_str)
                if m:
                    sid = " ".join(m.group(1).split())
                    st = m.group(2).strip()
                    src = m.group(4).strip()
                    dist = m.group(5).strip()
                    dt_str = m.group(6).strip()
                    ltype = m.group(7).strip()
                    summary_recs.append({
                        "id": sid,
                        "state": st,
                        "source": "Newspapers & Media",
                        "district": dist,
                        "date_raw": dt_str,
                        "type": ltype
                    })

    cards = {}
    with pdfplumber.open(pdf_path) as pdf:
        for p_num in range(34, len(pdf.pages)+1):
            words = pdf.pages[p_num-1].extract_words()
            for col_name, x_min, x_max in [('left', 0, 300), ('right', 300, 1000)]:
                col_words = [w for w in words if x_min <= w['x0'] < x_max]
                col_words.sort(key=lambda w: (w['top'], w['x0']))
                
                lines_dict = {}
                for w in col_words:
                    top_round = round(w['top'] / 3) * 3
                    lines_dict.setdefault(top_round, []).append(w['text'])
                
                col_text = '\n'.join(' '.join(lines_dict[top_val]) for top_val in sorted(lines_dict.keys()))
                chunks = re.split(r'(?=Slide\s+ID)', col_text)
                for chunk in chunks:
                    if 'Slide ID' not in chunk:
                        continue
                    m = re.search(r'Slide\s+ID\s+(.*?)(?=\s+Source|\s+Slide No|\n\s*Source|\n\s*Slide No)', chunk, re.DOTALL)
                    if m:
                        sid = " ".join(m.group(1).strip().split())
                        
                        def get_card_field(pattern):
                            cm = re.search(pattern, chunk, re.IGNORECASE)
                            return cm.group(1).strip() if cm else ""
                            
                        cards[sid] = {
                            "lat": get_card_field(r'Lat\s*\(dd\)\s+([-0-9.]+)'),
                            "lon": get_card_field(r'Lon\s*\(dd\)\s+([-0-9.]+)'),
                            "location": get_card_field(r'Location\s+(.*?)(?=\s+NH/SH|\s+Lat|\n|$)'),
                            "name": get_card_field(r'Name\s+(.*?)(?=\s+Location|\s+NH/SH|\n|$)'),
                            "district": get_card_field(r'District\s+(.*?)(?=\s+Name|\s+Location|\n|$)'),
                            "state": get_card_field(r'State\s+(.*?)(?=\s+District|\n|$)'),
                            "date": get_card_field(r'Date of Event\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})'),
                            "type": get_card_field(r'Type of Event\s+(\d+)')
                        }

    records = []
    all_2023_ids = list(set([s["id"] for s in summary_recs] + list(cards.keys())))

    for idx, sid in enumerate(all_2023_ids):
        summary_match = next((s for s in summary_recs if s["id"] == sid), {})
        card = cards.get(sid, {})
        
        d_raw = card.get("date", "") or summary_match.get("date_raw", "")
        d_val = ""
        try:
            dt = pd.to_datetime(d_raw, dayfirst=True)
            d_val = dt.strftime("%Y-%m-%d")
        except Exception:
            d_val = d_raw
            
        lat_val = float(card["lat"]) if card.get("lat") else None
        lon_val = float(card["lon"]) if card.get("lon") else None
        
        name_str = card.get("name", "")
        loc_str = card.get("location", "")
        loc_val = f"{name_str} {loc_str}".strip() if name_str and loc_str else (name_str or loc_str)
        
        dist_val = card.get("district", "") or summary_match.get("district", "")
        st_raw = card.get("state", "") or summary_match.get("state", "")
        if not st_raw and "/2023/" in sid:
            st_raw = sid.split("/2023/")[1].split("/")[0]
            
        st_val = standardize_state(st_raw, sid)
        type_val = card.get("type", "") or summary_match.get("type", "")
        
        records.append({
            "DATE": d_val,
            "LATITUDE": lat_val,
            "LONGITUDE": lon_val,
            "LOCATION": loc_val,
            "DISTRICT": dist_val,
            "STATE": st_val,
            "LANDSLIDE_TYPE": type_val,
            "SOURCE": sid,
            "RAW_DATE": d_raw,
            "YEAR": 2023,
            "ORIGINAL_INDEX": idx + 1
        })

    print(f"2023 total records extracted: {len(records)}")
    return records

def extract_2024():
    print("Extracting 2024 data from ls25.pdf...")
    pdf_path = "ls25.pdf"
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        rec_idx = 0
        for page_idx in range(27, 44):
            page = pdf.pages[page_idx]
            words = page.extract_words()
            
            row_anchors = [w for w in words if w['x0'] < 65 and re.fullmatch(r'\d+', w['text']) and w['top'] > 80]
            row_anchors.sort(key=lambda w: w['top'])
            
            for i, anchor in enumerate(row_anchors):
                top_min = anchor['top'] - 3
                top_max = row_anchors[i+1]['top'] - 3 if i + 1 < len(row_anchors) else 1000
                row_words = [w for w in words if top_min <= w['top'] < top_max]
                row_words.sort(key=lambda w: (w['top'], w['x0']))
                
                def get_text_in_x(x_start, x_end):
                    w_list = [w for w in row_words if x_start <= w['x0'] < x_end]
                    w_list.sort(key=lambda w: (w['top'], w['x0']))
                    return " ".join(w['text'] for w in w_list).strip()
                
                full_row_text = " ".join(w['text'] for w in row_words)
                
                id_match = re.search(r'(Newspapers\s*&\s*Media/2024/[^/]+/\d+|GSI_[^\s]+|SDMA_[^\s]+|field_visit_[^\s]+|satellite_[^\s]+)', full_row_text)
                full_id = id_match.group(1).strip() if id_match else get_text_in_x(60, 200)
                
                st_match = re.search(r'/2024/([^/]+)/\d+', full_id)
                raw_state_in_id = st_match.group(1).strip() if st_match else ""
                st_val = standardize_state(raw_state_in_id, full_id)
                
                district = get_text_in_x(300, 355)
                name = get_text_in_x(355, 410)
                location = get_text_in_x(410, 475)
                
                floats = re.findall(r'-?\d+\.\d+', full_row_text)
                lat_val = float(floats[0]) if len(floats) >= 1 else None
                lon_val = float(floats[1]) if len(floats) >= 2 else None
                
                date_match = re.search(r'(\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})', full_row_text)
                d_raw = date_match.group(1) if date_match else ""
                d_val = ""
                try:
                    dt = pd.to_datetime(d_raw, dayfirst=True)
                    d_val = dt.strftime("%Y-%m-%d")
                except Exception:
                    d_val = d_raw
                    
                type_str = get_text_in_x(695, 730)
                if not type_str:
                    t_match = re.search(r'\d{2}-\d{2}-\d{4}\s+(?:\d{2}:\d{2})?\s+(\d+)', full_row_text)
                    type_str = t_match.group(1) if t_match else ""
                    
                loc_combined = f"{name} {location}".strip() if name and location else (name or location)
                
                rec_idx += 1
                records.append({
                    "DATE": d_val,
                    "LATITUDE": lat_val,
                    "LONGITUDE": lon_val,
                    "LOCATION": loc_combined,
                    "DISTRICT": district,
                    "STATE": st_val,
                    "LANDSLIDE_TYPE": type_str,
                    "SOURCE": full_id,
                    "RAW_DATE": d_raw,
                    "YEAR": 2024,
                    "ORIGINAL_INDEX": rec_idx
                })

    print(f"2024 total records extracted: {len(records)}")
    return records

def extract_2025():
    print("Extracting 2025 data...")
    df_sih = pd.read_csv("sih_historical_landslide_records.csv")
    df2025 = df_sih[pd.to_datetime(df_sih["DATE"], errors="coerce").dt.year == 2025].copy()
    records = []
    for idx, row in df2025.iterrows():
        records.append({
            "DATE": clean_str(row["DATE"]),
            "LATITUDE": float(row["LATITUDE"]) if pd.notna(row["LATITUDE"]) else None,
            "LONGITUDE": float(row["LONGITUDE"]) if pd.notna(row["LONGITUDE"]) else None,
            "LOCATION": clean_str(row["LOCATION"]),
            "DISTRICT": clean_str(row["DISTRICT"]),
            "STATE": standardize_state(clean_str(row["STATE"]), clean_str(row["SOURCE"])),
            "LANDSLIDE_TYPE": clean_str(row["LANDSLIDE_TYPE"]),
            "SOURCE": clean_str(row["SOURCE"]),
            "RAW_DATE": clean_str(row["DATE"]),
            "YEAR": 2025,
            "ORIGINAL_INDEX": idx + 1
        })
    print(f"2025 total records extracted: {len(records)}")
    return records

def main():
    all_recs = []
    all_recs.extend(extract_2020())
    all_recs.extend(extract_2021())
    all_recs.extend(extract_2022())
    all_recs.extend(extract_2023())
    all_recs.extend(extract_2024())
    all_recs.extend(extract_2025())

    df_master_full = pd.DataFrame(all_recs)
    print(f"\nTotal master records extracted: {len(df_master_full)}")

    master_cols = ["DATE", "LATITUDE", "LONGITUDE", "LOCATION", "DISTRICT", "STATE", "LANDSLIDE_TYPE", "SOURCE"]
    df_master = df_master_full[master_cols].copy()

    master_path = "historical_landslides_master.csv"
    df_master.to_csv(master_path, index=False)
    print(f"Saved master dataset: {master_path}")

    # Build Audit
    audit_rows = []
    for idx, row in df_master_full.iterrows():
        flags = []
        d_val = row["DATE"]
        lat = row["LATITUDE"]
        lon = row["LONGITUDE"]
        src = row["SOURCE"]
        yr = row["YEAR"]

        # Date validation
        if not d_val or d_val == "":
            flags.append("MISSING_DATE")
        elif "16-06-2020" in row["RAW_DATE"] or "2020-06-16" in d_val:
            if yr == 2022 or "2022" in src:
                flags.append("SUSPICIOUS_DATE_2020_IN_2022_SOURCE")
        else:
            try:
                y = int(d_val.split("-")[0])
                if y < 2020 or y > 2025:
                    flags.append(f"DATE_OUT_OF_BOUNDS_{y}")
            except Exception:
                flags.append("UNPARSEABLE_DATE_FORMAT")

        # Coordinate validation for NE India (Lat: 20-30°N, Lon: 87-97°E approx)
        if pd.isna(lat) or lat is None:
            flags.append("MISSING_LATITUDE")
        elif lat < 20.0 or lat > 32.0:
            flags.append("IMPOSSIBLE_LATITUDE")

        if pd.isna(lon) or lon is None:
            flags.append("MISSING_LONGITUDE")
        elif lon < 85.0 or lon > 98.0:
            flags.append("IMPOSSIBLE_LONGITUDE")

        if not row["LOCATION"]:
            flags.append("MISSING_LOCATION")
        if not row["DISTRICT"]:
            flags.append("MISSING_DISTRICT")
        if not row["STATE"]:
            flags.append("MISSING_STATE")
        if not row["LANDSLIDE_TYPE"]:
            flags.append("MISSING_LANDSLIDE_TYPE")

        audit_rows.append({
            "ROW_ID": idx + 1,
            "YEAR": yr,
            "DATE": d_val,
            "RAW_DATE": row["RAW_DATE"],
            "LATITUDE": lat,
            "LONGITUDE": lon,
            "LOCATION": row["LOCATION"],
            "DISTRICT": row["DISTRICT"],
            "STATE": row["STATE"],
            "LANDSLIDE_TYPE": row["LANDSLIDE_TYPE"],
            "SOURCE": src,
            "AUDIT_FLAGS": "; ".join(flags) if flags else "OK"
        })

    df_audit = pd.DataFrame(audit_rows)

    # Check duplicates
    dup_mask = df_master.duplicated(subset=["DATE", "LATITUDE", "LONGITUDE", "LOCATION", "DISTRICT", "STATE"], keep=False)
    for idx, is_dup in enumerate(dup_mask):
        if is_dup:
            existing = df_audit.at[idx, "AUDIT_FLAGS"]
            flag_str = "DUPLICATE_RECORD_CANDIDATE"
            df_audit.at[idx, "AUDIT_FLAGS"] = f"{existing}; {flag_str}" if existing != "OK" else flag_str

    audit_csv_path = "historical_landslides_audit.csv"
    df_audit.to_csv(audit_csv_path, index=False)
    print(f"Saved audit CSV: {audit_csv_path}")

    # Build Markdown Audit Report
    year_counts = df_master_full["YEAR"].value_counts().sort_index()
    state_year_tbl = pd.crosstab(df_master_full["STATE"], df_master_full["YEAR"], margins=True)

    audit_md = []
    audit_md.append("# HISTORICAL LANDSLIDE DATASET AUDIT REPORT\n")
    audit_md.append("## 1. Summary of Records by Year\n")
    audit_md.append("| Year | Record Count | Valid Dates | Missing/Unparseable Dates |")
    audit_md.append("|---|---|---|---|")
    total_valid = 0
    total_recs = len(df_master_full)
    for y in sorted(df_master_full["YEAR"].unique()):
        sub = df_master_full[df_master_full["YEAR"] == y]
        v_cnt = sum(1 for d in sub["DATE"] if d != "")
        m_cnt = len(sub) - v_cnt
        total_valid += v_cnt
        audit_md.append(f"| **{y}** | {len(sub)} | {v_cnt} | {m_cnt} |")
    audit_md.append(f"| **TOTAL** | **{total_recs}** | **{total_valid}** | **{total_recs - total_valid}** |\n")

    audit_md.append("## 2. State-wise Distribution by Year\n")
    def df_to_md_table(df_tbl):
        headers = ["STATE"] + [str(c) for c in df_tbl.columns]
        header_row = "| " + " | ".join(headers) + " |"
        sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        body_rows = []
        for index, row in df_tbl.iterrows():
            r_str = "| " + str(index) + " | " + " | ".join(str(v) for v in row.values) + " |"
            body_rows.append(r_str)
        return "\n".join([header_row, sep_row] + body_rows)

    audit_md.append(df_to_md_table(state_year_tbl))
    audit_md.append("\n")

    audit_md.append("## 3. Data Quality & Audit Observations\n")
    audit_md.append(f"* **Total Master Rows**: {total_recs}")
    audit_md.append(f"* **Exact Duplicate Rows**: {df_master.duplicated().sum()}")
    audit_md.append(f"* **Date + Location Duplicates**: {df_master.duplicated(subset=['DATE', 'LATITUDE', 'LONGITUDE', 'LOCATION']).sum()}")
    audit_md.append(f"* **Missing Latitudes**: {df_master['LATITUDE'].isna().sum()}")
    audit_md.append(f"* **Missing Longitudes**: {df_master['LONGITUDE'].isna().sum()}")
    audit_md.append(f"* **Missing Locations**: {(df_master['LOCATION'] == '').sum()}")
    audit_md.append(f"* **Missing Districts**: {(df_master['DISTRICT'] == '').sum()}")
    audit_md.append(f"* **Suspicious Date Record**: `Newspapers&Media/2022/Meghalaya/115` has table date `16-06-2020` in 2022 report source. Preserved as `16-06-2020` / `2020-06-16` and flagged.")
    audit_md.append(f"* **2020 Date Parsing Note**: 10 records in 2020 source had non-standard text dates (e.g. 'Last week of June'). Preserved with empty `DATE` in master and flagged in audit.\n")

    audit_md_path = "historical_landslides_audit.md"
    with open(audit_md_path, "w") as f:
        f.write("\n".join(audit_md))
    print(f"Saved audit Markdown: {audit_md_path}")

    # Phase 2: Environmental Matching
    print("\n=== PHASE 2: ENVIRONMENTAL DATA MATCHING ===")
    df_env = pd.read_parquet("rainfall_soil_ndvi_terrain_2020_2025.parquet")
    grid_cells = set(zip(df_env["LATITUDE"].round(2), df_env["LONGITUDE"].round(2)))
    grid_lats = np.array(sorted(df_env["LATITUDE"].unique()))
    grid_lons = np.array(sorted(df_env["LONGITUDE"].unique()))

    # Build quick lookup dictionary for env rows
    # Key: (TIME_str, round_lat, round_lon) -> row index or dict of features
    env_feature_cols = [
        "Daily_Rain_mm", "Rain_3Day_mm", "Rain_7Day_mm", "Rain_15Day_mm", "Rain_30Day_mm",
        "Soil_Moisture", "NDVI", "elevation_mean", "elevation_range", "elevation_std",
        "slope_mean", "slope_max", "slope_std", "slope_pct_above_30", "tri_mean", "tri_p95", "tri_std"
    ]

    df_env["TIME_STR"] = df_env["TIME"].dt.strftime("%Y-%m-%d")
    df_env["LAT_R"] = df_env["LATITUDE"].round(2)
    df_env["LON_R"] = df_env["LONGITUDE"].round(2)

    # Set multi-index for fast lookup
    df_env_indexed = df_env.set_index(["TIME_STR", "LAT_R", "LON_R"])

    matched_spatial = 0
    matched_temporal = 0
    matched_both = 0
    complete_env_rows = 0
    missing_env_windows = 0

    for idx, row in df_master_full.iterrows():
        lat = row["LATITUDE"]
        lon = row["LONGITUDE"]
        d_val = row["DATE"]

        # Spatial check
        s_match = False
        grid_lat, grid_lon = None, None
        if pd.notna(lat) and pd.notna(lon):
            best_lat = round(grid_lats[np.abs(grid_lats - lat).argmin()], 2)
            best_lon = round(grid_lons[np.abs(grid_lons - lon).argmin()], 2)
            if abs(best_lat - lat) <= 0.25 and abs(best_lon - lon) <= 0.25:
                if (best_lat, best_lon) in grid_cells:
                    s_match = True
                    grid_lat, grid_lon = best_lat, best_lon

        if s_match:
            matched_spatial += 1

        # Temporal check
        t_match = False
        if d_val and d_val != "":
            try:
                y = int(d_val.split("-")[0])
                if 2020 <= y <= 2025:
                    t_match = True
            except Exception:
                pass

        if t_match:
            matched_temporal += 1

        if s_match and t_match:
            matched_both += 1
            # Check environmental features in parquet
            try:
                env_row = df_env_indexed.loc[(d_val, grid_lat, grid_lon)]
                if isinstance(env_row, pd.DataFrame):
                    env_row = env_row.iloc[0]

                has_null = False
                for col in env_feature_cols:
                    if pd.isna(env_row[col]):
                        has_null = True
                        break

                if not has_null:
                    complete_env_rows += 1
                else:
                    missing_env_windows += 1
            except KeyError:
                missing_env_windows += 1

    print(f"Historical events: {len(df_master_full)}")
    print(f"Matched spatially: {matched_spatial}")
    print(f"Matched temporally: {matched_temporal}")
    print(f"Matched both spatially and temporally: {matched_both}")
    print(f"Complete environmental feature rows: {complete_env_rows}")
    print(f"Number lost because of missing environmental windows/features: {missing_env_windows}")
    print(f"Final usable labelled samples: {complete_env_rows}")

if __name__ == "__main__":
    main()
