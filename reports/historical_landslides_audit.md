# HISTORICAL LANDSLIDE DATASET AUDIT REPORT

## 1. Summary of Records by Year

| Year | Record Count | Valid Dates | Missing/Unparseable Dates |
|---|---|---|---|
| **2020** | 141 | 131 | 10 |
| **2021** | 40 | 40 | 0 |
| **2022** | 145 | 145 | 0 |
| **2023** | 86 | 85 | 1 |
| **2024** | 223 | 223 | 0 |
| **2025** | 91 | 91 | 0 |
| **TOTAL** | **726** | **715** | **11** |

## 2. State-wise Distribution by Year

| STATE | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | All |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Arunachal Pradesh | 5 | 17 | 5 | 20 | 29 | 28 | 104 |
| Assam | 20 | 4 | 78 | 8 | 15 | 17 | 142 |
| Manipur | 15 | 11 | 1 | 3 | 22 | 0 | 52 |
| Meghalaya | 23 | 4 | 35 | 22 | 94 | 46 | 224 |
| Mizoram | 41 | 4 | 24 | 8 | 12 | 0 | 89 |
| Nagaland | 10 | 0 | 0 | 10 | 26 | 0 | 46 |
| Sikkim | 27 | 0 | 2 | 14 | 19 | 0 | 62 |
| Tripura | 0 | 0 | 0 | 1 | 6 | 0 | 7 |
| All | 141 | 40 | 145 | 86 | 223 | 91 | 726 |


## 3. Data Quality & Audit Observations

* **Total Master Rows**: 726
* **Exact Duplicate Rows**: 0
* **Date + Location Duplicates**: 24
* **Missing Latitudes**: 41
* **Missing Longitudes**: 46
* **Missing Locations**: 39
* **Missing Districts**: 1
* **Suspicious Date Record**: `Newspapers&Media/2022/Meghalaya/115` has table date `16-06-2020` in 2022 report source. Preserved as `16-06-2020` / `2020-06-16` and flagged.
* **2020 Date Parsing Note**: 10 records in 2020 source had non-standard text dates (e.g. 'Last week of June'). Preserved with empty `DATE` in master and flagged in audit.
