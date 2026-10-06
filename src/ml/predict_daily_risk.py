import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

def run_daily_prediction_simulation(target_date="2025-05-30"):
    print(f"=== DAILY LANDSLIDE EARLY WARNING BULLETIN FOR: {target_date} ===")
    
    # 1. Load Training Dataset & Train Model
    df_ml = pd.read_csv("landslide_ml_dataset.csv")
    feature_cols = [
        "Daily_Rain_mm", "Rain_3Day_mm", "Rain_7Day_mm", "Rain_15Day_mm", "Rain_30Day_mm",
        "Soil_Moisture", "NDVI", "elevation_mean", "elevation_range", "elevation_std",
        "slope_mean", "slope_max", "slope_std", "slope_pct_above_30", "tri_mean", "tri_p95", "tri_std"
    ]
    
    # Train model on all historical data prior to target date
    df_ml["DATE_DT"] = pd.to_datetime(df_ml["DATE"])
    train_mask = df_ml["DATE_DT"] < pd.to_datetime(target_date)
    
    X_train = df_ml.loc[train_mask, feature_cols]
    y_train = df_ml.loc[train_mask, "LABEL"]
    
    model = HistGradientBoostingClassifier(
        max_iter=100, max_depth=5, learning_rate=0.05, random_state=42
    )
    model.fit(X_train, y_train)
    print("Model trained and ready for inference.")
    
    # 2. Load Environmental Observations for Target Date across all 380 Grid Cells
    df_env = pd.read_parquet("rainfall_soil_ndvi_terrain_2020_2025.parquet")
    df_env["TIME_STR"] = df_env["TIME"].dt.strftime("%Y-%m-%d")
    
    target_env = df_env[df_env["TIME_STR"] == target_date].copy()
    
    if len(target_env) == 0:
        print(f"No environmental data found for date {target_date}")
        return
        
    print(f"Fetched weather data for {len(target_env)} grid locations across Northeast India.")
    
    # Drop any missing values in features
    target_env = target_env.dropna(subset=feature_cols).copy()
    
    # 3. Model Inference (Predict Probability)
    X_today = target_env[feature_cols]
    probabilities = model.predict_proba(X_today)[:, 1]
    target_env["RISK_PROBABILITY_%"] = (probabilities * 100).round(1)
    
    # Assign Risk Categories
    def assign_alert(prob):
        if prob >= 70.0:
            return "HIGH WARNING (RED 🚨)"
        elif prob >= 30.0:
            return "WATCH (YELLOW ⚠️)"
        else:
            return "SAFE (GREEN 🟢)"
            
    target_env["ALERT_LEVEL"] = target_env["RISK_PROBABILITY_%"].apply(assign_alert)
    
    # 4. Generate Emergency Summary Bulletin
    print("\n" + "="*75)
    print(f"       NORTHEAST INDIA DAILY LANDSLIDE HAZARD BULLETIN")
    print(f"                      Date: {target_date}")
    print("="*75)
    
    alert_counts = target_env["ALERT_LEVEL"].value_counts()
    for alert, count in alert_counts.items():
        print(f"  {alert:<25}: {count:3d} grid cells")
        
    # Show Top High-Risk Grid Cells
    high_risk = target_env.sort_values(by="RISK_PROBABILITY_%", ascending=False).head(10)
    print("\n🔥 TOP 10 HIGHEST RISK GRID CELLS TODAY:")
    print("-" * 75)
    
    disp_cols = ["LATITUDE", "LONGITUDE", "Daily_Rain_mm", "Rain_3Day_mm", "Soil_Moisture", "RISK_PROBABILITY_%", "ALERT_LEVEL"]
    print(high_risk[disp_cols].to_string(index=False))
    print("="*75)

if __name__ == "__main__":
    run_daily_prediction_simulation("2025-05-30")
