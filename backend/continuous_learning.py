import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sqlite3

def retrain_models_from_db(db_path="smart_gym.db"):
    """
    Continuous Learning Pipeline:
    Connects to the database, extracts recent SensorData and retrains the models.
    """
    print("Fetching new data from Database for Continuous Learning...")
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT heart_rate, steps, calories FROM sensor_data ORDER BY timestamp DESC LIMIT 5000"
        df_new = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return False

    if len(df_new) < 100:
        print("Not enough new data to retrain. Need at least 100 records.")
        return False

    # 1. Preprocessing new data (Cleaning & Normalization)
    df_new['heart_rate'] = df_new['heart_rate'].clip(40, 220)
    df_new['steps'] = df_new['steps'].clip(0, 10000)
    df_new['calories'] = df_new['calories'].clip(0, 2000)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_new)
    
    # Normally we would fetch the true labels (Fatigue, Injury Risk) from Coach feedback/PerformanceMetrics.
    # For automated pipeline demonstration, we use heuristic labeling or an active learning model
    df_new['fatigue'] = np.where(df_new['heart_rate'] > 150, 2, np.where(df_new['heart_rate'] > 110, 1, 0))
    df_new['injury_risk'] = np.where((df_new['heart_rate'] > 165) & (df_new['steps'] < 200), 1, 0)
    
    # Adding Noise to simulate real-world variance
    noise = np.random.choice([0, 1], size=len(df_new), p=[0.95, 0.05])
    df_new['injury_risk'] = np.clip(df_new['injury_risk'] + noise, 0, 1)

    X = df_new[['heart_rate', 'steps', 'calories']]
    y_injury = df_new['injury_risk']
    y_fatigue = df_new['fatigue']

    # 2. Retrain Models
    print("Retraining XGBoost (Injury Model)...")
    injury_model = xgb.XGBClassifier(
        objective='binary:logistic', n_estimators=100, learning_rate=0.05, max_depth=4
    )
    injury_model.fit(X, y_injury)

    print("Retraining Random Forest (Fatigue Model)...")
    fatigue_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    fatigue_model.fit(X, y_fatigue)

    # 3. Save Updated Models
    os.makedirs('ml_models', exist_ok=True)
    joblib.dump(injury_model, 'ml_models/injury_xgboost.pkl')
    joblib.dump(fatigue_model, 'ml_models/fatigue_rf.pkl')
    joblib.dump(scaler, 'ml_models/scaler.pkl')

    print("Continuous Learning Pipeline Completed. Models updated and saved.")
    return True

if __name__ == "__main__":
    retrain_models_from_db()
