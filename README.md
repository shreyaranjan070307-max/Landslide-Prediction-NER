# Landslide Early Warning & Risk Prediction System (SIH26001)

An end-to-end Geospatial AI & Earth Observation Pipeline for predicting landslide susceptibility and daily risk in India's North East Region (NER).

---

## 📁 Repository Structure

```text
SIH26001/
├── src/                          # Source Code
│   ├── data_prep/                # Climate, Soil, NDVI & Terrain Feature Pipeline
│   │   ├── rainfall.py           # IMD Rainfall extraction & feature engineering
│   │   ├── soil_download.py      # ERA5-Land soil moisture CDS download
│   │   ├── regrid_soil.py        # Interp ERA5-Land onto IMD 0.25° grid
│   │   ├── soil_mask.py          # Spatial polygon masking for NER region
│   │   ├── soil_to_table.py      # Convert NetCDF grid to Parquet table
│   │   ├── terrain_download.py   # SRTM DEM elevation retrieval
│   │   ├── terrain_slope.py      # Compute Slope & TRI metrics
│   │   ├── terrain_aggregate.py  # Spatial aggregation to 0.25° grid
│   │   ├── merge_ndvi.py         # Merge NASA MODIS GEE NDVI data
│   │   └── combine_rain_soil.py  # Merge rainfall + soil datasets
│   │
│   └── ml/                       # Machine Learning Pipeline
│       ├── extract_historical_landslides.py # Extract GSI inventory records
│       ├── prepare_ml_dataset.py # Match positive events & sample negatives
│       ├── train_landslide_model.py # Train HistGradientBoosting model
│       ├── predict_daily_risk.py # Model evaluation & batch prediction
│       ├── realtime_monitor.py   # Daily risk monitor & alert pipeline
│       └── audit_landslide.py    # Data audit & quality checks
│
├── data/                         # Data Storage
│   ├── raw_landslides/           # GSI PDF extract CSVs
│   ├── soil_data/                # Raw & regridded NetCDFs / tables
│   ├── rainfall_data/            # IMD NetCDF daily rainfall files
│   ├── terrain_data/             # SRTM DEM & terrain Parquet features
│   └── boundaries/               # GeoJSON spatial boundaries (NER)
│
├── models/                       # Trained ML Models & Artifacts
│   └── landslide_model.joblib
│
├── reports/                      # GSI Inventory Reports & Audits
│   ├── SLI2020.pdf
│   ├── SLI2021.pdf
│   ├── FINAL2022 landslide report2.pdf
│   ├── Seasonal_LS_Inventory_2023_Report.pdf
│   └── ls25.pdf, ls26.pdf, ls28.pdf
│
└── archive/                      # Archived test / scratch scripts
```

---

## 🚀 Pipeline Workflow

### 1. Data Processing Pipeline
```bash
# Soil Processing
python src/data_prep/soil_download.py
python src/data_prep/regrid_soil.py
python src/data_prep/soil_mask.py
python src/data_prep/soil_to_table.py

# Combine Environmental Features
python src/data_prep/combine_rain_soil.py
python src/data_prep/merge_ndvi.py
```

### 2. Machine Learning Training & Evaluation
```bash
# Build Training Dataset (Positives + Negative 3:1 sampling)
python src/ml/prepare_ml_dataset.py

# Train & Validate Gradient Boosting Classifier
python src/ml/train_landslide_model.py
```

### 3. Real-Time Risk Monitoring
```bash
python src/ml/realtime_monitor.py
```


Project Report-https://docs.google.com/document/d/1gFw4-REFhdwDEU51EJg4QF1s0io5saONHfT36B8Y4zo/edit?usp=sharing
