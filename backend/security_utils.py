from cryptography.fernet import Fernet
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

# --- Security & Privacy Configuration ---
# In a real environment, load this securely from an environment variable!
SECRET_KEY = os.environ.get("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 1 day

DB_ENCRYPTION_KEY = os.environ.get("DB_ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(DB_ENCRYPTION_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def encrypt_sensitive_data(plain_text: str) -> str:
    """
    يقوم بتشفير البيانات الشخصية قبل تخزينها في قاعدة البيانات (Data at Rest Encryption).
    """
    if not plain_text:
        return ""
    encrypted_bytes = cipher_suite.encrypt(plain_text.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_sensitive_data(encrypted_text: str) -> str:
    """
    لفك تشفير البيانات عند الحاجة لعرضها للمستخدم صاحب الصلاحية فقط.
    """
    if not encrypted_text:
        return ""
    decrypted_bytes = cipher_suite.decrypt(encrypted_text.encode('utf-8'))
    return decrypted_bytes.decode('utf-8')

# Example Usage inside models/main.py (For Biometric or PII data):
# db_user.medical_history = encrypt_sensitive_data("Has a history of asthma")
