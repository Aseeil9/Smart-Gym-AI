from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "Admin"
    COACH = "Coach"
    ATHLETE = "Athlete"

class FatigueLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class InjuryRiskLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Gym(Base):
    __tablename__ = 'gyms'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=True)
    
    memberships = relationship("GymMembership", back_populates="gym")
    workout_classes = relationship("WorkoutClass", back_populates="gym")

class CustomerPhone(Base):
    __tablename__ = 'customer_phones'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    phone_number = Column(String(20), nullable=False)
    
    customer = relationship("User", back_populates="phones")

class ClassInstructor(Base):
    __tablename__ = 'class_instructors'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('users.id'))
    workout_class_id = Column(Integer, ForeignKey('workout_classes.id'))

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthdate = Column(DateTime, nullable=True)
    address = Column(String(200), nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ATHLETE)  # Used to identify GymEmployee/GymManager
    working_hours = Column(String(100), nullable=True) # مثال: 8AM - 4PM
    daily_advice = Column(String(500), nullable=True) # نصيحة عامة للمتدربين
    
    # حقول الملف الشخصي الجديد
    training_days = Column(Integer, default=3)
    has_injury = Column(Integer, default=0) # 0: No, 1: Yes
    injury_details = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    phones = relationship("CustomerPhone", back_populates="customer")
    sensor_data = relationship("SensorData", back_populates="user")
    performance_metrics = relationship("PerformanceMetrics", back_populates="user")
    predictions = relationship("AIPrediction", back_populates="user")
    memberships = relationship("GymMembership", back_populates="customer")
    instructed_classes = relationship("WorkoutClass", secondary='class_instructors', back_populates="instructors")
    enrollments = relationship("ClassEnrollment", back_populates="athlete")
    invoices = relationship("PaymentInvoice", back_populates="customer")
    sleep_data = relationship("SleepData", back_populates="user")
    exercise_logs = relationship("ExerciseLog", back_populates="user")

class GymMembership(Base):
    __tablename__ = 'gym_memberships'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    gym_id = Column(Integer, ForeignKey('gyms.id'))
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True) # تاريخ الانتهاء
    status = Column(String(50), default="Active")
    
    customer = relationship("User", back_populates="memberships")
    gym = relationship("Gym", back_populates="memberships")

class WorkoutClass(Base):
    __tablename__ = 'workout_classes'
    
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(100), nullable=False)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=True)
    schedule = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=20)
    
    gym = relationship("Gym", back_populates="workout_classes")
    instructors = relationship("User", secondary='class_instructors', back_populates="instructed_classes")
    enrollments = relationship("ClassEnrollment", back_populates="workout_class")

class ClassEnrollment(Base):
    __tablename__ = 'class_enrollments'
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey('users.id'))
    class_id = Column(Integer, ForeignKey('workout_classes.id'))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Booked") # Booked, Cancelled, Attended
    
    athlete = relationship("User", back_populates="enrollments")
    workout_class = relationship("WorkoutClass", back_populates="enrollments")

class PaymentInvoice(Base):
    __tablename__ = 'payment_invoices'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    issue_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Pending") # Pending, Paid, Overdue
    
    customer = relationship("User", back_populates="invoices")

class SensorData(Base):
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    heart_rate = Column(Float)       
    steps = Column(Integer)          
    calories = Column(Float)  
    
    user = relationship("User", back_populates="sensor_data")

class PerformanceMetrics(Base):
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow) # تم تغيير الاسم بناءً على المتطلبات
    fatigue_level = Column(Enum(FatigueLevel), default=FatigueLevel.LOW) # تم تحويله إلى Enum ودمجه هنا
    endurance_score = Column(Float)
    recovery_rate = Column(Float)
    
    user = relationship("User", back_populates="performance_metrics")

class AIPrediction(Base):
    __tablename__ = 'ai_predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    prediction_time = Column(DateTime, default=datetime.utcnow)
    injury_risk = Column(Float) # تم إرجاعه إلى Float لأن نماذج الـ ML ترجع احتمالية رقمية
    # تم إزالة fatigue_prediction لوجوده في PerformanceMetrics
    recommendation = Column(String(500))    
    is_alert_sent = Column(Integer, default=0) 
    
    user = relationship("User", back_populates="predictions")
    training_plans = relationship("TrainingPlan", back_populates="prediction")

class TrainingPlan(Base):
    __tablename__ = 'training_plans'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    prediction_id = Column(Integer, ForeignKey('ai_predictions.id'), nullable=True) # ربط اختياري
    plan_text = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prediction = relationship("AIPrediction", back_populates="training_plans")

class SleepData(Base):
    __tablename__ = 'sleep_data'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    sleep_hours = Column(Float)
    quality_score = Column(Integer) # 1 to 100
    
    user = relationship("User", back_populates="sleep_data")

class ExerciseLog(Base):
    __tablename__ = 'exercise_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    exercise_name = Column(String(100)) # مثال: Bench Press, Squat
    muscle_group = Column(String(100)) # مثال: Chest, Legs
    max_weight = Column(Float) # أقصى وزن بالكيلو
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="exercise_logs")

class Announcement(Base):
    __tablename__ = 'announcements'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    priority = Column(String(20), default="Normal") # Normal, Urgent
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- Database Setup ---
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "..", "data", "smart_gym.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
