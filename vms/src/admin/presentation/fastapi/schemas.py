from pydantic import BaseModel, EmailStr, Field


class RegisterSchema(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3)
    password: str = Field(min_length=6)
    city_ids: list[str] = []
    is_admin: bool = False


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    city_ids: list[str]
    is_admin: bool
    is_active: bool


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
