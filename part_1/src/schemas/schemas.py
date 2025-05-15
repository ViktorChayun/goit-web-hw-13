from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ContactSchema(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr = Field()
    phone_number: str = Field(max_length=20)
    birthday: date = Field()
    additional_info: Optional[str] = Field()


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=6, max_length=12)


class UserDbModel(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: Optional[str] = None
    confirmed: bool

    class Config:
        orm_mode = True


class UserResponseModel(BaseModel):
    user: UserDbModel
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=12)
