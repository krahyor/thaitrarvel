from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from ..models.default_setting_model import ProvinceEnum


# Pydantic models สำหรับ request/response
class BaseProvinceTax(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    province: ProvinceEnum
    tax: float


class ProvinceTax(BaseProvinceTax):
    id: int


class RegisteredProvinceTax(BaseModel):
    id: int
    user_id: int
    name: str
    email: EmailStr
    main_province_id: int
    main_province_tax: float
    secondary_province_id: Optional[int] = None
    secondary_province_tax: Optional[float] = None


class RegisterProvinceTaxRequest(BaseModel):
    name: str
    email: EmailStr
    main_province_id: int
    secondary_province_id: Optional[int] = None
