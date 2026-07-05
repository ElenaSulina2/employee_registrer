from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    UploadFile,
    File,
    status,
    Form,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EmployeeFormData, EmployeeSearchParams, IndexPageContext
from app.config import settings
from app.template_engine import templates
from app.services.employee_service import EmployeeService
from app.utils.template_utils import render_form_error

router = APIRouter()


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(db)


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    params: EmployeeSearchParams = Depends(),
    service: EmployeeService = Depends(get_employee_service),
):
    employees, total, total_pages = service.get_employees_with_filters(params)
    context = IndexPageContext.from_employees(
        employees=employees,
        total=total,
        params=params,
        max_photo_size_kb=settings.MAX_PHOTO_SIZE_KB,
    )
    return templates.TemplateResponse(
        request,
        "index.html",
        context.to_template_dict(),
    )


@router.get("/add", response_class=HTMLResponse)
def add_form(request: Request):
    return templates.TemplateResponse(
        request,
        "add_edit.html",
        {
            "request": request,
            "employee": None,
            "action": "/add",
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB,
        },
    )


@router.post("/add")
def add_employee(
    request: Request,
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: Optional[str] = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    photo: UploadFile = File(None),
    service: EmployeeService = Depends(get_employee_service),
):
    form_data = EmployeeFormData(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone=phone,
    )
    validated, error = service.process_employee_form(form_data, photo)
    if error:
        return render_form_error(request, error, action="/add")
    service.create_employee(validated)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit/{employee_id}", response_class=HTMLResponse)
def edit_form(
    request: Request,
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    employee = service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return templates.TemplateResponse(
        request,
        "add_edit.html",
        {
            "employee": employee,
            "action": f"/edit/{employee_id}",
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB,
        },
    )


@router.post("/edit/{employee_id}")
def edit_employee(
    request: Request,
    employee_id: int,
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: Optional[str] = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    photo: UploadFile = File(None),
    service: EmployeeService = Depends(get_employee_service),
):
    employee = service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    form_data = EmployeeFormData(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone=phone,
    )
    validated, error = service.process_employee_form(form_data)
    if error:
        return render_form_error(
            request, error, employee=employee, action=f"/edit/{employee_id}"
        )

    updated_employee, error = service.update_employee_with_photo(
        employee_id, validated, photo
    )
    if error:
        return render_form_error(
            request, error, employee=employee, action=f"/edit/{employee_id}"
        )

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete/{employee_id}")
def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    deleted = service.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
