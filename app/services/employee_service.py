from typing import Any, Dict, List, Tuple, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils.constants import MAX_PHOTO_SIZE_BYTES
from app.utils.helpers import save_uploaded_photo, delete_photo
from app.utils.validators import validate_and_parse_employee_data
from app.utils.filters import get_gender_filter


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_employee(self, employee_id: int) -> Optional[schemas.Employee]:
        db_employee = crud.get_employee(self.db, employee_id)
        if db_employee:
            return schemas.Employee.model_validate(db_employee)
        return None

    def get_employees_with_filters(
        self, params: schemas.EmployeeSearchParams
    ) -> Tuple[List[schemas.Employee], int, int]:
        gender = get_gender_filter(params.gender_male, params.gender_female)
        skip = (params.page - 1) * params.size

        db_employees = crud.get_employees(
            self.db,
            skip=skip,
            limit=params.size,
            search=params.search,
            gender=gender,
            age_from=params.get_age_from_int(),
            age_to=params.get_age_to_int(),
        )
        total = crud.count_employees(
            self.db,
            search=params.search,
            gender=gender,
            age_from=params.get_age_from_int(),
            age_to=params.get_age_to_int(),
        )
        total_pages = (total + params.size - 1) // params.size

        employees = [schemas.Employee.model_validate(emp) for emp in db_employees]
        return employees, total, total_pages

    def process_employee_form(
        self, form_data: schemas.EmployeeFormData, photo: Optional[UploadFile] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Валидирует данные формы и обрабатывает фото.
        Возвращает (validated_data, error_message).
        """
        try:
            validated = validate_and_parse_employee_data(
                form_data.last_name,
                form_data.first_name,
                form_data.birth_date,
                form_data.gender,
                form_data.middle_name,
                form_data.phone,
            )
        except ValueError as e:
            return None, str(e)

        validated["middle_name"] = validated.get("middle_name") or ""
        validated["phone"] = validated.get("phone") or ""

        photo_filename = None
        if photo and photo.filename:
            filename, err = save_uploaded_photo(photo, MAX_PHOTO_SIZE_BYTES)
            if err:
                return None, err
            photo_filename = filename

        validated["photo"] = photo_filename
        return validated, None

    def create_employee(self, validated_data: dict) -> schemas.Employee:
        employee_data = schemas.EmployeeCreate(
            last_name=validated_data["last_name"],
            first_name=validated_data["first_name"],
            middle_name=validated_data["middle_name"],
            birth_date=validated_data["birth_date"],
            gender=validated_data["gender"],
            phone=validated_data["phone"],
            photo=validated_data["photo"],
        )
        db_employee = crud.create_employee(self.db, employee_data)
        return schemas.Employee.model_validate(db_employee)

    def update_employee(self, employee_id: int, validated_data: dict) -> Optional[schemas.Employee]:
        """Обновляет сотрудника без обработки фото (фото уже в validated_data)."""
        employee_data = schemas.EmployeeUpdate(
            last_name=validated_data["last_name"],
            first_name=validated_data["first_name"],
            middle_name=validated_data["middle_name"],
            birth_date=validated_data["birth_date"],
            gender=validated_data["gender"],
            phone=validated_data["phone"],
            photo=validated_data.get("photo"),  # может быть None или новое имя
        )
        db_employee = crud.update_employee(self.db, employee_id, employee_data)
        if db_employee:
            return schemas.Employee.model_validate(db_employee)
        return None

    def delete_employee(self, employee_id: int) -> bool:
        employee = crud.get_employee(self.db, employee_id)
        if employee:
            delete_photo(employee.photo)
        return crud.delete_employee(self.db, employee_id)