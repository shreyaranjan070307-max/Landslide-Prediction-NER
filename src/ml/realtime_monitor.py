import os
import sys
import time
import joblib
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

# =====================================================================
# REAL-TIME MONITORING PIPELINE FOR LANDSLIDE PREDICTION (SIH26001)
# =====================================================================

MODEL_FILE = "landslide_model.joblib"
PARQUET_FILE = "rainfall_soil_ndvi_terrain_2020_2025.parquet"
GRID_FILE = "ner_grid_380.csv"

LATEST_OUTPUT_FILE = "realtime_risk_latest.csv"
HISTORY_OUTPUT_FILE = "realtime_risk_history.csv"

FEATURE_COLS = [
    "Daily_Rain_mm", "Rain_3Day_mm", "Rain_7Day_mm", "Rain_15Day_mm", "Rain_30Day_mm",
    "Soil_Moisture", "NDVI", "elevation_mean", "elevation_range", "elevation_std",
    "slope_mean", "slope_max", "slope_std", "slope_pct_above_30", "tri_mean", "tri_p95", "tri_std"
]

STATIC_TERRAIN_COLS = [
    "elevation_mean", "elevation_range", "elevation_std",
    "slope_mean", "slope_max", "slope_std", "slope_pct_above_30",
    "tri_mean", "tri_p95", "tri_std"
]

class RealtimeLandslideMonitor:
    def __init__(self, mode="LIVE_API", target_date=None):
        """
        Mode options:
          - 'LIVE_API': Fetches real/current weather forecasts from Open-Meteo public API (non-authenticated).
          - 'SIMULATION_REPLAY': Replays environmental data from latest historical parquet dataset.
        """
        self.mode = mode
        self.target_date = target_date or datetime.now().strftime("%Y-%m-%d")
        self.execution_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.model = None
        self.df_env_historical = None
        self.grid_df = None
        self.source_status = "OK"

    def load_resources(self):
        """Load trained ML model and baseline grid/environmental datasets."""
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(f"Trained model file '{MODEL_FILE}' not found. Please run train_landslide_model.py first.")
        
        model_pack = joblib.load(MODEL_FILE)
        self.model = model_pack["model"]
        print(f"Loaded trained model from '{MODEL_FILE}'.")

        if os.path.exists(PARQUET_FILE):
            self.df_env_historical = pd.read_parquet(PARQUET_FILE)
            self.df_env_historical["TIME_STR"] = self.df_env_historical["TIME"].dt.strftime("%Y-%m-%d")
            print(f"Loaded historical reference parquet dataset ({len(self.df_env_historical)} rows).")
        else:
            raise FileNotFoundError(f"Parquet file '{PARQUET_FILE}' not found.")

    def fetch_live_open_meteo_rainfall(self, lat, lon, target_dt_str):
        """
        Fetch real-time daily rainfall from Open-Meteo public non-authenticated API.
        Retrieves 30-day past history to compute rolling rainfall windows correctly.
        """
        try:
            target_dt = datetime.strptime(target_dt_str, "%Y-%m-%d")
            start_dt = target_dt - timedelta(days=35)
            
            start_str = start_dt.strftime("%Y-%m-%d")
            end_str = target_dt.strftime("%Y-%m-%d")

            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&"
                f"daily=rain_sum&past_days=35&forecast_days=1&"
                f"timezone=Asia%2FKolkata"
            )
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                rain_sums = daily.get("rain_sum", [])
                
                df_rain = pd.DataFrame({"date": dates, "rain": rain_sums})
                df_rain["rain"] = pd.to_numeric(df_rain["rain"], errors="coerce")
                
                # Compute rolling windows
                df_rain = df_rain.sort_values("date").reset_index(drop=True)
                df_rain["rain_3d"] = df_rain["rain"].rolling(3).sum()
                df_rain["rain_7d"] = df_rain["rain"].rolling(7).sum()
                df_rain["rain_15d"] = df_rain["rain"].rolling(15).sum()
                df_rain["rain_30d"] = df_rain["rain"].rolling(30).sum()

                target_row = df_rain[df_rain["date"] == target_dt_str]
                if not target_row.empty:
                    r = target_row.iloc[0]
                    return {
                        "Daily_Rain_mm": float(r["rain"]),
                        "Rain_3Day_mm": float(r["rain_3d"]),
                        "Rain_7Day_mm": float(r["rain_7d"]),
                        "Rain_15Day_mm": float(r["rain_15d"]),
                        "Rain_30Day_mm": float(r["rain_30d"]),
                        "status": "LIVE_API_SUCCESS"
                    }
        except Exception as e:
            pass
        return None

    def prepare_features(self):
        """
        Prepare feature matrix for all 380 grid cells.
        Calculates rolling rainfall windows and integrates static terrain + latest NDVI/soil moisture.
        """
        print(f"Preparing features for date: {self.target_date} (Mode: {self.mode})...")

        # Ensure LAT_R and LON_R columns exist on historical dataset
        self.df_env_historical["LAT_R"] = self.df_env_historical["LATITUDE"].round(2)
        self.df_env_historical["LON_R"] = self.df_env_historical["LONGITUDE"].round(2)

        # 1. Unique 380 spatial grid cells from reference parquet
        grid_cells = self.df_env_historical[["LATITUDE", "LONGITUDE"]].drop_duplicates().reset_index(drop=True)
        grid_cells["LAT_R"] = grid_cells["LATITUDE"].round(2)
        grid_cells["LON_R"] = grid_cells["LONGITUDE"].round(2)
        
        # Extract static terrain features per grid cell
        terrain_features = self.df_env_historical.groupby(["LATITUDE", "LONGITUDE"])[STATIC_TERRAIN_COLS].first().reset_index()

        rows = []

        if self.mode == "LIVE_API":
            print("Attempting LIVE API fetch from Open-Meteo for grid cells (sample batch)...")
            api_success_count = 0
            
            # For efficiency in prototype, sample 10 representative grid cells via Live API, fallback rest gracefully
            for idx, g in grid_cells.iterrows():
                lat, lon = g["LATITUDE"], g["LONGITUDE"]
                lat_r, lon_r = g["LAT_R"], g["LON_R"]
                
                live_rain = None
                if idx < 10:  # Fetch live API for sample grid points to demonstrate live API integration
                    live_rain = self.fetch_live_open_meteo_rainfall(lat, lon, self.target_date)
                    if live_rain:
                        api_success_count += 1
                
                # Retrieve static terrain
                ter = terrain_features[(terrain_features["LATITUDE"] == lat) & (terrain_features["LONGITUDE"] == lon)].iloc[0]

                # Retrieve latest available historical NDVI and Soil Moisture
                latest_env_sub = self.df_env_historical[(self.df_env_historical["LAT_R"] == lat_r) & (self.df_env_historical["LON_R"] == lon_r)]
                
                ndvi_val = latest_env_sub["NDVI"].dropna().iloc[-1] if not latest_env_sub.empty else np.nan
                ndvi_time = latest_env_sub["TIME_STR"].dropna().iloc[-1] if not latest_env_sub.empty else "N/A"
                
                soil_val = latest_env_sub["Soil_Moisture"].dropna().iloc[-1] if not latest_env_sub.empty else np.nan

                if live_rain:
                    d_rain = live_rain["Daily_Rain_mm"]
                    r3 = live_rain["Rain_3Day_mm"]
                    r7 = live_rain["Rain_7Day_mm"]
                    r15 = live_rain["Rain_15Day_mm"]
                    r30 = live_rain["Rain_30Day_mm"]
                    sub_mode = "LIVE_API"
                else:
                    # Fallback to replay row if live API not sampled/failed
                    sub_mode = "LIVE_API_FALLBACK_REPLAY"
                    dt_rows = latest_env_sub[latest_env_sub["TIME_STR"] == self.target_date]
                    if not dt_rows.empty:
                        r = dt_rows.iloc[0]
                        d_rain = float(r["Daily_Rain_mm"]) if pd.notna(r["Daily_Rain_mm"]) else np.nan
                        r3 = float(r["Rain_3Day_mm"]) if pd.notna(r["Rain_3Day_mm"]) else np.nan
                        r7 = float(r["Rain_7Day_mm"]) if pd.notna(r["Rain_7Day_mm"]) else np.nan
                        r15 = float(r["Rain_15Day_mm"]) if pd.notna(r["Rain_15Day_mm"]) else np.nan
                        r30 = float(r["Rain_30Day_mm"]) if pd.notna(r["Rain_30Day_mm"]) else np.nan
                    else:
                        d_rain = r3 = r7 = r15 = r30 = np.nan

                rec = {
                    "execution_timestamp": self.execution_timestamp,
                    "data_mode": sub_mode,
                    "observation_date": self.target_date,
                    "latitude": lat,
                    "longitude": lon,
                    "Daily_Rain_mm": d_rain,
                    "Rain_3Day_mm": r3,
                    "Rain_7Day_mm": r7,
                    "Rain_15Day_mm": r15,
                    "Rain_30Day_mm": r30,
                    "Soil_Moisture": soil_val,
                    "NDVI": ndvi_val,
                    "ndvi_observation_timestamp": ndvi_time,
                    "source_status": "LIVE_API_ACTIVE" if api_success_count > 0 else "SIMULATION_REPLAY_ACTIVE"
                }
                for t_col in STATIC_TERRAIN_COLS:
                    rec[t_col] = float(ter[t_col])
                    
                rows.append(rec)
            print(f"Live API ingestion completed: {api_success_count} cells live-fetched, remaining fallback-replayed.")

        else:
            # SIMULATION_REPLAY MODE
            print(f"Replaying observations from historical dataset for date: {self.target_date}...")
            dt_subset = self.df_env_historical[self.df_env_historical["TIME_STR"] == self.target_date]
            
            if dt_subset.empty:
                # If target_date is beyond historical parquet (e.g. current date), use latest available date in parquet
                latest_date_in_parquet = self.df_env_historical["TIME_STR"].max()
                print(f"Target date {self.target_date} not in historical parquet. Replaying latest available date: {latest_date_in_parquet}")
                self.target_date = latest_date_in_parquet
                dt_subset = self.df_env_historical[self.df_env_historical["TIME_STR"] == self.target_date]
                
            for idx, r in dt_subset.iterrows():
                rec = {
                    "execution_timestamp": self.execution_timestamp,
                    "data_mode": "SIMULATION_REPLAY",
                    "observation_date": self.target_date,
                    "latitude": float(r["LATITUDE"]),
                    "longitude": float(r["LONGITUDE"]),
                    "Daily_Rain_mm": float(r["Daily_Rain_mm"]) if pd.notna(r["Daily_Rain_mm"]) else np.nan,
                    "Rain_3Day_mm": float(r["Rain_3Day_mm"]) if pd.notna(r["Rain_3Day_mm"]) else np.nan,
                    "Rain_7Day_mm": float(r["Rain_7Day_mm"]) if pd.notna(r["Rain_7Day_mm"]) else np.nan,
                    "Rain_15Day_mm": float(r["Rain_15Day_mm"]) if pd.notna(r["Rain_15Day_mm"]) else np.nan,
                    "Rain_30Day_mm": float(r["Rain_30Day_mm"]) if pd.notna(r["Rain_30Day_mm"]) else np.nan,
                    "Soil_Moisture": float(r["Soil_Moisture"]) if pd.notna(r["Soil_Moisture"]) else np.nan,
                    "NDVI": float(r["NDVI"]) if pd.notna(r["NDVI"]) else np.nan,
                    "ndvi_observation_timestamp": self.target_date,
                    "source_status": "SIMULATION_REPLAY_ACTIVE"
                }
                for t_col in STATIC_TERRAIN_COLS:
                    rec[t_col] = float(r[t_col]) if pd.notna(r[t_col]) else np.nan
                    
                rows.append(rec)

        return pd.DataFrame(rows)

    def run_inference_and_export(self):
        """Run ML model inference on prepared feature matrix and save outputs."""
        self.load_resources()
        df_prepared = self.prepare_features()

        print(f"Running inference on {len(df_prepared)} grid observations...")
        
        # Filter valid feature rows for inference
        X_features = df_prepared[FEATURE_COLS].copy()
        
        # Identify rows with missing feature values
        valid_mask = ~X_features.isna().any(axis=1)
        
        probabilities = np.full(len(df_prepared), np.nan)
        if valid_mask.sum() > 0:
            probs_valid = self.model.predict_proba(X_features.loc[valid_mask])[:, 1]
            probabilities[valid_mask] = probs_valid

        df_prepared["landslide_probability"] = np.round(probabilities, 4)

        # Categorize risk levels
        def get_risk_level(prob):
            if pd.isna(prob):
                return "UNAVAILABLE_MISSING_DATA"
            elif prob >= 0.70:
                return "HIGH"
            elif prob >= 0.30:
                return "WATCH"
            else:
                return "SAFE"

        df_prepared["risk_level"] = df_prepared["landslide_probability"].apply(get_risk_level)

        # Reorder output columns cleanly
        output_cols = [
            "execution_timestamp", "data_mode", "observation_date",
            "latitude", "longitude",
            "Daily_Rain_mm", "Rain_3Day_mm", "Rain_7Day_mm", "Rain_15Day_mm", "Rain_30Day_mm",
            "Soil_Moisture", "NDVI", "ndvi_observation_timestamp",
            "landslide_probability", "risk_level", "source_status"
        ]

        df_out = df_prepared[output_cols].copy()

        # Save Latest Execution Output
        df_out.to_csv(LATEST_OUTPUT_FILE, index=False)
        print(f"Saved latest risk output: {LATEST_OUTPUT_FILE} ({len(df_out)} rows)")

        # Append to History Log
        if not os.path.exists(HISTORY_OUTPUT_FILE):
            df_out.to_csv(HISTORY_OUTPUT_FILE, index=False)
        else:
            df_out.to_csv(HISTORY_OUTPUT_FILE, mode="a", header=False, index=False)
        print(f"Appended run to historical log: {HISTORY_OUTPUT_FILE}")

        # Summary Statistics
        print("\n" + "="*65)
        print("          REAL-TIME RISK MONITORING EXECUTION SUMMARY")
        print("="*65)
        print(f"Execution Time     : {self.execution_timestamp}")
        print(f"Data Mode          : {self.mode}")
        print(f"Observation Date   : {self.target_date}")
        print(f"Total Grid Cells   : {len(df_out)}")
        print("\nRisk Level Breakdown:")
        print(df_out["risk_level"].value_counts().to_string())
        print("="*65)

def main():
    # Parse CLI argument for mode or date if provided
    mode = sys.argv[1] if len(sys.argv) > 1 else "SIMULATION_REPLAY"
    date_arg = sys.argv[2] if len(sys.argv) > 2 else "2025-05-30"

    monitor = RealtimeLandslideMonitor(mode=mode, target_date=date_arg)
    monitor.run_inference_and_export()

if __name__ == "__main__":
    main()
