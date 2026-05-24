import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)
initial_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert isinstance(response.json(), dict)


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_for_activity_already_signed_up_returns_400():
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_from_activity_success():
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": existing_email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from {activity_name}"}
    assert existing_email not in app_module.activities[activity_name]["participants"]


def test_unregister_from_activity_not_found_returns_404():
    activity_name = "Chess Club"
    missing_email = "missingstudent@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": missing_email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
