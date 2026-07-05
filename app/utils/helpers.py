import os
import uuid
from datetime import date
from fastapi import UploadFile
from app.utils.constants import UPLOAD_DIR, ALLOWED_EXTENSIONS


def calculate_age(birth_date: date) -> int:
    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def save_uploaded_photo(photo: UploadFile, max_size_bytes: int):
    if not photo or not photo.filename:
        return None, None
    ext = os.path.splitext(photo.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None, "Неподдерживаемый формат. Разрешены: JPG, JPEG, PNG"
    content = photo.file.read()
    if len(content) > max_size_bytes:
        return None, f"Файл превышает {max_size_bytes // 1024} КБ"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return filename, None


def delete_photo(filename: str | None):
    if filename:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
