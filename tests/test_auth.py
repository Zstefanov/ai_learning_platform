import sqlite3
import pytest
import uuid
import logging

logger = logging.getLogger(__name__)

# Test for user registration, login, and deletion using FastAPI and SQLite

@pytest.mark.asyncio
async def test_register_login_delete_user(async_client, db_path):
    unique_id = uuid.uuid4().hex[:6]
    email = f"testuser_{unique_id}@example.com"
    payload = {
        "username": f"testuser_{unique_id}",
        "email": email,
        "password": "testpass123"
    }

    # Register
    response = await async_client.post("/api/register", json=payload)
    print(f"Register response status: {response.status_code}")
    print(f"Register response content: {await response.aread()}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    msg = f"User created with email: {email}"
    logger.info(msg)
    print(msg)

    # Login
    login_payload = {
        "email": email,
        "password": "testpass123"
    }
    response = await async_client.post("/api/login", json=login_payload)
    print(f"Login response status: {response.status_code}")
    print(f"Login response content: {await response.aread()}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    msg = f"User logged in with email: {email}"
    logger.info(msg)
    print(msg)

    # Delete Account
    response = await async_client.request(
        "DELETE",
        "/api/delete-account",
        json=login_payload
    )
    print(f"Delete response status: {response.status_code}")
    print(f"Delete response content: {await response.aread()}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    msg = f"User deleted with email: {email}"
    logger.info(msg)
    print(msg)

    # Ensure user is gone
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user_exists = cursor.fetchone()
    conn.close()
    assert user_exists is None
    msg = f"Verified user removal from database for email: {email}"
    logger.info(msg)
    print(msg)
