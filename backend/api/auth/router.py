from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "OFFICER"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    status: str

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin):
    # Stub login verification
    if payload.email == "admin@police.gov.in" and payload.password == "admin123":
        return TokenResponse(
            access_token="mock_admin_jwt_token_stub_2026",
            role="ADMIN"
        )
    elif payload.email == "sp@police.gov.in" and payload.password == "sp123":
        return TokenResponse(
            access_token="mock_superintendent_jwt_token_stub_2026",
            role="SUPERINTENDENT"
        )
    elif payload.email == "officer@police.gov.in" and payload.password == "officer123":
        return TokenResponse(
            access_token="mock_officer_jwt_token_stub_2026",
            role="OFFICER"
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    )

@router.post("/register", response_model=UserProfile)
def register(payload: UserRegister):
    return UserProfile(
        id=999,
        name=payload.name,
        email=payload.email,
        role=payload.role,
        status="active"
    )

@router.get("/me", response_model=UserProfile)
def get_me():
    return UserProfile(
        id=1,
        name="Officer Stub",
        email="officer@police.gov.in",
        role="OFFICER",
        status="active"
    )
