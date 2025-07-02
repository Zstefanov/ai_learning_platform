from dotenv import load_dotenv
import os
print("TOGETHER_API_KEY:", os.getenv("TOGETHER_API_KEY"))

# Load env variables before importing app
load_dotenv()

from main import app
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="module")
def sync_client():
    return TestClient(app)

@pytest_asyncio.fixture(scope="module")
async def async_client():
    transport = ASGITransport(app=app)  # remove lifespan param here
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module")
def db_path():
    # Adjust the path to your database location here
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../db/my_database.db"))