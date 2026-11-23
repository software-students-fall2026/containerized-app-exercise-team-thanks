"""Tests for the home page."""

from app import app, db


def test_home_needs_login():
    """Logged out users get sent to the login page."""
    response = app.test_client().get("/home")
    assert response.status_code == 302


def test_home_no_sounds(client):
    """With no sounds the page shows the empty message."""
    response = client.get("/home")
    assert b"Welcome ben!" in response.data
    assert b"recorded any sounds yet" in response.data


def test_home_shows_my_sounds(client, user_id):
    """Only the logged in user's sounds show up."""
    db.sounds.insert_one(
        {"user_id": user_id, "name": "Glass tap", "instrument": {"type": "bell"}}
    )
    db.sounds.insert_one({"user_id": "someone else", "name": "Not mine"})

    response = client.get("/home")
    assert b"Glass tap" in response.data
    assert b"bell" in response.data
    assert b"Not mine" not in response.data


def test_home_sound_not_analyzed(client, user_id):
    """A sound with no instrument yet still shows up."""
    db.sounds.insert_one({"user_id": user_id, "name": "New clip"})

    response = client.get("/home")
    assert b"New clip" in response.data
    assert b"not generated yet" in response.data


def test_sound_detail(client, user_id):
    """A user can open the page for one of their sounds."""
    sound_id = db.sounds.insert_one(
        {"user_id": user_id, "name": "Glass tap", "material": "glass"}
    ).inserted_id

    response = client.get(f"/sounds/{sound_id}")
    assert response.status_code == 200
    assert b"Glass tap" in response.data
    assert b"glass" in response.data


def test_sound_detail_bad_id(client):
    """A made up id gives a 404."""
    response = client.get("/sounds/not-a-real-id")
    assert response.status_code == 404


def test_sound_detail_someone_elses(client):
    """Users can't see other users' sounds."""
    sound_id = db.sounds.insert_one(
        {"user_id": "someone else", "name": "Not mine"}
    ).inserted_id

    response = client.get(f"/sounds/{sound_id}")
    assert response.status_code == 404
