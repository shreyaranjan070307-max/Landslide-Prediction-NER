import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.inspection import permutation_importance

def main():
    # =====================================================================
    # BLOCK 1: Load Data & Temporal Train/Test Split (2020-2024 vs 2025)
    # =====================================================================
    print("=== BLOCK 1: LOADING DATA & TEMPORAL SPLIT ===")
    df = pd.read_csv("landslide_ml_dataset.csv")

    # 17 Environmental Features
    feature_cols = [
        "Daily_Rain_mm", "Rain_3Day_mm", "Rain_7Day_mm", "Rain_15Day_mm", "Rain_30Day_mm",
        "Soil_Moisture", "NDVI", "elevation_mean", "elevation_range", "elevation_std",
        "slope_mean", "slope_max", "slope_std", "slope_pct_above_30", "tri_mean", "tri_p95", "tri_std"
    ]

    # Convert DATE to datetime for splitting
    df["DATE_DT"] = pd.to_datetime(df["DATE"], errors="coerce")

    # Split into Train (2020-2024) and Test (2025)
    train_mask = df["DATE_DT"].dt.year < 2025
    test_mask = df["DATE_DT"].dt.year == 2025

    X_train = df.loc[train_mask, feature_cols]
    y_train = df.loc[train_mask, "LABEL"]

    X_test = df.loc[test_mask, feature_cols]
    y_test = df.loc[test_mask, "LABEL"]

    print(f"Training Set (2020-2024): {len(X_train)} rows | Positives: {y_train.sum()}, Negatives: {len(y_train) - y_train.sum()}")
    print(f"Testing Set (2025):       {len(X_test)} rows | Positives: {y_test.sum()}, Negatives: {len(y_test) - y_test.sum()}")

    # =====================================================================
    # BLOCK 2: Train Gradient Boosted Decision Tree Model
    # =====================================================================
    print("\n=== BLOCK 2: TRAINING GRADIENT BOOSTING MODEL ===")
    # Using HistGradientBoostingClassifier (Scikit-Learn's fast Gradient Boosting algorithm)
    model = HistGradientBoostingClassifier(
        max_iter=100,
        max_depth=5,
        learning_rate=0.05,
        random_state=42
    )

    model.fit(X_train, y_train)
    print("Model training complete!")

    import joblib
    joblib.dump({"model": model, "feature_cols": feature_cols}, "landslide_model.joblib")
    print("Saved trained model to landslide_model.joblib")

    # =====================================================================
    # BLOCK 3: Evaluate Performance on Unseen 2025 Test Data
    # =====================================================================
    print("\n=== BLOCK 3: EVALUATING MODEL ON 2025 TEST DATA ===")
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_prob >= 0.5).astype(int)

    auc_score = roc_auc_score(y_test, y_pred_prob)
    print(f"ROC-AUC Score on 2025 Test Set: {auc_score:.4f}")

    print("\nClassification Report (2025 Test Set):")
    print(classification_report(y_test, y_pred, target_names=["No Landslide (0)", "Landslide (1)"]))

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(f"  True Negatives  (Correctly predicted safe): {cm[0, 0]}")
    print(f"  False Positives (False alarms):            {cm[0, 1]}")
    print(f"  False Negatives (Missed landslides):       {cm[1, 0]}")
    print(f"  True Positives  (Correctly caught slides): {cm[1, 1]}")

    # =====================================================================
    # BLOCK 4: Feature Importance Analysis
    # =====================================================================
    print("\n=== BLOCK 4: FEATURE IMPORTANCE RANKING ===")
    # Permutation importance calculates importance by measuring drop in score when a feature is shuffled
    result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
    
    importance_df = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": result.importances_mean
    }).sort_values(by="Importance", ascending=False)

    print(importance_df.to_string(index=False))

if __name__ == "__main__":
    main()
