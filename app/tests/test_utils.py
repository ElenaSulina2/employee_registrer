import os
import pytest
from datetime import date
from io import BytesIO

from fastapi import UploadFile

from app.utils.validators import validate_gender, parse_date
from app.utils.helpers import calculate_age, save_uploaded_photo, delete_photo
from app.utils.constants import UPLOAD_DIR, MAX_PHOTO_SIZE_BYTES


def test_calculate_age():
    assert calculate_age(date(2000, 1, 1)) == 26  # до конца 2026 года


def test_validate_gender():
    assert validate_gender("M") == "M"
    with pytest.raises(ValueError):
        validate_gender("X")


def test_parse_date():
    assert parse_date("1990-01-01") == date(1990, 1, 1)
    with pytest.raises(ValueError):
        parse_date("01-01-1990")


def test_save_uploaded_photo_success():
    content = b"fake image content"
    file = UploadFile(filename="test.jpg", file=BytesIO(content))
    filename, error = save_uploaded_photo(file, MAX_PHOTO_SIZE_BYTES)
    assert error is None
    assert filename is not None
    file_path = os.path.join(UPLOAD_DIR, filename)
    assert os.path.exists(file_path)
    with open(file_path, "rb") as f:
        saved_content = f.read()
    assert saved_content == content


def test_save_uploaded_photo_invalid_extension():
    file = UploadFile(filename="test.txt", file=BytesIO(b"content"))
    filename, error = save_uploaded_photo(file, MAX_PHOTO_SIZE_BYTES)
    assert filename is None
    assert error == "Неподдерживаемый формат. Разрешены: JPG, JPEG, PNG"


def test_save_uploaded_photo_too_large():
    content = b"x" * (MAX_PHOTO_SIZE_BYTES + 1)
    file = UploadFile(filename="test.jpg", file=BytesIO(content))
    filename, error = save_uploaded_photo(file, MAX_PHOTO_SIZE_BYTES)
    assert filename is None
    assert "превышает" in error


def test_save_uploaded_photo_empty_file():
    file = UploadFile(filename="", file=BytesIO(b""))
    filename, error = save_uploaded_photo(file, MAX_PHOTO_SIZE_BYTES)
    assert filename is None
    assert error is None

    filename, error = save_uploaded_photo(None, MAX_PHOTO_SIZE_BYTES)
    assert filename is None
    assert error is None


def test_delete_photo_success():
    content = b"test delete"
    file = UploadFile(filename="test.jpg", file=BytesIO(content))
    filename, _ = save_uploaded_photo(file, MAX_PHOTO_SIZE_BYTES)
    file_path = os.path.join(UPLOAD_DIR, filename)
    assert os.path.exists(file_path)

    delete_photo(filename)
    assert not os.path.exists(file_path)


def test_delete_photo_none():
    delete_photo(None)


def test_delete_photo_not_exists():
    delete_photo("nonexistent.jpg")
