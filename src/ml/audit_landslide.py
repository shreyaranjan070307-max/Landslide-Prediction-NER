import csv
from datetime import datetime

raw_rows = [
    "2021-06-08,27.241524,93.335972,Leporiang,Papum Pare,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-08-13,28.849609,94.748649,Between Tuting and Yingkiong,Upper Siang,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-08-13,28.122053,95.274842,near Sirki waterfall,East Siang,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-08-13,27.784222,94.721322,Between Likabali and Basar,West Siang,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-06-27,28.153611,95.181369,Rotung Village at Kebang,East Siang,Arunachal Pradesh,Type 1,NESAC-SR-277-2022",
    "2021-06-17,28.936253,94.842537,Pekong Village,Upper Siang,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-07-08,27.965813,94.467809,Tode Village,Upper Subansiri,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-06-05,27.326763,92.438010,77.200 km in BCT road near Saddle,West Kameng,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-05-31,27.095983,93.622322,Near Indira Gandhi Park entry gate,Papum Pare,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-05-25,27.208119,92.479767,80.3-km between Nechiphu and Saddle,West Kameng,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-06-22,26.911944,95.603611,Kuthong Village,Tirap,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-06-30,28.214774,95.235101,Pasighat to Yingkiong (100 kms away),Upper Siang,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-06-30,27.796145,94.713350,near Garu 25 km from Likabali,West Siang,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-04-28,27.186597,92.303984,between Membachur and Garbow,West Kameng,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-06-27,28.233722,94.996300,Sangam Bridge Collapse near Pangin,East Siang,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-09-09,27.794025,94.073954,Raga headquarters,Lower Subansiri,Arunachal Pradesh,Type 3,NESAC-SR-277-2022",
    "2021-09-20,27.104442,92.566072,20 locations along BCT Road,West Kameng,Arunachal Pradesh,Type 2,NESAC-SR-277-2022",
    "2021-06-18,26.162784,91.694636,Water Works Colony,Kamrup metro,Assam,Type 2,NESAC-SR-277-2022",
    "2021-08-25,26.574761,93.110996,Kaliabor,Nagaon,Assam,Type 3,NESAC-SR-277-2022",
    "2021-10-20,26.170251,91.690161,Guwahati,Kamrup metro,Assam,Type 2,NESAC-SR-277-2022",
    "2021-08-06,26.154238,91.810523,Borbari,Kamrup metro,Assam,Type 2,NESAC-SR-277-2022",
    "2025-05-30,25.679230,91.899880,Umiam Landslide 7,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.686720,91.903400,Umbang Landslide,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.686240,91.902820,Umbang Landslide 2,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.690240,91.905340,Sumer Landslide 1,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.758520,91.879990,Umsamlem Landslide,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.823080,91.872420,Kwinain Landslide,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.814880,91.875710,Umnget Landslide,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.926830,91.875210,Umling Landslide,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.927230,91.875060,Umling Landslide 2,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.958570,91.864670,Umling Landslide 3,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-05-30,25.957100,91.861250,Umling Landslide 4,Ri Bhoi,Meghalaya,Verified,Landslide-Field-Survey-2025",
    "2025-02-26,28.788330,95.909020,Near Anini NH 313,Dibang Valley,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-03-04,28.628870,95.856600,KM5 from Etalin along NH-313,Dibang Valley,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-03-12,28.788460,95.908840,Near Anini NH 313,Dibang Valley,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-04-02,28.038260,96.438060,Located close to the Indo-China border,Anjaw,Arunachal Pradesh,Type 3,NESAC-SR-392-2026",
    "2025-05-30,27.076510,93.656950,Near Gyan Mission Orphan School,Papum Pare,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-05-30,27.183320,92.599520,Jamiri Landslide NH 13,West Kameng,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-05-30,27.306160,92.953880,Bana Seppa Road NH 13,East Kameng,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-05-31,27.622060,93.840960,Ziro Kamle Road NH 13,Lower Subansiri,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-06-01,27.649590,93.873850,Param Putu Circle,Keyi Panyor,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-06-03,27.718880,94.703990,Along Likabali-Basar Road,Lower Siang,Arunachal Pradesh,Type 3,NESAC-SR-392-2026",
    "2025-06-15,27.798370,94.076500,Govt Higher Secondary School in Raga,Kamle,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-06-25,27.514130,92.809880,between Lada and Sachung,East Kameng,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-06-29,27.066530,92.592470,road connecting Tippi and Elephant Flat,West Kameng,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-04-01,28.771130,94.855870,Between Janbo and Bomdo Village,Upper Siang,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-04-02,28.805550,94.801390,Mosing Hotel under Megging Circle,Upper Siang,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-04-14,27.228840,95.908690,Jotin Joda under Manmao circle,Changlang,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-04-23,27.987910,96.406530,Between Tidding to Hayuliang,Anjaw,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-04-23,27.832650,93.504440,Between Chello village & Tagum Village,Kurung Kumey,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-04-25,28.277670,97.014670,Between Tezu to Kibithoo,Anjaw,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-04-28,27.916380,93.502610,Parsi Landslide,Kurung Kumey,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-04-29,27.867720,93.399820,Rite Landslide,Kurung Kumey,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-04-29,28.622710,95.043720,Between Yingkiong and Pasighat,Upper Siang,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-08-04,28.556700,94.207840,Tato-Menchuka road,Shi-Yomi,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-08-05,26.887490,95.579860,between Noglo and Lazu,Tirap,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-08-25,27.401380,92.145580,Balipara-Charduar-Tawang Road NH 13,West Kameng,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-09-03,27.580080,91.976880,Balipara-Charduar-Tawang Road NH 13,Tawang,Arunachal Pradesh,Type 2,NESAC-SR-392-2026",
    "2025-09-19,27.728560,93.636790,Palin Koloriang road,Kra Daadi,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-10-01,26.994650,95.486690,Near Khonsa Town,Tirap,Arunachal Pradesh,Type 1,NESAC-SR-392-2026",
    "2025-03-31,24.533690,92.832400,Rajgobinadapur in Dholai block,Cachar,Assam,Type 1,NESAC-SR-392-2026",
    "2025-05-20,26.160250,91.696860,Maligaons Hilltop Colony,Kamrup Metro,Assam,Type 3,NESAC-SR-392-2026",
    "2025-05-30,26.191250,91.829530,Bonda Landslide outskirts of Guwahati,Kamrup Metro,Assam,Type 1,NESAC-SR-392-2026",
    "2025-05-31,26.161340,91.705290,Maligaon Landslide,Kamrup Metro,Assam,Type 1,NESAC-SR-392-2026",
    "2025-05-31,26.132670,91.719670,Datalpara Landslide,Kamrup Metro,Assam,Type 2,NESAC-SR-392-2026",
    "2025-05-30,26.203840,91.858360,Panikhaiti Landslide near rail crossing,Kamrup Metro,Assam,Type 1,NESAC-SR-392-2026",
    "2025-06-02,24.920720,93.072990,Doloicherra GP Lakhipur,Cachar,Assam,Type 1,NESAC-SR-392-2026",
    "2025-06-02,24.688740,92.644410,Bowarthar Region,Hailakandi,Assam,Type 1,NESAC-SR-392-2026",
    "2025-06-02,24.780950,92.309290,Brahmanshasan Pt II Nilambazar,Karimganj,Assam,Type 1,NESAC-SR-392-2026",
    "2025-06-02,25.386750,93.119930,Haflong Revenue Circle,Dima Hasao,Assam,Type 1,NESAC-SR-392-2026",
    "2025-06-04,26.146900,91.689860,Pachali Colony area of Maligaon,Kamrup Metro,Assam,Type 2,NESAC-SR-392-2026",
    "2025-05-30,26.203960,91.858510,Near Panikhaiti Police Outpost,Kamrup Metro,Assam,Type 1,NESAC-SR-392-2026",
    "2025-05-31,26.195150,91.766670,Bhupen Hazarika Path Navagraha Hills,Kamrup Metro,Assam,Type 1,NESAC-SR-392-2026",
    "2025-05-31,26.160730,91.704980,Near Swagat Hospital,Kamrup Metro,Assam,Type 1,NESAC-SR-277-2022",
    "2025-06-07,26.156780,91.760960,RupNagar Region Guwahati,Kamrup Metro,Assam,Type 3,NESAC-SR-392-2026",
    "2025-05-20,24.720000,92.500000,Nilambazar RC,Sribhumi,Assam,Type 1,NESAC-SR-392-2026",
    "2025-05-21,25.176870,93.003240,Haflong Landslide,Dima Hasao,Assam,Type 1,NESAC-SR-392-2026"
]

header = "DATE,LATITUDE,LONGITUDE,LOCATION,DISTRICT,STATE,LANDSLIDE_TYPE,SOURCE"

records, errors = [], []
seen_rows = set()
year_distribution = {}
duplicate_count = 0
ne_india_count = 0

LAT_MIN, LAT_MAX = 6.0, 37.0
LON_MIN, LON_MAX = 68.0, 98.0
NE_STATES = {"ARUNACHAL PRADESH", "ASSAM", "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "SIKKIM", "TRIPURA"}

reader = csv.DictReader([header] + raw_rows)
columns = reader.fieldnames

for idx, row in enumerate(reader):
    records.append(row)
    for col in columns:
        if not row[col] or row[col].strip() == "":
            errors.append(f"Row {idx+1}: Missing value in column {col}")
    try:
        lat, lon = float(row["LATITUDE"]), float(row["LONGITUDE"])
        if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
            errors.append(f"Row {idx+1}: Coordinates outside India bounds.")
    except ValueError:
        errors.append(f"Row {idx+1}: Malformed coordinate string.")
    try:
        year = datetime.strptime(row["DATE"].strip(), "%Y-%m-%d").year
        year_distribution[year] = year_distribution.get(year, 0) + 1
    except ValueError: