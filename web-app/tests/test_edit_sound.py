"""Tests for editing sounds."""

from bson.objectid import ObjectId
from app import app, db


def test_edit_sound_needs_login():
    """Logged out users cannot edit sounds."""
    response = app.test_client().get(f"/sounds/{ObjectId()}/edit")
    assert response.status_code == 302


def test_edit_sound_form(client, user_id):
    """The edit form displays existing sound information."""
    sound_id = db.sounds.insert_one(
        {
            "user_id": user_id,
            "name": "Glass tap",
            "material": "glass",
            "instrument": {"type": "bell"},
        }
    ).inserted_id

    response = client.get(f"/sounds/{sound_id}/edit")

    assert response.status_code == 200
    assert b"Glass tap" in response.data
    assert b"glass" in response.data
    assert b"bell" in response.data


def test_edit_sound_update(client, user_id):
    """Users can update their own sounds."""
    sound_id = db.sounds.insert_one(
        {
            "user_id": user_id,
            "name": "Glass tap",
            "material": "glass",
            "instrument": {"type": "bell"},
            "analysis": {"note": "A5", "tags": []},
        }
    ).inserted_id

    response = client.post(
        f"/sounds/{sound_id}/edit",
        data={
            "name": "Desk knock",
            "material": "wood",
            "instrument": "drum",
        },
    )

    assert response.status_code == 302

    sound = db.sounds.find_one({"_id": sound_id})

    assert sound["name"] == "Desk knock"
    assert sound["material"] == "wood"
    assert sound["instrument"]["type"] == "drum"
    assert sound["analysis"]["note"] == "A5"
    assert sound["user_id"] == user_id


def test_edit_sound_empty_fields(client, user_id):
    """Empty fields are rejected without changing the sound."""
    sound_id = db.sounds.insert_one(
        {"user_id": user_id, "name": "Glass tap"}
    ).inserted_id

    response = client.post(
        f"/sounds/{sound_id}/edit",
        data={"name": "", "material": "", "instrument": ""},
    )

    assert response.status_code == 400
    assert b"All fields are required." in response.data

    sound = db.sounds.find_one({"_id": sound_id})
    assert sound["name"] == "Glass tap"


def test_edit_sound_bad_id(client):
    """Invalid sound IDs return a 404."""
    response = client.get("/sounds/not-a-real-id/edit")
    assert response.status_code == 404


def test_edit_sound_missing(client):
    """Nonexistent sounds return a 404."""
    response = client.get(f"/sounds/{ObjectId()}/edit")
    assert response.status_code == 404


def test_edit_sound_someone_elses(client):
    """Users cannot view or update another user's sound."""
    sound_id = db.sounds.insert_one(
        {"user_id": "someone else", "name": "Not mine"}
    ).inserted_id

    response = client.get(f"/sounds/{sound_id}/edit")
    assert response.status_code == 404

    response = client.post(
        f"/sounds/{sound_id}/edit",
        data={
            "name": "Changed",
            "material": "wood",
            "instrument": "drum",
        },
    )

    assert response.status_code == 404

    sound = db.sounds.find_one({"_id": sound_id})
    assert sound["name"] == "Not mine"