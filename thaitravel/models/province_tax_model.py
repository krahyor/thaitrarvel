from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlmodel import SQLModel, Field, Relationship
from .default_setting_model import ProvinceEnum
from .user_model import DBUser


class DBBaseProvinceTax(SQLModel, table=True):
    __tablename__ = "provice_tax"
    id: int | None = Field(default=None, primary_key=True)
    province: ProvinceEnum = Field(sa_column_kwargs={"unique": True})
    tax: float

    # Relationship
    registered_main: list["DBRegisteredProvinceTax"] = Relationship(
        back_populates="main_province_ref",
        sa_relationship_kwargs={
            "foreign_keys": "[DBRegisteredProvinceTax.main_province_id]"
        },
    )
    registered_secondary: list["DBRegisteredProvinceTax"] = Relationship(
        back_populates="secondary_province_ref",
        sa_relationship_kwargs={
            "foreign_keys": "[DBRegisteredProvinceTax.secondary_province_id]"
        },
    )


class DBRegisteredProvinceTax(SQLModel, table=True):
    __tablename__ = "registered_province_tax"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    email: str

    main_province_id: int = Field(foreign_key="provice_tax.id")
    secondary_province_id: Optional[int] = Field(
        default=None, foreign_key="provice_tax.id"
    )
    main_province_tax: float
    secondary_province_tax: Optional[float] = Field(default=None)

    # Relationship
    main_province_ref: Optional["DBBaseProvinceTax"] = Relationship(
        back_populates="registered_main",
        sa_relationship_kwargs={
            "foreign_keys": "[DBRegisteredProvinceTax.main_province_id]"
        },
    )
    secondary_province_ref: Optional["DBBaseProvinceTax"] = Relationship(
        back_populates="registered_secondary",
        sa_relationship_kwargs={
            "foreign_keys": "[DBRegisteredProvinceTax.secondary_province_id]"
        },
    )


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
