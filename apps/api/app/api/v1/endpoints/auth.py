from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import structlog

from app.core.config import settings
from app.core.database import prisma
from app.core.exceptions import UnauthorizedError, ValidationError

logger = structlog.get_logger()

router = APIRouter()
security = HTTPBearer(auto_error=False)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    plan: str
    credits_remaining: int
    credits_used: int


def create_access_token(user_id: str, email: str, plan: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "plan": plan,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRY_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    if not credentials:
        raise UnauthorizedError("Missing authorization header")

    try:
        payload = jwt.decode(
            credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.JWTError:
        raise UnauthorizedError("Invalid token")

    user = await prisma.user.find_unique(where={"id": payload["sub"]})
    if not user:
        raise UnauthorizedError("User not found")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "plan": user.plan,
        "credits_remaining": user.credits_remaining,
        "credits_used": user.credits_used,
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    existing = await prisma.user.find_unique(where={"email": data.email})
    if existing:
        raise ValidationError("Email already registered")

    password_hash = hash_password(data.password)
    user = await prisma.user.create(
        data={
            "email": data.email,
            "passwordHash": password_hash,
            "name": data.name,
            "plan": "FREE",
            "creditsRemaining": settings.FREE_TIER_MONTHLY_CREDITS,
        }
    )

    access_token = create_access_token(user.id, user.email, user.plan)
    refresh_token = create_refresh_token(user.id)

    logger.info("User registered", user_id=user.id, email=user.email)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRY_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    user = await prisma.user.find_unique(where={"email": data.email})
    if not user or not user.passwordHash or not verify_password(data.password, user.passwordHash):
        raise UnauthorizedError("Invalid email or password")

    access_token = create_access_token(user.id, user.email, user.plan)
    refresh_token = create_refresh_token(user.id)

    logger.info("User logged in", user_id=user.id, email=user.email)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRY_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise UnauthorizedError("Missing refresh token")

    try:
        payload = jwt.decode(
            credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Refresh token expired")
    except jwt.JWTError:
        raise UnauthorizedError("Invalid refresh token")

    user = await prisma.user.find_unique(where={"id": payload["sub"]})
    if not user:
        raise UnauthorizedError("User not found")

    access_token = create_access_token(user.id, user.email, user.plan)
    new_refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_EXPIRY_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}