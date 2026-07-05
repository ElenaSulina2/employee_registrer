from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import employees
from app.template_engine import templates


app = FastAPI( title="Реестр сотрудников")

app.include_router(employees.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.templates = templates