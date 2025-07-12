import pytest
import pytest_asyncio
from httpx import AsyncClient
from thaitravel.main import app
from thaitravel.core import config

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv
from .test_base import client, session, prepare_database, create_async_engine

settings = config.get_settings()


@pytest.fixture
def user_data():
    return {
        "email": "admin@email.local",
        "username": "admin",
        "first_name": "Admin",
        "last_name": "Test",
        "province": "Bangkok",
        "password": "password",
    }


@pytest.mark.asyncio
async def test_province_tax_crud_flow(client, user_data):
    create_user_resp = await client.post("/v1/users/create", json=user_data)
    assert create_user_resp.status_code in [200, 201]

    token_resp = await client.post(
        "/v1/token",
        data={
            "grant_type": "password",
            "username": user_data["username"],
            "password": user_data["password"],
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    base_data = {"province": "Chiang Mai", "tax": 7.5}
    base_resp = await client.post(
        "/v1/province_tax/base", json=base_data, headers=headers
    )
    assert base_resp.status_code == 201
    base = base_resp.json()
    assert base["province"] == "Chiang Mai"

    base_list_resp = await client.get("/v1/province_tax/base", headers=headers)
    assert base_list_resp.status_code == 200
    base_list = base_list_resp.json()
    assert any(b["province"] == "Chiang Mai" for b in base_list)
    reg_data = {
        "name": "My Company",
        "email": "test@company.com",
        "main_province_id": base_list[0]["id"],
        "secondary_province_id": None,
    }
    reg_resp = await client.post(
        "/v1/province_tax/register", json=reg_data, headers=headers
    )
    assert reg_resp.status_code == 201
    reg = reg_resp.json()
    assert reg["main_province_tax"] == 7.5

    reg_list_resp = await client.get("/v1/province_tax/registered", headers=headers)
    assert reg_list_resp.status_code == 200
    reg_list = reg_list_resp.json()
    assert any(r["id"] == reg["id"] for r in reg_list)
