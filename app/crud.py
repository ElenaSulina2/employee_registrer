from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta
from app import models, schemas

def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = "",
    gender: list[str] = None,
    age_from: int = None,
    age_to: int = None,
):
    query = db.query(models.Employee)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Employee.last_name.ilike(pattern),
                models.Employee.first_name.ilike(pattern),
                models.Employee.middle_name.ilike(pattern),
            )
        )
    if gender:
        query = query.filter(models.Employee.gender.in_(gender))
    today = date.today()
    if age_from is not None:
        max_birth = date(today.year - age_from, today.month, today.day)
        query = query.filter(models.Employee.birth_date <= max_birth)
    if age_to is not None:
        min_birth = date(today.year - age_to - 1, today.month, today.day) + timedelta(days=1)
        query = query.filter(models.Employee.birth_date >= min_birth)
    return query.offset(skip).limit(limit).all()

def count_employees(db: Session, search: str = "", gender: list[str] = None, age_from: int = None, age_to: int = None):
    query = db.query(models.Employee)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Employee.last_name.ilike(pattern),
                models.Employee.first_name.ilike(pattern),
                models.Employee.middle_name.ilike(pattern),
            )
        )
    if gender:
        query = query.filter(models.Employee.gender.in_(gender))
    today = date.today()
    if age_from is not None:
        max_birth = date(today.year - age_from, today.month, today.day)
        query = query.filter(models.Employee.birth_date <= max_birth)
    if age_to is not None:
        min_birth = date(today.year - age_to - 1, today.month, today.day) + timedelta(days=1)
        query = query.filter(models.Employee.birth_date >= min_birth)
    return query.count()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee_data: schemas.EmployeeUpdate):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        for key, value in employee_data.dict(exclude_unset=True).items():
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