"""Tests for the search page."""

from app import db


def add_sounds(user_id):
    """Add a few sounds for ben and one for another user."""
    db.sounds.insert_many(
        [
            {
                "user_id": user_id,
                "name": "Glass tap",
                "material": "glass",
                "instrument": {"type": "bell"},
            },
            {
                "user_id": user_id,
                "name": "Desk knock",
                "material": "wood",
                "instrument": {"type": "drum"},
            },
            {
                "user_id": "someone else",
                "name": "Glass smash",
                "material": "glass",
                "instrument": {"type": "bell"},
            },
        ]
    )


def test_search_by_name(client, user_id):
    """Searching part of a name finds the sound."""
    add_sounds(user_id)
    response = client.get("/search?q=knock")
    assert b"Desk knock" in response.data
    assert b"Glass tap" not in response.data


def test_search_by_material_any_case(client, user_id):
    """Searching a material works no matter the capitals."""
    add_sounds(user_id)
    response = client.get("/search?q=GLASS")
    assert b"Glass tap" in response.data
    assert b"Glass smash" not in response.data


def test_search_by_instrument(client, user_id):
    """The instrument filter only shows that instrument."""
    add_sounds(user_id)
    response = client.get("/search?instrument=drum")
    assert b"Desk knock" in response.data
    assert b"Glass tap" not in response.data


def test_search_no_results(client, user_id):
    """A search that matches nothing shows a message."""
    add_sounds(user_id)
    response = client.get("/search?q=banana")
    assert b"No sounds match" in response.data


def test_search_needs_login(client):
    """Logged out users get sent to the login page."""
    client.get("/logout")
    response = client.get("/search?q=glass")
    assert response.status_code == 302
