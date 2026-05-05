import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

print("TensorFlow version:", tf.__version__)

# --- 1. بناء مجموعة بيانات وهمية لتدريب النموذج (Dummy Dataset) ---
np.random.seed(42)
n_samples = 2000

# الميزات: نبض القلب، الخطوات، السعرات (متوسط 5 دقائق)
heart_rate = np.random.normal(120, 30, n_samples)
steps = np.random.normal(500, 200, n_samples)
calories = np.random.normal(100, 50, n_samples)

# حساب الإجهاد (Fatigue - 0: Low, 1: Medium, 2: High)
fatigue = []
for hr in heart_rate:
    if hr > 150:
        fatigue.append(2) # High
    elif hr > 110:
        fatigue.append(1) # Medium
    else:
        fatigue.append(0) # Low

df = pd.DataFrame({
    'heart_rate': heart_rate,
    'steps': steps,
    'calories': calories,
    'fatigue': fatigue,
})

X = df[['heart_rate', 'steps', 'calories']].values
y = df['fatigue'].values

# تقسيم البيانات إلى تدريب واختبار
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# تطبيع البيانات (مهم جداً للتعلم العميق)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- 2. بناء نموذج التعلم العميق (Deep Neural Network) ---
print("Building Deep Learning Model for Fatigue Prediction...")

model = Sequential([
    Dense(32, activation='relu', input_shape=(3,)),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dropout(0.1),
    Dense(3, activation='softmax') # 3 فئات: Low, Medium, High
])

model.compile(optimizer='adam', 
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])

# --- 3. تدريب النموذج ---
print("Training Deep Learning Model...")
model.fit(X_train_scaled, y_train, epochs=30, batch_size=32, validation_split=0.1, verbose=1)

# تقييم النموذج
loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"Model Test Accuracy: {accuracy:.2f}")

# --- 4. حفظ النموذج لكي يتم استخدامه في النظام المباشر ---
os.makedirs('models', exist_ok=True)
model.save('models/fatigue_dl_model.h5')
joblib.dump(scaler, 'models/dl_scaler.pkl') # يجب حفظ الـ scaler ليتم استخدامه في التطبيق

print("Deep Learning model and scaler saved successfully in 'models/' directory!")
