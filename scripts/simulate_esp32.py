import time
import requests
import random

# ==========================================
# إعدادات المحاكي (IoT Simulator Settings)
# ==========================================
API_URL = "http://127.0.0.1:8090"

# ⚠️ هام جداً: ضع هنا إيميل ورمز مرور أي مشترك (Athlete) مسجل لديك في النظام
# لتتمكن المنصة من ربط هذه القراءات الحيوية بحسابه بشكل صحيح
EMAIL = "athlete@example.com"  
PASSWORD = "123"

def get_token():
    print("[*] جارٍ محاولة تسجيل الدخول للاتصال بالسيرفر...")
    response = requests.post(
        f"{API_URL}/token", 
        data={"username": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        print("[+] تم الاتصال وتوثيق الجهاز بنجاح! 🔓")
        return response.json()["access_token"]
    else:
        print("[-] تأكد من الإيميل وكلمة المرور في أعلى السكريبت.")
        print("تفاصيل الخطأ:", response.text)
        return None

def simulate_workout():
    token = get_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # المعايير الابتدائية للاعب وقت الراحة
    heart_rate = 75.0
    steps = 0
    calories = 0.0

    print("\n[🚀] بدء محاكاة تمرين حي (يرجى مراقبة لوحة التحكم وإشعارات المدرب في الموقع)...\n")
    print("[اضغط Ctrl+C لإيقاف المحاكي في أي وقت]")
    
    try:
        while True:
            # محاكاة إجهاد تدريجي (النبض يرتفع مع الوقت مع نسبة عشوائية)
            heart_rate += random.uniform(-1.0, 4.5) 
            
            # منع النبض من تجاوز 200 بشكل غير طبيعي
            if heart_rate > 195:
                heart_rate -= random.uniform(5.0, 10.0)
            if heart_rate < 60:
                heart_rate = 60
                
            steps += random.randint(15, 35)
            calories += random.uniform(1.5, 4.0)
            
            payload = {
                "heart_rate": round(heart_rate, 1),
                "steps": steps,
                "calories": round(calories, 1)
            }
            
            print(f"[📡] إرسال --> نبض: {payload['heart_rate']} BPM | خطوات: {payload['steps']} | حريرات: {payload['calories']}")
            
            try:
                res = requests.post(f"{API_URL}/sensor-data/", json=payload, headers=headers)
                
                if res.status_code == 200:
                    ai_response = res.json()
                    # إذا كان هناك خطر، نعرض تنبيه في موجه الأوامر الخاص بالهاردوير أيضاً
                    if ai_response.get('is_alert_sent') == 1:
                        print(f"      [⚠️ خطر ML] => {ai_response.get('recommendation')}")
                else:
                    print("      [x] فشل الاستجابة:", res.status_code)
            except Exception as e:
                print("      [x] خطأ في الاتصال بالخادم:", str(e))

            # انتظار ثانيتين لمحاكاة إرسال بطيء مشابه لقدرات الـ ESP32
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[🛑] تم إيقاف المحاكي يدوياً.")

if __name__ == "__main__":
    print("=======================================")
    print("   ⌚ AI.SPORT - ESP32 IoT Simulator  ")
    print("=======================================")
    simulate_workout()
