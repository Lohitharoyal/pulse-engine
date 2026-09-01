import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_skilltrack.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clear_skills():
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM skills"))
    yield


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_and_list_skills():
    response = client.post(
        "/skills",
        json={
            "name": "Docker",
            "category": "DevOps",
            "current_level": 2,
            "target_level": 6,
            "last_practiced_date": "2026-09-01",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Docker"
    assert data["progress_percentage"] == 33

    list_response = client.get("/skills")
    assert list_response.status_code == 200
    assert any(item["name"] == "Docker" for item in list_response.json())


def test_update_skill_progress():
    create_response = client.post(
        "/skills",
        json={
            "name": "Git",
            "category": "Version Control",
            "current_level": 1,
            "target_level": 5,
            "last_practiced_date": "2026-08-30",
        },
    )
    skill_id = create_response.json()["id"]

    response = client.patch(
        f"/skills/{skill_id}/progress",
        json={
            "current_level": 3,
            "target_level": 5,
            "last_practiced_date": "2026-09-02",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["current_level"] == 3
    assert data["progress_percentage"] == 60
    assert data["last_practiced_date"] == "2026-09-02"


def test_next_practice_recommendation_works():
    client.post(
        "/skills",
        json={
            "name": "JavaScript",
            "category": "Frontend",
            "current_level": 1,
            "target_level": 5,
            "last_practiced_date": "2026-08-20",
        },
    )
    client.post(
        "/skills",
        json={
            "name": "SQL",
            "category": "Database",
            "current_level": 3,
            "target_level": 5,
            "last_practiced_date": "2026-09-01",
        },
    )

    response = client.get("/skills/recommendation")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["name"]
    assert "progress" in payload["reason"].lower()
