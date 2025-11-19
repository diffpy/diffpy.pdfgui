"""Pytest configuration and fixtures."""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.services.auth_service import AuthService

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Test data directory (uses original pdfGUI test data)
ORIGINAL_TESTDATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "tests", "testdata"
)


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session for each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        email="test@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def testdata_file():
    """Get path to original pdfGUI test data file."""
    def _get_file(filename):
        return os.path.join(ORIGINAL_TESTDATA_DIR, filename)
    return _get_file
