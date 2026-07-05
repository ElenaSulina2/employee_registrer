from fastapi import Request
from app.template_engine import templates
from app.config import settings


def render_add_edit_page(request: Request, employee=None, action: str = "/add"):
    return templates.TemplateResponse(
        request,
        "add_edit.html",
        {
            "employee": employee,
            "action": action,
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB,
        }
    )


def render_form_error(request: Request, error: str, employee=None, action: str = "/add"):
    return templates.TemplateResponse(
        request,
        "add_edit.html",
        {
            "employee": employee,
            "action": action,
            "error": error,
            "MAX_PHOTO_SIZE_KB": settings.MAX_PHOTO_SIZE_KB,
        }
    )