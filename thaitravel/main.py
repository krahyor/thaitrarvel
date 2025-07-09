from contextlib import asynccontextmanager
from fastapi import FastAPI

from . import models
from . import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await models.init_db()
    yield
    # Shutdown
    await models.close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(routers.router)


@app.get("/")
def read_root() -> dict:
    return {"Hello": "World"}
