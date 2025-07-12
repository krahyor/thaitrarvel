import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from sqlmodel import SQLModel

from thaitravel.models import get_session
from thaitravel.main import app

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from .test_base import client, session, prepare_database, create_async_engine
from thaitravel.core import config

settings = config.get_settings()


@pytest.fixture
def user_data():
    return {
        "email": "admin@email.local",
        "username": "admin",
        "first_name": "Firstname",
        "last_name": "Lastname",
        "province": "Bangkok",
        "password": "password",
    }


@pytest.mark.asyncio
async def test_user_crud_flow(client, user_data):
    response = await client.post("/v1/users/create", json=user_data)

    assert response.status_code == 200  # หรือ 201 ถ้า API ระบุไว้

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["province"] == user_data["province"]
    assert "id" in data


@pytest.mark.asyncio
async def test_user_token_and_auth_flow(client, user_data):
    # Create user
    create_response = await client.post("/v1/users/create", json=user_data)
    user_id = create_response.json()

    # Get token
    form_data = {
        "grant_type": "password",
        "username": user_data["username"],
        "password": user_data["password"],
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    token_response = await client.post(
        "/v1/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert token_response.status_code == 200, f"Token failed: {token_response.text}"
    tokens = token_response.json()
    access_token = tokens["access_token"]

    # Use access_token to call a protected route
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await client.get("/v1/users/me", headers=headers)

    assert me_response.status_code == 200
