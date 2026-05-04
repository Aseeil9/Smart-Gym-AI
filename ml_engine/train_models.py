import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib
import os

# --- 1. بناء مجموعة بيانات وهمية لتدريب النماذج (Dummy Dataset) ---
np.random.seed(42)
n_samples = 1000

# الميزات: نبض القلب، الخطوات، السعرات (متوسط 5 دقائق)
heart_rate = np.random.normal(120, 30, n_samples)
steps = np.random.normal(500, 200, n_samples)
calories = np.random.normal(100, 50, n_samples)

# حساب الإجهاد (Fatigue - 0: Low, 1: Medium, 2: High)
# تصنيف بسيط لتدريب النموذج
fatigue = []
for hr in heart_rate:
    if hr > 150:
        fatigue.append(2) # High
    elif hr > 110:
        fatigue.append(1) # Medium
    else:
        fatigue.append(0) # Low

# حساب احتمالية الإصابة (Injury_Risk - 0: Safe, 1: At Risk)
# تفترض أن النبض العالي مع قلة الخطوات خطير (الإرهاق العضلي المفاجئ)
injury_risk = []
for i in range(n_samples):
    if heart_rate[i] > 165 and steps[i] < 200:
        injury_risk.append(1) # At risk
    else:
        # بعض العشوائية (Noise) لجعل النموذج يتعلم
        injury_risk.append(np.random.choice([0, 1], p=[0.9, 0.1]))

df = pd.DataFrame({
    'heart_rate': heart_rate,
    'steps': steps,
    'calories': calories,
    'fatigue': fatigue,
    'injury_risk': injury_risk
})

X = df[['heart_rate', 'steps', 'calories']]
y_injury = df['injury_risk']
y_fatigue = df['fatigue']

# --- 2. تدريب نموذج XGBoost لاكتشاف خطر الإصابات ---
print("Training XGBoost for Injury Risk Prediction...")
injury_model = xgb.XGBClassifier(
    objective='binary:logistic',
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    eval_metric='logloss'
)
injury_model.fit(X, y_injury)

# --- 3. تدريب نموذج Random Forest لاكتشاف مستوى الإجهاد (كمثال لـ Classifier آخر) ---
print("Training Random Forest for Fatigue Level Prediction...")
fatigue_model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
fatigue_model.fit(X, y_fatigue)

# --- 4. حفظ النماذج باستخدام Joblib لاستخدامها في النظام المباشر ---
os.makedirs('ml_models', exist_ok=True)
joblib.dump(injury_model, 'ml_models/injury_xgboost.pkl')
joblib.dump(fatigue_model, 'ml_models/fatigue_rf.pkl')

print("Models trained and saved successfully in 'ml_models/' directory!")
