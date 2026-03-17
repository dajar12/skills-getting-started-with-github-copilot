import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture that provides a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities(monkeypatch):
    """Fixture that resets activities to a fresh copy for each test"""
    fresh_activities = deepcopy(activities)
    monkeypatch.setattr("src.app.activities", fresh_activities)
    return fresh_activities
