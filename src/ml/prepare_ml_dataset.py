import pandas as pd
import numpy as np

def build_ml_dataset():
    print("=== STEP 1: BUILDING ML DATASET (POSITIVES + NEGATIVES) ===")
    
    # 1. Load Master Historical Landslides
    df_master = pd.read_csv("historical_landslides_master.csv")
    print(f"Loaded master landslide records: {len(df_master)} rows")
    
    # 2. Load Environmental Parquet Dataset
    df_env = pd.read_parquet("rainfall_soil_ndvi_terrain_2020_2025.parquet")
    print(f"Loaded environmental dataset: {len(df_env)} grid-day rows")
    
    # Feature columns to extract
    feature_cols = [
        "Daily_Rain_mm", "Rain_3Day_mm", "Rain_7Day_mm", "Rain_15Day_mm", "Rain_30Day_mm",
        "Soil_Moisture", "NDVI", "elevation_mean", "elevation_range", "elevation_std",
        "slope_mean", "slope_max", "slope_std", "slope_pct_above_30", "tri_mean", "tri_p95", "tri_std"
    ]
    
    # Ensure rounded lat/lon for fast matching
    df_env["TIME_STR"] = df_env["TIME"].dt.strftime("%Y-%m-%d")
    df_env["LAT_R"] = df_env["LATITUDE"].round(2)
    df_env["LON_R"] = df_env["LONGITUDE"].round(2)
    
    grid_lats = np.array(sorted(df_env["LATITUDE"].unique()))
    grid_lons = np.array(sorted(df_env["LONGITUDE"].unique()))
    
    # MultiIndex lookup for fast environmental data retrieval
    df_env_indexed = df_env.set_index(["TIME_STR", "LAT_R", "LON_R"])
    
    # 3. Extract Positive Samples (LABEL = 1)
    pos_records = []
    landslide_keys = set()
    
    for idx, row in df_master.iterrows():
        d_val = row["DATE"]
        lat = row["LATITUDE"]
        lon = row["LONGITUDE"]
        
        if pd.isna(lat) or pd.isna(lon) or not d_val or d_val == "":
            continue
            
        best_lat = round(grid_lats[np.abs(grid_lats - lat).argmin()], 2)
        best_lon = round(grid_lons[np.abs(grid_lons - lon).argmin()], 2)
        
        if abs(best_lat - lat) <= 0.25 and abs(best_lon - lon) <= 0.25:
            key = (d_val, best_lat, best_lon)
            if key in df_env_indexed.index:
                env_row = df_env_indexed.loc[key]
                if isinstance(env_row, pd.DataFrame):
                    env_row = env_row.iloc[0]
                
                # Check complete features
                if not env_row[feature_cols].isna().any():
                    rec = {
                        "DATE": d_val,
                        "LATITUDE": best_lat,
                        "LONGITUDE": best_lon,
                        "STATE": row["STATE"],
                        "DISTRICT": row["DISTRICT"],
                        "LOCATION": row["LOCATION"],
                        "LABEL": 1
                    }
                    for f in feature_cols:
                        rec[f] = float(env_row[f])
                    
                    pos_records.append(rec)
                    landslide_keys.add(key)
    
    df_pos = pd.DataFrame(pos_records)
    print(f"Extracted Positive Samples (Landslide = 1): {len(df_pos)} rows")
    
    # 4. Extract Negative Samples (LABEL = 0)
    # Ratio: 3 negatives for every 1 positive
    n_negatives = len(df_pos) * 3
    print(f"Sampling Negative Samples (No Landslide = 0): target = {n_negatives} rows")
    
    # Filter out rows with NaN in features
    df_env_clean = df_env.dropna(subset=feature_cols).copy()
    
    # Filter out grid-days where a landslide occurred
    neg_candidates = []
    for idx, row in df_env_clean.iterrows():
        key = (row["TIME_STR"], row["LAT_R"], row["LON_R"])
        if key not in landslide_keys:
            neg_candidates.append(idx)
            
    np.random.seed(42)  # For reproducibility
    sampled_neg_indices = np.random.choice(neg_candidates, size=n_negatives, replace=False)
    
    neg_records = []
    for idx in sampled_neg_indices:
        env_row = df_env_clean.loc[idx]
        rec = {
            "DATE": env_row["TIME_STR"],
            "LATITUDE": env_row["LAT_R"],
            "LONGITUDE": env_row["LON_R"],
            "STATE": "Non-Landslide Grid",
            "DISTRICT": "Non-Landslide Grid",
            "LOCATION": f"Grid ({env_row['LAT_R']}, {env_row['LON_R']})",
            "LABEL": 0
        }
        for f in feature_cols:
            rec[f] = float(env_row[f])
            
        neg_records.append(rec)
        
    df_neg = pd.DataFrame(neg_records)
    print(f"Extracted Negative Samples (No Landslide = 0): {len(df_neg)} rows")
    
    # 5. Combine and Save Final ML Dataset
    df_ml = pd.concat([df_pos, df_neg], ignore_index=True)
    # Shuffle dataset
    df_ml = df_ml.sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    output_path = "landslide_ml_dataset.csv"
    df_ml.to_csv(output_path, index=False)
    print(f"\nFinal ML Dataset saved: {output_path}")
    print(f"Total Rows: {len(df_ml)} | Columns: {len(df_ml.columns)}")
    print(f"Label distribution:\n{df_ml['LABEL'].value_counts()}")

if __name__ == "__main__":
    build_ml_dataset()
