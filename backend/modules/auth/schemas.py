
from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID

# BaseModel :- This is the class of pydantic, By inheriting from it, we define the shape of the data.
# Request Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    # This is the custom validation, where we write our own rules
    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be atleast 8 character")
        return value

# Response Schema
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    plan: str

    class Config:
        from_attributes = True

# Login request schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Token response schema
class TokenResponse(BaseModel):
    access_token: str    # long string
    token_type: str = 'bearer'   # always bearer, because of industry standard, This tell which type of token