import os
import tempfile
from datetime import date

import pytest
from fastapi import status

from app.models import Employee
from app.utils.constants import UPLOAD_DIR


def test_index_empty(client):
    """Главная страница без сотрудников."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Реестр сотрудников" in response.text
    assert "Всего: 0" in response.text


def test_create_employee(client, db_session):
    """Создание сотрудника через POST /add."""
    data = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "birth_date": "1990-01-01",
        "gender": "M",
        "phone": "+7 (999) 123-45-67",
    }
    response = client.post("/add", data=data, files={}, follow_redirects=False)
    assert response.status_code == 303, f"Ошибка: {response.text}"
    assert response.headers["location"] == "/"

    # Проверяем запись в БД
    employee = db_session.query(Employee).filter_by(last_name="Иванов").first()
    assert employee is not None
    assert employee.first_name == "Иван"
    assert employee.middle_name == "Иванович"
    assert employee.birth_date == date(1990, 1, 1)
    assert employee.gender == "M"
    assert employee.phone == "+7 (999) 123-45-67"
    assert employee.photo is None


def test_list_employees_with_filters(client, db_session):
    """Фильтрация по поиску, полу и возрасту."""

    employees = [
        {
            "last_name": "Смирнов",
            "first_name": "Алексей",
            "birth_date": "1985-05-10",
            "gender": "M",
        },
        {
            "last_name": "Кузнецова",
            "first_name": "Ольга",
            "birth_date": "1995-08-20",
            "gender": "F",
        },
        {
            "last_name": "Иванов",
            "first_name": "Сергей",
            "birth_date": "2000-12-01",
            "gender": "M",
        },
    ]
    for emp in employees:
        client.post("/add", data=emp, files={})

    # Поиск по фамилии
    response = client.get("/?search=Иванов")
    assert response.status_code == 200
    assert "Сергей" in response.text
    assert "Алексей" not in response.text
    assert "Ольга" not in response.text

    # Фильтр по полу (мужчины)
    response = client.get("/?gender_male=true")
    assert "Алексей" in response.text
    assert "Сергей" in response.text
    assert "Ольга" not in response.text

    response = client.get("/?age_from=30&age_to=35")
    assert "Кузнецова" in response.text
    assert "Смирнов" not in response.text
    assert "Иванов" not in response.text


def test_edit_employee(client, db_session):
    """Редактирование сотрудника."""

    data = {
        "last_name": "Тестов",
        "first_name": "Тест",
        "birth_date": "1990-01-01",
        "gender": "M",
    }
    client.post("/add", data=data, files={})
    employee = db_session.query(Employee).filter_by(last_name="Тестов").first()
    emp_id = employee.id

    response = client.get(f"/edit/{emp_id}")
    assert response.status_code == 200
    assert "Редактировать" in response.text
    assert "Тестов" in response.text

    update_data = {
        "last_name": "Тестов",
        "first_name": "Тест",
        "middle_name": "Тестович",
        "birth_date": "1985-05-10",
        "gender": "M",
        "phone": "+7 (999) 111-22-33",
    }
    response = client.post(
        f"/edit/{emp_id}", data=update_data, files={}, follow_redirects=False
    )
    assert response.status_code == 303, f"Ошибка: {response.text}"
    assert response.headers["location"] == "/"

    db_session.refresh(employee)
    assert employee.middle_name == "Тестович"
    assert employee.birth_date == date(1985, 5, 10)
    assert employee.phone == "+7 (999) 111-22-33"


def test_delete_employee(client, db_session):
    """Удаление сотрудника."""
    data = {
        "last_name": "Удаляев",
        "first_name": "Удаляй",
        "birth_date": "2000-01-01",
        "gender": "M",
    }
    client.post("/add", data=data, files={})
    employee = db_session.query(Employee).filter_by(last_name="Удаляев").first()
    emp_id = employee.id

    response = client.post(f"/delete/{emp_id}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

    deleted = db_session.query(Employee).filter_by(id=emp_id).first()
    assert deleted is None


def test_edit_nonexistent_employee(client):
    """Редактирование/удаление несуществующего сотрудника."""
    response = client.get("/edit/99999")
    assert response.status_code == 404
    assert "не найден" in response.text

    response = client.post(
        "/edit/99999",
        data={
            "last_name": "test",
            "first_name": "test",
            "birth_date": "1990-01-01",
            "gender": "M",
        },
        files={},
    )
    assert response.status_code == 404
    assert "не найден" in response.text

    response = client.post("/delete/99999")
    assert response.status_code == 404


def test_pagination(client, db_session):
    """Проверка пагинации и изменения размера страницы."""

    for i in range(25):
        data = {
            "last_name": f"Фамилия{i}",
            "first_name": f"Имя{i}",
            "birth_date": "1990-01-01",
            "gender": "M" if i % 2 == 0 else "F",
        }
        client.post("/add", data=data, files={})

    response = client.get("/")
    assert response.status_code == 200

    for i in range(10):
        assert f"Фамилия{i}" in response.text
    assert "Фамилия10" not in response.text
    assert "Всего: 25" in response.text

    assert "page=2" in response.text
    assert "page=3" in response.text

    response = client.get("/?page=2")
    assert response.status_code == 200
    for i in range(10, 20):
        assert f"Фамилия{i}" in response.text
    assert "Фамилия0" not in response.text
    assert "Фамилия20" not in response.text

    response = client.get("/?page=3")
    assert response.status_code == 200
    for i in range(20, 25):
        assert f"Фамилия{i}" in response.text
    assert "Фамилия0" not in response.text

    response = client.get("/?size=5")
    assert response.status_code == 200
    for i in range(5):
        assert f"Фамилия{i}" in response.text
    assert "Фамилия5" not in response.text
    assert "Всего: 25" in response.text
    assert "page=5" in response.text

    response = client.get("/?search=Фамилия1&size=5")
    assert response.status_code == 200

    assert "Фамилия1" in response.text
    assert "Фамилия10" in response.text
    assert "Фамилия11" in response.text
    assert "Фамилия12" in response.text
    assert "Фамилия13" in response.text
    assert "Фамилия14" not in response.text
    assert "Всего: 11" in response.text
    assert "page=3" in response.text
