from pydantic import BaseModel, EmailStr
from typing import Optional


# ==========================
# Register Schema
# ==========================
class RegisterUser(BaseModel):
    name: str
    phone: str
    id_number: str
    age: int
    company: str
    email: EmailStr
    password: str


# ==========================
# Login Schema
# ==========================
class LoginUser(BaseModel):
    email: EmailStr
    password: str


# ==========================
# Interaction Schema
# ==========================
class InteractionSchema(BaseModel):
    hcp_name: str
    topics: str
    sentiment: str
    follow_up: str
    outcomes: str
    date: str
    time: str


# ==========================
# History Response Schema
# ==========================
class HistorySchema(BaseModel):
    serial_no: int
    hcp_name: str
    topics: str
    sentiment: str
    outcomes: str
    follow_up: str
    date: str
    time: str


# ==========================
# User Profile Schema
# ==========================
class UserProfileSchema(BaseModel):
    name: str
    phone: str
    id_number: str
    age: int
    company: str
    email: EmailStr


# ==========================
# JWT Response Schema
# ==========================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==========================
# Generic API Response
# ==========================
class MessageResponse(BaseModel):
    message: str