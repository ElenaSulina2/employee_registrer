from pydantic import BaseModel, ConfigDict, Field, computed_field
from datetime import date
from typing import Optional, List

from app.utils.helpers import calculate_age


class EmployeeBase(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    birth_date: date
    gender: str = Field(..., pattern="^(M|F)$")
    phone: Optional[str] = Field(None, max_length=20)
    photo: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def age(self) -> int:
        """Возраст сотрудника, вычисляется автоматически."""
        return calculate_age(self.birth_date)


class EmployeeSearchParams(BaseModel):
    search: str = Field(default="", description="Поиск по ФИО")
    gender_male: bool = Field(default=False, description="Фильтр по мужскому полу")
    gender_female: bool = Field(default=False, description="Фильтр по женскому полу")
    age_from: Optional[int] = Field(default=None, ge=0, description="Возраст от")
    age_to: Optional[int] = Field(default=None, ge=0, description="Возраст до")
    page: int = Field(default=1, ge=1, description="Номер страницы")
    size: int = Field(default=10, ge=1, le=100, description="Размер страницы")


class EmployeeFormData(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    birth_date: str = Field(..., description="Дата рождения в формате YYYY-MM-DD")
    gender: str = Field(..., pattern="^(M|F)$")
    phone: Optional[str] = Field(None, max_length=20)


class IndexPageContext(BaseModel):
    employees: List[Employee]
    page: int
    size: int
    total: int
    total_pages: int
    search: str
    gender_male: bool
    gender_female: bool
    age_from: Optional[int]
    age_to: Optional[int]
    MAX_PHOTO_SIZE_KB: int

    @classmethod
    def from_employees(
        cls,
        employees: List[Employee],
        total: int,
        params: EmployeeSearchParams,
        max_photo_size_kb: int,
    ) -> "IndexPageContext":
        total_pages = (total + params.size - 1) // params.size
        return cls(
            employees=employees,
            page=params.page,
            size=params.size,
            total=total,
            total_pages=total_pages,
            search=params.search,
            gender_male=params.gender_male,
            gender_female=params.gender_female,
            age_from=params.age_from,
            age_to=params.age_to,
            MAX_PHOTO_SIZE_KB=max_photo_size_kb,
        )

    def to_template_dict(self) -> dict:
        """Возвращает словарь для передачи в шаблон."""
        return self.model_dump()
