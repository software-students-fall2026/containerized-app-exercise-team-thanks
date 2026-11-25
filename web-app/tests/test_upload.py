"""tests for uploading files"""

from io import BytesIO
from app import app, db

def test_upload_needs_login():
    """tests if you need login to upload files"""

    response = app.test_client().post(
        "/sounds/add",
        data = {
            "name": "tap glass"
        }
    )

    assert response.status_code == 302

def test_upload_sound(client):
    """tests uploading an audio file"""

    response = client.post(
        "/sounds/add",
        data={
            "name": "tap glass",
            "aduio_file": (BytesIO(b"fake audio"), "tap.wav", "audio/wav")
        },
        follow_redirects=False
    )

    assert response.status_code == 302