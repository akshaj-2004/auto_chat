import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "date_of_birth": "1990-01-01",
            "address": "123 Test St"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_user_duplicate_email():
    response = client.post(
        "/users/",
        json={
            "full_name": "Test User 2",
            "email": "test@example.com",
            "phone": "0987654321",
            "date_of_birth": "1992-02-02"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_list_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_user():
    # First create a user to get
    create_response = client.post(
        "/users/",
        json={
            "full_name": "Get User",
            "email": "get@example.com",
            "phone": "1112223333",
            "date_of_birth": "1980-01-01"
        },
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_update_user():
    # First create a user to update
    create_response = client.post(
        "/users/",
        json={
            "full_name": "Update User",
            "email": "update@example.com",
            "phone": "4445556666",
            "date_of_birth": "1985-05-05"
        },
    )
    user_id = create_response.json()["id"]

    response = client.put(
        f"/users/{user_id}",
        json={
            "full_name": "Updated Name",
            "email": "updated@example.com"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"

def test_delete_user():
    # First create a user to delete
    create_response = client.post(
        "/users/",
        json={
            "full_name": "Delete User",
            "email": "delete@example.com",
            "phone": "7778889999",
            "date_of_birth": "2000-10-10"
        },
    )
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully"

    # Verify user is gone
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

from unittest.mock import MagicMock, patch

def test_chat_endpoint():
    # Mock the agent to avoid calling Ollama
    with patch("app.routes.chat.create_agent_with_tools") as mock_create_agent:
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                MagicMock(content="Hello! How can I help you?", tool_calls=None)
            ]
        }
        mock_create_agent.return_value = mock_agent

        response = client.post(
            "/chat/test_session",
            json={"message": "Hello"}
        )
        assert response.status_code == 200
        assert response.json()["reply"] == "Hello! How can I help you?"
