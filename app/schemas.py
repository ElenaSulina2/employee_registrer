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
        return calculate_age(self.birth_date)


class EmployeeSearchParams(BaseModel):
    search: str = Field(default="", description="Поиск по ФИО")
    gender_male: bool = Field(default=False, description="Фильтр по мужскому полу")
    gender_female: bool = Field(default=False, description="Фильтр по женскому полу")
    age_from: Optional[str] = Field(default=None, description="Возраст от (строка)")
    age_to: Optional[str] = Field(default=None, description="Возраст до (строка)")
    page: int = Field(default=1, ge=1, description="Номер страницы")
    size: int = Field(default=10, ge=1, le=100, description="Количество записей на странице")

    def get_age_from_int(self) -> Optional[int]:
        if self.age_from and self.age_from.strip():
            try:
                return int(self.age_from)
            except ValueError:
                return None
        return None

    def get_age_to_int(self) -> Optional[int]:
        if self.age_to and self.age_to.strip():
            try:
                return int(self.age_to)
            except ValueError:
                return None
        return None


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
    page_range: List[int]
    base_query: str
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
        max_display_pages: int = 5,
    ) -> "IndexPageContext":
        total_pages = (total + params.size - 1) // params.size if total > 0 else 1
        page_range = cls._get_page_range(params.page, total_pages, max_display_pages)
        base_query = cls._build_base_query(params)

        return cls(
            employees=employees,
            page=params.page,
            size=params.size,
            total=total,
            total_pages=total_pages,
            page_range=page_range,
            base_query=base_query,
            search=params.search,
            gender_male=params.gender_male,
            gender_female=params.gender_female,
            age_from=params.get_age_from_int(),
            age_to=params.get_age_to_int(),
            MAX_PHOTO_SIZE_KB=max_photo_size_kb,
        )

    @staticmethod
    def _get_page_range(current_page: int, total_pages: int, max_display: int = 5) -> List[int]:
        if total_pages <= max_display:
            return list(range(1, total_pages + 1))
        half = max_display // 2
        start = max(1, current_page - half)
        end = min(total_pages, start + max_display - 1)
        if end - start < max_display - 1:
            start = max(1, end - max_display + 1)
        return list(range(start, end + 1))

    @staticmethod
    def _build_base_query(params: EmployeeSearchParams) -> str:
        parts = []
        if params.search:
            parts.append(f"search={params.search}")
        if params.gender_male:
            parts.append("gender_male=true")
        if params.gender_female:
            parts.append("gender_female=true")
        age_from = params.get_age_from_int()
        if age_from is not None:
            parts.append(f"age_from={age_from}")
        age_to = params.get_age_to_int()
        if age_to is not None:
            parts.append(f"age_to={age_to}")
        return "&".join(parts)

    def to_template_dict(self) -> dict:
        return self.model_dump()