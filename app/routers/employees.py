from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query, UploadFile, File, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas
from app.config import settings
from app.utils.constants import MAX_PHOTO_SIZE_BYTES, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.utils.helpers import calculate_age, save_uploaded_photo, delete_photo
from app.utils.validators import validate_and_parse_employee_data

router = APIRouter()
templates = Jinja2Templates(directory="./app/templates")


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    search: str = Query("", alias="search"),
    gender_male: bool = Query(False),
    gender_female: bool = Query(False),
    age_from: Optional[str] = Query(None, alias="age_from"),
    age_to: Optional[str] = Query(None, alias="age_to"),
    page: int = Query(DEFAULT_PAGE, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db)
):
    # Преобразование строк в целые числа
    age_from_int = None
    age_to_int = None
    if age_from is not None and age_from.strip():
        try:
            age_from_int = int(age_from)
        except ValueError:
            pass
    if age_to is not None and age_to.strip():
        try:
            age_to_int = int(age_to)
        except ValueError:
            pass

    # Фильтр по полу
    gender = []
    if gender_male:
        gender.append("M")
    if gender_female:
        gender.append("F")
    if not gender:
        gender = None

    skip = (page - 1) * size
    employees = crud.get_employees(
        db,
        skip=skip,
        limit=size,
        search=search,
        gender=gender,
        age_from=age_from_int,
        age_to=age_to_int
    )
    total = crud.count_employees(
        db,
        search=search,
        gender=gender,
        age_from=age_from_int,
        age_to=age_to_int
    )
    total_pages = (total + size - 1) // size

    employees_with_age = []
    for emp in employees:
        employees_with_age.append({
            "id": emp.id,
            "last_name": emp.last_name,
            "first_name": emp.first_name,
            "middle_name": emp.middle_name or "",  # защита от None
            "birth_date": emp.birth_date,
            "gender": emp.gender,
            "phone": emp.phone or "",              # защита от None
            "photo": emp.photo,
            "age": calculate_age(emp.birth_date)
        })

    return templates.TemplateResponse(
        request, "index.html",
        {
            "employees": employees_with_age,
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages,
            "search": search,
            "gender_male": gender_male,
            "gender_female": gender_female,
            "age_from": age_from,
            "age_to": age_to,
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB
        }
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
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB
        }
    )


@router.post("/add")
def add_employee(
    request: Request,
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: str = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    error = None
    try:
        validated = validate_and_parse_employee_data(
            last_name, first_name, birth_date, gender, middle_name, phone
        )
    except ValueError as e:
        error = str(e)

    # Приводим необязательные строки к пустой строке (вместо None)
    if not error:
        validated["middle_name"] = validated.get("middle_name") or ""
        validated["phone"] = validated.get("phone") or ""

    photo_filename = None
    if photo and photo.filename and not error:
        filename, err = save_uploaded_photo(photo, MAX_PHOTO_SIZE_BYTES)
        if err:
            error = err
        else:
            photo_filename = filename

    if error:
        return templates.TemplateResponse(
            "add_edit.html",
            {
                "employee": None,
                "action": "/add",
                "error": error,
                "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB
            }
        )

    employee_data = schemas.EmployeeCreate(
        last_name=validated["last_name"],
        first_name=validated["first_name"],
        middle_name=validated["middle_name"],
        birth_date=validated["birth_date"],
        gender=validated["gender"],
        phone=validated["phone"],
        photo=photo_filename
    )
    crud.create_employee(db, employee_data)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit/{employee_id}", response_class=HTMLResponse)
def edit_form(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return templates.TemplateResponse(
        request,
        "add_edit.html",
        {
            "employee": employee,
            "action": f"/edit/{employee_id}",
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB
        }
    )


@router.post("/edit/{employee_id}")
def edit_employee(
    request: Request,
    employee_id: int,
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: str = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    error = None
    try:
        validated = validate_and_parse_employee_data(
            last_name, first_name, birth_date, gender, middle_name, phone
        )
    except ValueError as e:
        error = str(e)

    # Приводим необязательные строки к пустой строке
    if not error:
        validated["middle_name"] = validated.get("middle_name") or ""
        validated["phone"] = validated.get("phone") or ""

    new_photo = employee.photo
    if photo and photo.filename and not error:
        filename, err = save_uploaded_photo(photo, MAX_PHOTO_SIZE_BYTES)
        if err:
            error = err
        else:
            delete_photo(employee.photo)
            new_photo = filename

    if error:
        return templates.TemplateResponse(
            request,
            "add_edit.html",
            {
                "employee": employee,
                "action": f"/edit/{employee_id}",
                "error": error,
                "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB
            }
        )

    employee_data = schemas.EmployeeUpdate(
        last_name=validated["last_name"],
        first_name=validated["first_name"],
        middle_name=validated["middle_name"],
        birth_date=validated["birth_date"],
        gender=validated["gender"],
        phone=validated["phone"],
        photo=new_photo
    )
    crud.update_employee(db, employee_id, employee_data)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if employee:
        delete_photo(employee.photo)
    deleted = crud.delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)