import pytest
from fastapi import HTTPException, UploadFile
from fastapi.datastructures import UploadFile as FastAPIUploadFile
from unittest.mock import MagicMock, patch
from io import BytesIO

from app.schemas import EmployeeFormData
from app.services.form_handlers import get_employee_form, handle_employee_form
from app.services.employee_service import EmployeeService


def test_get_employee_form():
    form_data = get_employee_form(
        last_name="Иванов",
        first_name="Иван",
        middle_name="Иванович",
        birth_date="1990-01-01",
        gender="M",
        phone="+7 (999) 123-45-67",
    )
    assert isinstance(form_data, EmployeeFormData)
    assert form_data.last_name == "Иванов"
    assert form_data.first_name == "Иван"
    assert form_data.middle_name == "Иванович"
    assert form_data.birth_date == "1990-01-01"
    assert form_data.gender == "M"
    assert form_data.phone == "+7 (999) 123-45-67"


@pytest.fixture
def mock_service():
    service = MagicMock(spec=EmployeeService)
    service.process_employee_form.return_value = ({"id": 1, "name": "test"}, None)
    service.create_employee.return_value = None
    service.update_employee_with_photo.return_value = (MagicMock(), None)
    service.get_employee.return_value = MagicMock()
    return service


@pytest.fixture
def mock_request():
    request = MagicMock()
    return request


def test_handle_employee_form_create_success(mock_request, mock_service):
    form_data = EmployeeFormData(
        last_name="Иванов",
        first_name="Иван",
        birth_date="1990-01-01",
        gender="M",
    )
    result = handle_employee_form(mock_request, form_data, None, mock_service)

    assert result.status_code == 303
    assert result.headers["location"] == "/"
    mock_service.create_employee.assert_called_once()
    mock_service.update_employee_with_photo.assert_not_called()


def test_handle_employee_form_update_success(mock_request, mock_service):
    form_data = EmployeeFormData(
        last_name="Иванов",
        first_name="Иван",
        birth_date="1990-01-01",
        gender="M",
    )
    employee_id = 1
    result = handle_employee_form(
        mock_request, form_data, None, mock_service, employee_id
    )

    assert result.status_code == 303
    assert result.headers["location"] == "/"
    mock_service.get_employee.assert_called_once_with(employee_id)
    mock_service.update_employee_with_photo.assert_called_once()
    mock_service.create_employee.assert_not_called()


def test_handle_employee_form_employee_not_found(mock_request, mock_service):
    mock_service.get_employee.return_value = None
    form_data = EmployeeFormData(
        last_name="Иванов",
        first_name="Иван",
        birth_date="1990-01-01",
        gender="M",
    )
    with pytest.raises(HTTPException) as exc_info:
        handle_employee_form(
            mock_request, form_data, None, mock_service, employee_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Сотрудник не найден"
    mock_service.create_employee.assert_not_called()
    mock_service.update_employee_with_photo.assert_not_called()


def test_handle_employee_form_unknown_error(mock_request, mock_service):
    mock_service.process_employee_form.return_value = (
        None,
        None,
    )  # validated = None, error = None
    form_data = EmployeeFormData(
        last_name="Иванов",
        first_name="Иван",
        birth_date="1990-01-01",
        gender="M",
    )
    with patch("app.services.form_handlers.render_form_error") as mock_render:
        mock_render.return_value = MagicMock(status_code=200)
        result = handle_employee_form(mock_request, form_data, None, mock_service)

        mock_render.assert_called_once_with(
            mock_request, "Неизвестная ошибка валидации", employee=None, action="/add"
        )
        mock_service.create_employee.assert_not_called()
