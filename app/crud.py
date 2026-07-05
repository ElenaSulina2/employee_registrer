from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta

from app.models import Employee
from app import schemas


def _apply_filters(
    query,
    search: str = "",
    gender: list[str] = None,
    age_from: int = None,
    age_to: int = None,
):
    """Применяет фильтры к запросу (общая логика)."""
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Employee.last_name.ilike(pattern),
                Employee.first_name.ilike(pattern),
                Employee.middle_name.ilike(pattern),
            )
        )
    if gender:
        query = query.filter(Employee.gender.in_(gender))

    today = date.today()
    if age_from is not None:
        max_birth = date(today.year - age_from, today.month, today.day)
        query = query.filter(Employee.birth_date <= max_birth)
    if age_to is not None:
        min_birth = date(today.year - age_to - 1, today.month, today.day) + timedelta(
            days=1
        )
        query = query.filter(Employee.birth_date >= min_birth)
    return query


def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = "",
    gender: list[str] = None,
    age_from: int = None,
    age_to: int = None,
):
    query = db.query(Employee)
    query = _apply_filters(query, search, gender, age_from, age_to)
    return query.offset(skip).limit(limit).all()


def count_employees(
    db: Session,
    search: str = "",
    gender: list[str] = None,
    age_from: int = None,
    age_to: int = None,
):
    query = db.query(Employee)
    query = _apply_filters(query, search, gender, age_from, age_to)
    return query.count()


def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session, employee_id: int, employee_data: schemas.EmployeeUpdate
):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        for key, value in employee_data.model_dump(exclude_unset=True).items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False
