import os
import sys
import urllib.parse
from fastapi.testclient import TestClient

# Ensure repository root is on sys.path so `src.app` can be imported when tests
# are executed from the test runner.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_and_remove():
    activity = "Chess Club"
    email = "testuser+signup@example.com"
    encoded_activity = urllib.parse.quote(activity, safe="")

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up (should succeed)
    resp = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]

    # Duplicate signup should be rejected
    resp2 = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert resp2.status_code == 400

    # Remove participant (should succeed)
    resp3 = client.delete(f"/activities/{encoded_activity}/participants/{urllib.parse.quote(email, safe='')}")
    assert resp3.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_participant():
    activity = "Chess Club"
    email = "definitely-not-registered@example.com"
    encoded_activity = urllib.parse.quote(activity, safe="")
    resp = client.delete(f"/activities/{encoded_activity}/participants/{urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 404
