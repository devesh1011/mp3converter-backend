from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import jwt
import datetime
import base64
import os

# Load .env for local development (optional in Docker/K8s)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars

from models import User, SessionLocal
from schema import UserCreate, TokenResponse, RegisterResponse, ValidateResponse
from passlib.context import CryptContext
from sqlalchemy import select


pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login", response_model=TokenResponse)
def login(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("authorization")

    if not auth or not auth.startswith("Basic "):
        raise HTTPException(401, "Missing or invalid credentials")

    try:
        decoded = base64.b64decode(auth[6:]).decode()
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(401, "Invalid credentials")

    result = db.execute(select(User).where(User.username == username)).first()
    user = result[0] if result else None

    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(401, "Invalid")

    token = create_jwt(username=user.username, secret=os.getenv("JWT_SECRET", "secret"))

    return {"access_token": token}


@app.post("/register", response_model=RegisterResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    exists = db.execute(select(User).where(User.username == data.username)).first()

    if exists:
        raise HTTPException(400, "Username already registered")

    hashed = pwd_context.hash(data.password)
    user = User(name=data.name, username=data.username, hashed_password=hashed)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/validate", response_model=ValidateResponse)
def validate(request: Request):
    auth = request.headers.get("authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")

    token = auth[7:]

    try:
        payload = jwt.decode(
            token, os.getenv("JWT_SECRET", "secret"), algorithms=["HS256"]
        )
        return {"username": payload["sub"], "valid": True}
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


def create_jwt(username: str, secret: str):
    return jwt.encode(
        {
            "sub": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        },
        secret,
        algorithm="HS256",
    )
