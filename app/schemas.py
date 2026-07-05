from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from typing import Optional

class EmployeeBase(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    birth_date: date
    gender: str = Field(..., pattern="^(M|F)$")
    phone: Optional[str] = Field(None, max_length=20)
    photo: Optional[str] = None

    @field_validator('gender')
    def validate_gender(cls, v: str) -> str:
        if v not in ('M', 'F'):
            raise ValueError('Пол должен быть M или F')
        return v

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)