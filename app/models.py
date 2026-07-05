from sqlalchemy import Column, Integer, String, Date, CHAR
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(CHAR(1), nullable=False)
    phone = Column(String(20), nullable=True)
    photo = Column(String(255), nullable=True)
