from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import employees
from app.database import engine


from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI( title="Реестр сотрудников")

app.include_router(employees.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.templates = templates