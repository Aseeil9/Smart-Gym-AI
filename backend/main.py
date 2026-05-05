import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from jose import JWTError, jwt
from security_utils import verify_password, get_password_hash, create_access_token, ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

from models import (
    SessionLocal, engine, init_db, User, UserRole, WorkoutClass, SensorData, 
    PerformanceMetrics, AIPrediction, Gym, GymMembership, ClassEnrollment, PaymentInvoice,
    TrainingPlan, FatigueLevel, CustomerPhone, ClassInstructor, SleepData, Announcement, ExerciseLog
)
# من فضلك تأكد من وجود ملفات ml_engine و continuous_learning في نفس المجلد
try:
    from ml_engine import analyze_sensor_data, generate_training_plan, update_coach_thresholds
    import continuous_learning
except ImportError:
    # لتجنب انهيار المشروع في حال نقص المكتبات
    analyze_sensor_data = lambda x: {"injury_risk": 0.1, "recommendation": "Data processing error", "is_alert_required": False}
    generate_training_plan = lambda x: "AI Plan placeholder"
    update_coach_thresholds = lambda a,b,c: None

init_db()  

app = FastAPI(
    title="Smart Gym AI System",
    description="نظام إدارة الصالات الرياضية مدعوم بالذكاء الاصطناعي مع التنبيهات اللحظية وحجوزات الحصص",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        # Dictionary of active websockets: { user_id: [websocket1, ...] }
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_alert_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Security Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="تعذر التحقق من التوكين (Could not validate credentials)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if user.role == UserRole.ATHLETE:
        membership = db.query(GymMembership).filter(GymMembership.customer_id == user.id).order_by(GymMembership.id.desc()).first()
        if not membership or (membership.end_date and membership.end_date < datetime.utcnow()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="اشتراكك منتهي. يرجى مراجعة مكتب الاستقبال لتسوية الاشتراك.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Schemas ---

class UserCreate(BaseModel):
    first_name: str 
    last_name: str
    birthdate: Optional[datetime] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: EmailStr
    password: str
    role: UserRole = UserRole.ATHLETE

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    working_hours: Optional[str] = None
    daily_advice: Optional[str] = None
    
    class Config:
        orm_mode = True

class AthleteRegistration(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    duration_months: int

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
class WorkoutClassCreate(BaseModel):
    class_name: str
    schedule: datetime
    capacity: int = 20

class WorkoutClassResponse(WorkoutClassCreate):
    id: int
    
    class Config:
        orm_mode = True

class InvoiceCreate(BaseModel):
    customer_id: int
    amount: float
    status: str = "Pending"

class InvoiceResponse(InvoiceCreate):
    id: int
    issue_date: datetime
    
    class Config:
        orm_mode = True

class SensorDataCreate(BaseModel):
    heart_rate: float
    steps: int
    calories: float

class SensorDataResponse(SensorDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

class AIPredictionResponse(BaseModel):
    id: int
    user_id: int
    injury_risk: float
    recommendation: str
    is_alert_sent: int
    prediction_time: datetime

    class Config:
        orm_mode = True

class SleepDataCreate(BaseModel):
    sleep_hours: float
    quality_score: int

class SleepDataResponse(SleepDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    training_days: int
    has_injury: bool
    injury_details: Optional[str] = None

class ExerciseLogCreate(BaseModel):
    exercise_name: str
    muscle_group: str
    max_weight: float

class ExerciseLogResponse(ExerciseLogCreate):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

class CoachInstruction(BaseModel):
    athlete_id: int
    message: str

class AnnouncementBase(BaseModel):
    title: str
    content: str
    priority: Optional[str] = "Normal"

class AnnouncementResponse(AnnouncementBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True


# --- WebSocket Endpoint ---

@app.websocket("/ws/alerts/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    يتصل بهذا المسار تطبيق المدرب أو الرياضي لاستقبال إشعارات الخطر بشكل لحظي.
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # نبقي الاتصال مفتوحاً ونقوم باستقبال البيانات لمنع إغلاقه
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# --- APIs ---

@app.post("/users/", response_model=UserResponse, tags=["Management: Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مسجل مسبقاً")
    
    hashed_pwd = get_password_hash(user.password)
    
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        birthdate=user.birthdate,
        address=user.address,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role
    )
    db.add(new_user)
    db.flush()
    if user.phone_number:
        new_phone = CustomerPhone(customer_id=new_user.id, phone_number=user.phone_number)
        db.add(new_phone)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/classes/", response_model=WorkoutClassResponse, tags=["Class Booking"])
def create_workout_class(workout_class: WorkoutClassCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """يقوم المدرب أو المسؤول بإنشاء حصة تدريبية جديدة."""
    if current_user.role not in [UserRole.COACH, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="يُسمح فقط للمدربين والمسؤولين بإنشاء حصص تدريبية")
    
    new_class = WorkoutClass(
        class_name=workout_class.class_name,
        schedule=workout_class.schedule,
        capacity=workout_class.capacity
    )
    db.add(new_class)
    db.flush()
    instructor_link = ClassInstructor(employee_id=current_user.id, workout_class_id=new_class.id)
    db.add(instructor_link)
    db.commit()
    db.refresh(new_class)
    return new_class


@app.post("/classes/{class_id}/book", tags=["Class Booking"])
def book_class(class_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """يقوم الرياضي بحجز مقعد في حصة تدريبية محددة."""
    workout_class = db.query(WorkoutClass).filter(WorkoutClass.id == class_id).first()
    if not workout_class:
        raise HTTPException(status_code=404, detail="الحصة غير موجودة")
    
    enrolled_count = db.query(ClassEnrollment).filter(ClassEnrollment.class_id == class_id).count()
    if enrolled_count >= workout_class.capacity:
        raise HTTPException(status_code=400, detail="عذراً، الحصة ممتلئة!")
    
    enrollment = ClassEnrollment(
        athlete_id=current_user.id,
        class_id=class_id,
        status="Booked"
    )
    db.add(enrollment)
    db.commit()
    return {"message": f"تم حجز الحصة '{workout_class.class_name}' بنجاح للمتدرب"}


@app.post("/invoices/", response_model=InvoiceResponse, tags=["Billing & Payments"])
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    """يقوم المسؤول بإنشاء فاتورة سداد للرياضي (لتجديد العضوية أو غيرها)."""
    new_invoice = PaymentInvoice(
        customer_id=invoice.customer_id,
        amount=invoice.amount,
        status=invoice.status
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice


@app.post("/sensor-data/", response_model=AIPredictionResponse, tags=["AI Analytics"])
async def ingress_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    تدفق مستمر للبيانات الحيوية.
    يقوم المحرك بقياس مستوى الخطر ويرسل التنبيه لحظياً عبر WebSockets.
    """
    
    new_sensor_data = SensorData(
        user_id=current_user.id,
        heart_rate=data.heart_rate,
        steps=data.steps,
        calories=data.calories
    )
    db.add(new_sensor_data)
    
    # استخراج الميزات وتشغيل محرك الذكاء الاصطناعي
    prediction_results = analyze_sensor_data({
        "heart_rate": data.heart_rate,
        "steps": data.steps,
        "calories": data.calories
    })
    
    # حفظ تقرير التعب والانذار
    new_prediction = AIPrediction(
        user_id=current_user.id,
        injury_risk=prediction_results['injury_risk'],
        recommendation=prediction_results['recommendation'],
        is_alert_sent=1 if prediction_results['is_alert_required'] else 0
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    
    # --- إرسال تحذير فوراً عبر WebSockets ---
    if prediction_results['is_alert_required']:
        alert_payload = {
            "type": "URGENT_ALERT",
            "message": f"تحذير خطر إصابة في نبض القلب لـ {current_user.first_name}! واصل للرقم: {data.heart_rate}",
            "recommendation": prediction_results['recommendation'],
            "risk_score": prediction_results['injury_risk']
        }
        await manager.send_alert_to_user(current_user.id, alert_payload)
        
        # تطبيق هيكلية إرسال التنبيه للمدرب (System sends Incident Alert to Coach)
        coaches = db.query(User).filter(User.role == UserRole.COACH).all()
        for coach in coaches:
            coach_payload = alert_payload.copy()
            coach_payload["message"] = f"تنبيه للمدرب: الرياضي {current_user.first_name} {current_user.last_name} في خطر الإجهاد/الإصابة!" 
            await manager.send_alert_to_user(coach.id, coach_payload)
    
    return new_prediction

@app.get("/users/me/predictions", response_model=List[AIPredictionResponse], tags=["Reports"])
def get_user_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    predictions = db.query(AIPrediction).filter(AIPrediction.user_id == current_user.id).order_by(AIPrediction.prediction_time.desc()).all()
    return predictions

@app.get("/users/me/sensor-history", response_model=List[SensorDataResponse], tags=["Reports"])
def get_sensor_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب سجل بيانات الحساسات الأخير للمستخدم لعرضه في الرسوم البيانية."""
    history = db.query(SensorData).filter(SensorData.user_id == current_user.id).order_by(SensorData.timestamp.desc()).limit(30).all()
    return sorted(history, key=lambda x: x.timestamp)

@app.get("/users/me/daily-summary", tags=["Reports"])
def get_daily_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تجميع البيانات حسب اليوم لعرض مقارنة الأداء للأيام الـ 7 الأخيرة."""
    # ملاحظة: تم استخدام SQLite date() أو PostgreSQL date() عبر func.date
    results = db.query(
        func.date(SensorData.timestamp).label('day'),
        func.max(SensorData.steps).label('max_steps'),
        func.avg(SensorData.heart_rate).label('avg_hr'),
        func.avg(SensorData.calories).label('avg_cal')
    ).filter(SensorData.user_id == current_user.id).group_by(func.date(SensorData.timestamp)).order_by('day').limit(7).all()
    
    return [{"day": r.day, "steps": r.max_steps, "avg_hr": round(r.avg_hr, 1) if r.avg_hr else 0, "avg_cal": round(r.avg_cal, 1) if r.avg_cal else 0} for r in results]

@app.post("/users/me/sleep/", response_model=SleepDataResponse, tags=["AI Analytics: Sleep"])
def record_sleep(data: SleepDataCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تسجيل بيانات النوم اليومية."""
    new_sleep = SleepData(user_id=current_user.id, sleep_hours=data.sleep_hours, quality_score=data.quality_score)
    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)
    return new_sleep

@app.get("/users/me/sleep-history/", response_model=List[SleepDataResponse], tags=["AI Analytics: Sleep"])
def get_sleep_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب سجل النوم للأسبوع الأخير."""
    return db.query(SleepData).filter(SleepData.user_id == current_user.id).order_by(SleepData.timestamp.desc()).limit(7).all()

@app.get("/users/me/sleep-recommendation/", tags=["AI Analytics: Sleep"])
def get_sleep_recommendation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """توليد توصية رياضية ذكية بناءً على جودة وكمية النوم."""
    latest = db.query(SleepData).filter(SleepData.user_id == current_user.id).order_by(SleepData.timestamp.desc()).first()
    if not latest:
        return {"recommendation": "يرجى تسجيل بيانات النوم أولاً للحصول على نصيحة مخصصة."}
    
    if latest.sleep_hours >= 7:
        return {
            "status": "Good",
            "recommendation": f"جودة نومك ممتازة اليوم ({latest.sleep_hours} ساعة). جسمك في وضع مثالي للمقاومة؛ ننصحك بالمشي 5000 خطوة وحرق 500 سعرة حرارية لتعزيز اللياقة.",
            "targets": {"steps": 5000, "calories": 500}
        }
    else:
        return {
            "status": "Poor",
            "recommendation": f"نومك كان أقل من المعدل ({latest.sleep_hours} ساعة). لتجنب الإجهاد، ننصحك بتمرين خفيف (2000 خطوة فقط) وتجنب التمارين الشاقة اليوم.",
            "targets": {"steps": 2000, "calories": 150}
        }


@app.get("/users/me", response_model=UserResponse, tags=["Management: Users"])
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/admin/retrain-models", tags=["Continuous Learning"])
def retrain_models_api():
    """
    يتصل بقاعدة البيانات لجمع بيانات الحساسات الأخيرة ويعيد تدريب نماذج الذكاء الاصطناعي لتحسين الدقة.
    (Data Pipeline / Continuous Learning)
    """
    success = continuous_learning.retrain_models_from_db()
    if success:
        return {"status": "success", "message": "تمت إعادة تدريب النماذج بنجاح. سيتم أخذ البيانات الجديدة في الحسبان."}
    else:
        raise HTTPException(status_code=500, detail="فشل في جلب البيانات الكافية لإعادة التدريب أو خطأ أثناء التدريب.")

@app.get("/coach/team-analytics/", tags=["Reports"])
def get_team_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    # 1. الحالات الحرجة (نبض عالي أو احتمالية إصابة عالية)
    critical_cases = db.query(AIPrediction).filter(AIPrediction.injury_risk > 0.60).order_by(AIPrediction.prediction_time.desc()).limit(10).all()
    
    # 2. إحصائيات عامة للفريق اليوم
    today = datetime.utcnow().date()
    avg_hr = db.query(func.avg(SensorData.heart_rate)).filter(func.date(SensorData.timestamp) == today).scalar() or 0
    total_steps = db.query(func.sum(SensorData.steps)).filter(func.date(SensorData.timestamp) == today).scalar() or 0
    total_athletes = db.query(User).filter(User.role == UserRole.ATHLETE).count()

    # تحويل البيانات لشكل أسهل للعرض
    detailed_cases = []
    for c in critical_cases:
        user = db.query(User).filter(User.id == c.user_id).first()
        detailed_cases.append({
            "athlete_name": f"{user.first_name} {user.last_name}",
            "risk": round(c.injury_risk * 100, 0),
            "recommendation": c.recommendation,
            "time": c.prediction_time.strftime("%H:%M")
        })

    return {
        "coach_name": current_user.first_name,
        "coach_email": current_user.email,
        "working_hours": current_user.working_hours,
        "daily_advice": current_user.daily_advice,
        "stats": {
            "avg_hr": round(avg_hr, 1) if avg_hr else 0,
            "total_steps": total_steps,
            "active_now": total_athletes
        },
        "critical_cases": detailed_cases
    }

@app.post("/coach/update-info/", tags=["Admin/Coach"])
def update_coach_info(working_hours: str, daily_advice: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تحديث ساعات العمل والنصيحة اليومية للمدرب."""
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="غير مصرح")
    current_user.working_hours = working_hours
    current_user.daily_advice = daily_advice
    db.commit()
    return {"status": "success", "message": "تم تحديث معلومات المدرب بنجاح"}

@app.get("/athletes/available-coaches/", tags=["Reports"])
def get_available_coaches(db: Session = Depends(get_db)):
    """جلب قائمة المدربين المتواجدين في النادي للرياضيين."""
    coaches = db.query(User).filter(User.role == UserRole.COACH).all()
    return [{
        "name": f"الكابتن {c.first_name} {c.last_name}",
        "hours": c.working_hours or "غير محدد",
        "advice": c.daily_advice or "لا توجد نصيحة حالية"
    } for c in coaches]

@app.post("/athletes/emergency/", tags=["AI Analytics"])
async def send_emergency(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """إرسال تنبيه طارئ (SOS) فوراً لجميع المدربين عبر WebSocket."""
    coaches = db.query(User).filter(User.role == UserRole.COACH).all()
    payload = {
        "type": "SOS_EMERGENCY",
        "message": f"🚨 نداء طوارئ عاجل من الرياضي {current_user.first_name}! يرجى التوجه لمكانه فوراً.",
        "user_id": current_user.id
    }
    for coach in coaches:
        await manager.send_alert_to_user(coach.id, payload)
    return {"status": "sent", "message": "تم إرسال نداء الاستغاثة للمدربين"}

@app.post("/users/me/generate-training-plan", tags=["AI Analytics"])
def api_generate_training_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    توليد خطة تدريبية مخصصة للرياضي بناءً على مقاييس أدائه وعدد أيام تمرينه.
    """
    days = current_user.training_days or 3
    injury = current_user.injury_details if current_user.has_injury else "لا يوجد"
    
    plans = {
        2: "اليوم 1: الجزء العلوي (صحة عامة)\nاليوم 2: الجزء السفلي (توازن)",
        3: "قائمة Split (3 أيام):\nاليوم 1: دفع (Push): صدر، أكتاف، تراي\nاليوم 2: سحب (Pull): ظهر، باي\nاليوم 3: أرجل وبطن",
        4: "قائمة Split (4 أيام):\nاليوم 1: علوي (قوة)\nاليوم 2: سفلي (قوة)\nاليوم 3: علوي (تضخيم)\nاليوم 4: سفلي (تضخيم)",
        5: "قائمة Split (5 أيام):\nاليوم 1: صدر\nاليوم 2: ظهر\nاليوم 3: أكتاف\nاليوم 4: أرجل\nاليوم 5: أذرع"
    }
    
    plan_text = plans.get(days, plans[3])
    if current_user.has_injury:
        plan_text += f"\n\n⚠️ ملاحظة طبية: نظراً لوجود إصابة ({injury})، يرجى تجنب الحركات التي تضغط على منطقة الإصابة."

    new_plan = TrainingPlan(
        user_id=current_user.id,
        plan_text=plan_text
    )
    db.add(new_plan)
    db.commit()
    return {"user_id": current_user.id, "ai_generated_plan": plan_text, "plan_id": new_plan.id}

@app.post("/memberships/", tags=["Admin/Coach"])
def manage_membership(customer_id: int, gym_id: int, end_date: datetime, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تفعيل نظام الاشتراكات: إدارة العضويات تاريخ البدء والانتهاء"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="يُسمح للمسؤول فقط بإدارة الاشتراكات")
    membership = GymMembership(customer_id=customer_id, gym_id=gym_id, end_date=end_date, status="Active")
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

class CoachParams(BaseModel):
    high_hr_threshold: Optional[int] = None
    medium_hr_threshold: Optional[int] = None
    injury_risk_threshold: Optional[float] = None

@app.post("/admin/coach-parameters", tags=["Admin/Coach"])
def update_parameters(params: CoachParams, current_user: User = Depends(get_current_user)):
    """تفاعل المدرب: تعديل بارامترات النماذج"""
    if current_user.role not in [UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(status_code=403, detail="غير مصرح")
    update_coach_thresholds(params.high_hr_threshold, params.medium_hr_threshold, params.injury_risk_threshold)
    return {"status": "success", "message": "تم بنجاح تحديث وتخصيص معايير الخطر للتدريب."}

@app.post("/admin/register-athlete", tags=["Admin/Management"])
def register_new_athlete_by_admin(reg: AthleteRegistration, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """من صفحة الإدارة: تسجيل رياضي جديد وتحديد مدة الاشتراك ليتم استخدامها في كل الصفحات."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="يُسمح للمسؤول فقط بتسجيل المشتركين")
    
    if db.query(User).filter(User.email == reg.email).first():
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مسجل مسبقاً")
        
    db_gym = db.query(Gym).first()
    gym_id = db_gym.id if db_gym else 1
    
    new_athlete = User(
        first_name=reg.first_name,
        last_name=reg.last_name,
        email=reg.email,
        hashed_password=get_password_hash(reg.password),
        role=UserRole.ATHLETE
    )
    db.add(new_athlete)
    db.flush()
    
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=reg.duration_months * 30)
    
    new_mem = GymMembership(
        customer_id=new_athlete.id,
        gym_id=gym_id,
        start_date=start_date,
        end_date=end_date,
        status="Active"
    )
    db.add(new_mem)
    db.commit()
    
    return {
        "status": "success", 
        "athlete_id": new_athlete.id, 
        "start_date": start_date.strftime("%Y-%m-%d"), 
        "end_date": end_date.strftime("%Y-%m-%d")
    }

@app.post("/admin/athletes/{user_id}/update", tags=["Admin/Management"])
def update_athlete_profile(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """يسمح للمسؤول بتعديل بيانات المشترك (الاسم أو الايميل)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="يُسمح للمسؤول فقط بتعديل المشتركين")
    
    target_user = db.query(User).filter(User.id == user_id, User.role == UserRole.ATHLETE).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="المشترك غير موجود")
        
    if update_data.first_name: target_user.first_name = update_data.first_name
    if update_data.last_name: target_user.last_name = update_data.last_name
    if update_data.email: target_user.email = update_data.email
    
    db.commit()
    return {"status": "success", "message": "تم التحديث بنجاح"}

@app.get("/admin/dashboard-stats", tags=["Admin/Management"])
def get_admin_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب إحصائيات الأعمال الشاملة للأدمن (مالي + نمو)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    total_users = db.query(User).count()
    total_athletes = db.query(User).filter(User.role == UserRole.ATHLETE).count()
    total_coaches = db.query(User).filter(User.role == UserRole.COACH).count()
    
    # حساب الإيرادات التقديرية (بافتراض 200 ريال للاشتراك)
    active_memberships = db.query(GymMembership).filter(GymMembership.status == "Active").count()
    total_revenue = active_memberships * 200
    
    # بيانات الرسم البياني للنمو (Mock data لغرض العرض)
    revenue_trend = [1200, 1500, 1800, 2400, total_revenue] 
    
    return {
        "total_revenue": f"{total_revenue} SAR",
        "active_memberships": active_memberships,
        "total_users": total_users,
        "athletes_count": total_athletes,
        "coaches_count": total_coaches,
        "revenue_trend": revenue_trend,
        "labels": ["يناير", "فبراير", "مارس", "أبريل", "مايو"]
    }

@app.get("/admin/users", tags=["Admin/Management"])
def list_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """قائمة بكافة المستخدمين في النظام."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="غير مصرح")
    return db.query(User).all()

# --- New Personal Trainer Features ---

@app.post("/users/me/profile", tags=["Management: Users"])
async def update_athlete_profile(profile: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تحديث الملف الشخصي الصحي والرياضي للرياضي."""
    current_user.training_days = profile.training_days
    current_user.has_injury = 1 if profile.has_injury else 0
    current_user.injury_details = profile.injury_details if profile.has_injury else ""
    db.commit()

    # إرسال تنبيه للمدرب إذا وجدت إصابة
    if profile.has_injury:
        coaches = db.query(User).filter(User.role == UserRole.COACH).all()
        alert_payload = {
            "type": "INJURY_REPORT",
            "message": f"🚨 تنبيه إصابة: الرياضي {current_user.first_name} أبلغ عن إصابة: {profile.injury_details}",
            "user_id": current_user.id
        }
        for coach in coaches:
            await manager.send_alert_to_user(coach.id, alert_payload)
            
    return {"status": "success", "message": "تم تحديث الملف الشخصي بنجاح."}

@app.post("/users/me/log-exercise", response_model=ExerciseLogResponse, tags=["Training Analysis"])
def log_exercise(log: ExerciseLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تسجيل أقصى وزن تم حمله لتمرين معين."""
    new_log = ExerciseLog(
        user_id=current_user.id,
        exercise_name=log.exercise_name,
        muscle_group=log.muscle_group,
        max_weight=log.max_weight
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@app.get("/users/me/smart-recommendation/{exercise_name}", tags=["Training Analysis"])
def get_smart_recommendation(exercise_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تقديم نصيحة ذكية للوزن المناسب بناءً على التاريخ والمجهود الحالي."""
    # جلب آخر وزن مسجل لهذا التمرين
    last_log = db.query(ExerciseLog).filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.exercise_name == exercise_name
    ).order_by(ExerciseLog.timestamp.desc()).first()
    
    if not last_log:
        return {"recommendation": "أول مرة لهذا التمرين؟ ابدأ بوزن خفيف لتجربة التكنيك."}

    # جلب آخر مستوى تنبؤ بالمخاطر/التعب
    last_prediction = db.query(AIPrediction).filter(AIPrediction.user_id == current_user.id).order_by(AIPrediction.prediction_time.desc()).first()
    
    risk_score = last_prediction.injury_risk if last_prediction else 0.0
    
    base_weight = last_log.max_weight
    
    if risk_score > 0.6: # تعب عالي
        suggested = round(base_weight * 0.9, 1)
        return {
            "status": "Fatigued",
            "last_weight": base_weight,
            "suggested_weight": suggested,
            "recommendation": f"مجهودك البدني مرتفع اليوم. ننصح بتخفيف الأوزان بنسبة 10% لتجنب الإصابة. تمرن على وزن {suggested}kg."
        }
    else: # حالة جيدة
        suggested = base_weight + 2.5
        return {
            "status": "Good",
            "last_weight": base_weight,
            "suggested_weight": suggested,
            "recommendation": f"حالتك البدنية ممتازة! جرب زيادة الوزن بمقدار 2.5kg لتحقيق تقدم. الوزن المقترح: {suggested}kg."
        }

# --- Coach Advanced Management ---

@app.get("/coach/team", tags=["Admin/Coach"])
def get_coach_team(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب قائمة بكافة الرياضيين وحالاتهم الحالية للمدرب."""
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    athletes = db.query(User).filter(User.role == UserRole.ATHLETE).all()
    team_data = []
    
    for a in athletes:
        # جلب آخر حالة مجهود
        last_pred = db.query(AIPrediction).filter(AIPrediction.user_id == a.id).order_by(AIPrediction.prediction_time.desc()).first()
        status = "Safe"
        if a.has_injury:
            status = "Injured"
        elif last_pred and last_pred.injury_risk > 0.6:
            status = "Critical"
            
        # جلب آخر نبض وسجل آخر زيارة
        last_sensor = db.query(SensorData).filter(SensorData.user_id == a.id).order_by(SensorData.timestamp.desc()).first()
        last_hr = last_sensor.heart_rate if last_sensor else 0
        last_visit_raw = last_sensor.timestamp if last_sensor else None
        
        last_visit_str = "لم يزر النادي بعد"
        if last_visit_raw:
            months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
            try:
                last_visit_str = f"{last_visit_raw.day} {months[last_visit_raw.month-1]} {last_visit_raw.strftime('%I:%M %p')}"
            except:
                last_visit_str = last_visit_raw.strftime("%Y-%m-%d %H:%M")
            
        team_data.append({
            "id": a.id,
            "name": f"{a.first_name} {a.last_name}",
            "email": a.email,
            "status": status,
            "injury_details": a.injury_details if a.has_injury else None,
            "last_hr": last_hr,
            "last_visit": last_visit_str
        })
    return team_data

@app.get("/coach/athlete/{athlete_id}/details", tags=["Admin/Coach"])
def get_athlete_details_for_coach(athlete_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب تفاصيل دقيقة (تاريخية) لرياضي معين لعرضها للمدرب."""
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    athlete = db.query(User).filter(User.id == athlete_id).first()
    if not athlete: raise HTTPException(status_code=404, detail="المشترك غير موجود")
    
    history = db.query(SensorData).filter(SensorData.user_id == athlete_id).order_by(SensorData.timestamp.desc()).limit(20).all()
    logs = db.query(ExerciseLog).filter(ExerciseLog.user_id == athlete_id).order_by(ExerciseLog.timestamp.desc()).limit(10).all()
    
    return {
        "profile": {
            "name": f"{athlete.first_name} {athlete.last_name}",
            "training_days": athlete.training_days,
            "has_injury": athlete.has_injury,
            "injury_details": athlete.injury_details
        },
        "sensor_history": [{
            "timestamp": h.timestamp,
            "heart_rate": h.heart_rate,
            "steps": h.steps,
            "calories": h.calories
        } for h in history],
        "exercise_logs": [{
            "exercise_name": l.exercise_name,
            "max_weight": l.max_weight,
            "timestamp": l.timestamp
        } for l in logs]
    }

@app.post("/coach/send-instruction", tags=["Admin/Coach"])
async def send_coach_instruction(instruction: CoachInstruction, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """إرسال توجيه مباشر من المدرب إلى رياضي معين عبر الـ WebSocket."""
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    payload = {
        "type": "COACH_DIRECT_MESSAGE",
        "coach_name": current_user.first_name,
        "message": instruction.message
    }
    await manager.send_alert_to_user(instruction.athlete_id, payload)
    return {"status": "sent"}

@app.post("/coach/mark-recovered/{athlete_id}", tags=["Admin/Coach"])
def mark_athlete_recovered(athlete_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تغيير حالة الرياضي من مصاب إلى معافى."""
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    athlete = db.query(User).filter(User.id == athlete_id).first()
    if athlete:
        athlete.has_injury = 0
        athlete.injury_details = ""
        db.commit()
    return {"status": "success"}

# --- Public Announcements ---

@app.post("/admin/announcements", response_model=AnnouncementResponse, tags=["Admin/Management"])
def create_announcement(ann: AnnouncementBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """نشر إعلان جديد من قبل الأدمن."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    new_ann = Announcement(
        title=ann.title,
        content=ann.content,
        priority=ann.priority
    )
    db.add(new_ann)
    db.commit()
    db.refresh(new_ann)
    return new_ann

@app.get("/announcements", response_model=List[AnnouncementResponse], tags=["Public"])
def get_announcements(db: Session = Depends(get_db)):
    """جلب آخر 5 إعلانات عامة للجميع."""
    return db.query(Announcement).order_by(Announcement.timestamp.desc()).limit(5).all()

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)

