import os
from app.config import settings

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/static/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_PHOTO_SIZE_BYTES = settings.MAX_PHOTO_SIZE_KB * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

GENDER_CHOICES = ("M", "F")
DATE_FORMAT = "%Y-%m-%d"

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
