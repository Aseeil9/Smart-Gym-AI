import joblib
import numpy as np
import pandas as pd
import json
import os

# --- 1. Load Pre-trained ML Models ---
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, 'models')
    
    injury_model = joblib.load(os.path.join(models_dir, 'injury_xgboost.pkl'))
    fatigue_model = joblib.load(os.path.join(models_dir, 'fatigue_rf.pkl'))
    
    # Load Scaler if exists
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
    else:
        scaler = None
    MODELS_LOADED = True
except Exception as e:
    print(f"Warning: ML Models not found in {models_dir}. Using fallback logic. ({e})")
    MODELS_LOADED = False
    scaler = None

# --- 1.1 Coach Thresholds (Dynamic Adjustments) ---
COACH_THRESHOLDS = {
    "high_hr_threshold": 150,
    "medium_hr_threshold": 110,
    "injury_risk_threshold": 0.60
}

def update_coach_thresholds(high_hr: int, med_hr: int, injury_risk: float):
    """
    تسمح للمدرب بتعديل المتغيرات والمعايير بناءً على الفروق الفردية للرياضيين
    """
    global COACH_THRESHOLDS
    if high_hr: COACH_THRESHOLDS["high_hr_threshold"] = high_hr
    if med_hr: COACH_THRESHOLDS["medium_hr_threshold"] = med_hr
    if injury_risk: COACH_THRESHOLDS["injury_risk_threshold"] = injury_risk

# --- 2. Data Preprocessing Layer (Middleware) ---
def preprocess_sensor_data(sensor_data: dict) -> dict:
    """
    Data Cleaning and Normalization Middleware.
    """
    # 1. Outlier Removal / Clipping
    hr = max(40, min(sensor_data.get("heart_rate", 80), 220))
    steps = max(0, min(sensor_data.get("steps", 0), 10000))
    calories = max(0, min(sensor_data.get("calories", 0), 2000))

    # 2. Data Scaling/Normalization
    if scaler:
        # Transform using pre-fitted scaler
        scaled_features = scaler.transform([[hr, steps, calories]])
        hr_scaled, steps_scaled, calories_scaled = scaled_features[0]
    else:
        # Fallback manual scaling (MinMax similar)
        hr_scaled = (hr - 60) / (200 - 60)
        steps_scaled = steps / 10000.0
        calories_scaled = calories / 2000.0

    return {
        "heart_rate_raw": hr,
        "steps_raw": steps,
        "calories_raw": calories,
        "heart_rate": hr_scaled if scaler else hr, 
        "steps": steps_scaled if scaler else steps,
        "calories": calories_scaled if scaler else calories
    }

# --- 3. AI Analytics Pipeline ---
def analyze_sensor_data(raw_sensor_data: dict) -> dict:
    clean_data = preprocess_sensor_data(raw_sensor_data)
    
    # Input for models (Using raw bounded data for models trained previously without scaler)
    # If starting fresh, would use scaled data.
    X_input = pd.DataFrame([{
        "heart_rate": clean_data["heart_rate_raw"],
        "steps": clean_data["steps_raw"],
        "calories": clean_data["calories_raw"]
    }])

    fatigue_prediction_label = "Low"
    injury_risk_score = 0.1
    
    if MODELS_LOADED:
        proba_injury = injury_model.predict_proba(X_input)
        injury_risk_score = round(float(proba_injury[0][1]), 2)
        
        prediction_fatigue = fatigue_model.predict(X_input)[0] 
        fatigue_map = {0: "Low", 1: "Medium", 2: "High"}
        fatigue_prediction_label = fatigue_map.get(prediction_fatigue, "Medium")
    else:
        hr = clean_data["heart_rate_raw"]
        if hr > COACH_THRESHOLDS["high_hr_threshold"]:
            fatigue_prediction_label = "High"
            injury_risk_score = 0.85 
        elif hr > COACH_THRESHOLDS["medium_hr_threshold"]:
            fatigue_prediction_label = "Medium"
            injury_risk_score = 0.45 
            
    recommendation = "أداؤك ممتاز في النطاق الآمن. استمر بالروتين التدريبي الحالي."
    is_alert_required = False
    
    if fatigue_prediction_label == "High" or injury_risk_score > COACH_THRESHOLDS["injury_risk_threshold"]:
        recommendation = "تنبيه ذكي: مؤشر خطر إصابة أو إجهاد عضلي حاد! (يُرجى التوقف للراحة لمدة 48 ساعة أو خفض الشدة)."
        is_alert_required = True
        
    return {
        "injury_risk": injury_risk_score,
        "fatigue_prediction": fatigue_prediction_label,
        "recommendation": recommendation,
        "is_alert_required": is_alert_required,
        "clean_data_used": clean_data 
    }

# --- 4. AI-Driven Personalized Training Plan Generator ---
def generate_training_plan(performance_metrics: list) -> str:
    """
    Uses predictive modeling logic to build a weekly workout plan.
    (Ideally this calls an LLM or a trained sequence model like LSTM, 
     here we simulate an AI decision engine based on past metrics)
    """
    if not performance_metrics:
        # Default AI Plan for new users
        return "برنامج تمهيدي: \nاليوم 1: تقييم لياقة شامل (كارديو خفيف)\nاليوم 2: راحة\nاليوم 3: تمارين وزن الجسم الأساسية"
        
    sum_fatigue = 0
    for m in performance_metrics:
        # Handle Enum from the database correctly
        level = m.fatigue_level.value if hasattr(m.fatigue_level, 'value') else m.fatigue_level
        if level == "High":
            sum_fatigue += 10.0
        elif level == "Medium":
            sum_fatigue += 5.0
        else:
            sum_fatigue += 2.0
            
    avg_fatigue = sum_fatigue / len(performance_metrics)
    avg_recovery = sum([m.recovery_rate for m in performance_metrics]) / len(performance_metrics)
    
    # We could load a specifically trained model here, e.g., plan_generator.predict([[avg_fatigue, avg_recovery]])
    # For now, advanced analytical mapping
    if avg_fatigue > 7.0 and avg_recovery < 5.0:
        return "خطة استشفائية نشطة مدعومة بالذكاء الاصطناعي:\n- اليوم 1: يوجا وإطالة (30 دقيقة)\n- اليوم 2: راحة تامة\n- اليوم 3: سباحة خفيفة (Recovery Pool)\n- اليوم 4-7: مشي خفيف مع مراقبة النبض."
    elif avg_fatigue < 4.0 and avg_recovery > 7.0:
        return "خطة مكثفة لتضخيم العضلات (Hypertrophy):\n- اليوم 1: دفع (صدر وكتف)\n- اليوم 2: سحب (ظهر وبايسبس)\n- اليوم 3: أرجل (سكوات ورفعة ميتة)\n- اليوم 4: راحة\n- وتكرار الدورة لرفع الكفاءة."
    else:
        return "خطة لياقة متوازنة لتعزيز التحمل:\n- 3 أيام تدريب مقاومة متكرر\n- يومين كارديو متوسط الشدة\n- يومين راحة لضمان بقاء معدل الاستشفاء فوق 60%."
