import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_from_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "No such activity"
    email = "student@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@student.edu"
    url = f"/activities/{quote(activity_name)}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
