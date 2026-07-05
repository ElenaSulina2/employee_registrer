from datetime import datetime, date
from typing import Optional
from app.utils.constants import GENDER_CHOICES, DATE_FORMAT


def validate_gender(gender: str) -> str:
    if gender not in GENDER_CHOICES:
        raise ValueError("Неверное значение пола. Допустимы: M или F")
    return gender


def parse_date(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        raise ValueError(f"Неверный формат даты. Используйте {DATE_FORMAT}")


def validate_and_parse_employee_data(
    last_name: str,
    first_name: str,
    birth_date: str,
    gender: str,
    middle_name: Optional[str] = None,
    phone: Optional[str] = None,
) -> dict:
    if not last_name or not first_name:
        raise ValueError("Фамилия и Имя обязательны")
    validated_gender = validate_gender(gender)
    validated_birth_date = parse_date(birth_date)
    return {
        "last_name": last_name.strip(),
        "first_name": first_name.strip(),
        "middle_name": middle_name.strip() if middle_name else None,
        "birth_date": validated_birth_date,
        "gender": validated_gender,
        "phone": phone.strip() if phone else None,
    }
