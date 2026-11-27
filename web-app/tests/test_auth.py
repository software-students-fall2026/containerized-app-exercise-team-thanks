"""tests for authorization"""

from app import db
from bson import ObjectId
from werkzeug.security import generate_password_hash

def test_login_page(client):
    """test if GET of /login loads the login page"""
    response = client.get("/login")
    assert response.status_code == 200

def test_signup_page(client):
    """test if GET of /signup loads the login page"""
    response = client.get("/signup")
    assert response.status_code == 200

def test_signup(client):
    """test if signup properly signs up people to the web app"""
    response = client.post(
        "/signup",
        data = {
            "username": "test_user",
            "email": "test123@gmail.com",
            "password": "password123456"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert db.users.find_one({"email": "test123@gmail.com"}) is not None

def test_login(client):
    """test if login properly logs in users to the web app"""  
    user_id = ObjectId()
    db.users.insert_one({
        "_id": user_id,
        "username": "robert",
        "email": "robert123@gmail.com",
        "password_hash": generate_password_hash("password123")
    })

    response = client.post(
        "/login", 
        data = {
        "username": "Robert",
        "password": "password123"
    })

    assert response.status_code == 302

def test_wrong_password(client):
    """test if wrong password returns an error"""

    user_id = ObjectId()

    db.users.insert_one({
        "_id": user_id,
        "username": "robert",
        "email": "robert123@gmail.com",
        "password_hash": generate_password_hash("password123")
    })

    response = client.post(
        "/login", 
        data = {
            "username": "Robert",
            "password": "wrong"
        }
    )

    assert response.status_code == 200

