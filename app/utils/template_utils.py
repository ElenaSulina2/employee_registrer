from fastapi import Request
from app.template_engine import templates
from app.config import settings


def render_form_error(
    request: Request,
    error: str,
    employee=None,
    action: str = "/add",
    max_photo_size_kb: int = settings.MAX_PHOTO_SIZE_KB,
):
    """Возвращает TemplateResponse со страницей добавления/редактирования и сообщением об ошибке."""
    return templates.TemplateResponse(
        request,
        "add_edit.html",
        {
            "employee": employee,
            "action": action,
            "error": error,
            "MAX_PHOTO_SIZE_KB": max_photo_size_kb,
        },
    )
