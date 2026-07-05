from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File, status
from fastapi.responses import RedirectResponse, HTMLResponse

from app.schemas import EmployeeSearchParams, IndexPageContext, EmployeeFormData
from app.config import settings
from app.template_engine import templates
from app.services.employee_service import EmployeeService
from app.dependencies import (
    get_employee_form,
    handle_employee_form,
    get_employee_service,
)
from app.utils.template_utils import render_add_edit_page

router = APIRouter()


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
    return render_add_edit_page(request, action="/add")


@router.post("/add")
def add_employee(
    request: Request,
    form_data: EmployeeFormData = Depends(get_employee_form),
    photo: UploadFile = File(None),
    service: EmployeeService = Depends(get_employee_service),
):
    return handle_employee_form(request, form_data, photo, service)


@router.get("/edit/{employee_id}", response_class=HTMLResponse)
def edit_form(
    request: Request,
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    employee = service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return render_add_edit_page(
        request, employee=employee, action=f"/edit/{employee_id}"
    )


@router.post("/edit/{employee_id}")
def edit_employee(
    request: Request,
    employee_id: int,
    form_data: EmployeeFormData = Depends(get_employee_form),
    photo: UploadFile = File(None),
    service: EmployeeService = Depends(get_employee_service),
):
    return handle_employee_form(request, form_data, photo, service, employee_id)


@router.post("/delete/{employee_id}")
def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    deleted = service.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
