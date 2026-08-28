from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field("user", max_length=20)
    is_active: bool = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Auth Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match")
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from current password")
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Category Schemas ---
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    current_amount: int = Field(0, ge=0)
    min_stock_threshold: int = Field(5, ge=0)
    image_path: Optional[str] = Field(None, max_length=255)
    category_id: int = Field(..., gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    current_amount: Optional[int] = Field(None, ge=0)
    min_stock_threshold: Optional[int] = Field(None, ge=0)
    image_path: Optional[str] = Field(None, max_length=255)
    category_id: Optional[int] = Field(None, gt=0)


class ProductResponse(ProductBase):
    id: int
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockAdjustment(BaseModel):
    change_amount: int  # Can be positive or negative
    reason: Optional[str] = Field(None, max_length=255)


# --- Stock Log Schemas ---
class StockLogResponse(BaseModel):
    user_name: str
    product_name: str
    previous_amount: int
    new_amount: int
    reason: Optional[str]
    created_at: datetime
    difference: int

    model_config = ConfigDict(from_attributes=True)
