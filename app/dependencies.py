from typing import Optional
from fastapi import Form, UploadFile, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EmployeeFormData
from app.services.employee_service import EmployeeService
from app.utils.template_utils import render_form_error
from app.utils.helpers import delete_photo


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(db)


def get_employee_form(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: Optional[str] = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
) -> EmployeeFormData:
    return EmployeeFormData(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone=phone,
    )


def handle_employee_form(
    request: Request,
    form_data: EmployeeFormData,
    photo: Optional[UploadFile],
    service: EmployeeService,
    employee_id: Optional[int] = None,
):
    employee = None
    if employee_id is not None:
        employee = service.get_employee(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")

    validated, error = service.process_employee_form(form_data, photo)
    if error:
        action = f"/add" if employee_id is None else f"/edit/{employee_id}"
        return render_form_error(request, error, employee=employee, action=action)

    if validated is None:
        action = f"/add" if employee_id is None else f"/edit/{employee_id}"
        return render_form_error(request, "Неизвестная ошибка валидации", employee=employee, action=action)

    if employee_id is not None and employee and photo and photo.filename:
        delete_photo(employee.photo)

    if employee_id is None:
        service.create_employee(validated)
    else:
        updated = service.update_employee(employee_id, validated)
        if not updated:
            return render_form_error(request, "Не удалось обновить сотрудника", employee=employee, action=f"/edit/{employee_id}")

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)