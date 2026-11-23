"""Fixtures shared by all the tests."""

import pytest
from app import app, db


@pytest.fixture(name="client")
def client_fixture():
    """Make a test client that is logged in as ben."""
    db.users.delete_many({})
    db.sounds.delete_many({})

    test_client = app.test_client()
    test_client.post(
        "/signup",
        data={"username": "ben", "email": "ben@test.com", "password": "password123"},
    )
    test_client.post("/login", data={"username": "ben", "password": "password123"})
    return test_client


@pytest.fixture(name="user_id")
def user_id_fixture(client):
    """Ben's id, the same way the app stores it on sounds."""
    assert client
    return str(db.users.find_one({"username": "ben"})["_id"])
