import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.utils.constants import UPLOAD_DIR

# Переопределяем папку для загрузок
TEST_UPLOAD_DIR = tempfile.mkdtemp()
os.environ["UPLOAD_DIR"] = TEST_UPLOAD_DIR

# Тестовая БД
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_uploads():
    for filename in os.listdir(TEST_UPLOAD_DIR):
        file_path = os.path.join(TEST_UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    yield
    for filename in os.listdir(TEST_UPLOAD_DIR):
        file_path = os.path.join(TEST_UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
