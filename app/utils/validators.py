from datetime import datetime, date
from typing import Optional
from app.utils.constants import GENDER_CHOICES, DATE_FORMAT

import re



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
    phone: Optional[str] = None
) -> dict:
    # 1. Обязательные поля
    if not last_name or not first_name:
        raise ValueError("Фамилия и Имя обязательны")

    # 2. Парсинг и валидация даты рождения
    try:
        birth = parse_date(birth_date)
    except ValueError as e:
        raise ValueError(str(e))  # пробрасываем дальше

    # 3. Проверка, что дата не в будущем
    today = date.today()
    if birth > today:
        raise ValueError("Дата рождения не может быть в будущем")

    # 4. Проверка возраста (не более 100 лет)
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    if age > 100:
        raise ValueError("Возраст не может превышать 100 лет")

    # 5. Валидация пола
    validated_gender = validate_gender(gender)

    # 6. Валидация телефона
    if phone and not re.match(r'^\+?[0-9\s\-()]{7,20}$', phone):
        raise ValueError("Некорректный номер телефона")

    # 7. Очистка строк
    cleaned_last_name = last_name.strip()
    cleaned_first_name = first_name.strip()
    cleaned_middle_name = middle_name.strip() if middle_name else None
    cleaned_phone = phone.strip() if phone else None

    return {
        "last_name": cleaned_last_name,
        "first_name": cleaned_first_name,
        "middle_name": cleaned_middle_name,
        "birth_date": birth,
        "gender": validated_gender,
        "phone": cleaned_phone,
    }


