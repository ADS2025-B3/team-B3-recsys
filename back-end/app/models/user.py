from sqlmodel import Field
from .base import SQLModel
from enum import Enum
from pydantic import EmailStr

class UserRole(str, Enum):
    analyst = "analyst"
    user = "user"
    admin = "admin"

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.user)
    is_active: bool = True


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = None  # type: ignore
    full_name: str | None = None
    password: str | None = None


class UserUpdateMe(SQLModel):
    email: EmailStr | None = None
    full_name: str | None = None

class UpdatePassword(SQLModel):
    current_password: str
    new_password: str

# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int

class UsersOut(SQLModel):
    data: list[UserOut]
    count: int

# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str