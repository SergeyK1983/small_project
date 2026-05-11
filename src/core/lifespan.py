from typing import TYPE_CHECKING
from contextlib import asynccontextmanager

from src.core.database import db_helper


if TYPE_CHECKING:
    from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: "FastAPI"):
    
    yield

    await db_helper.dispose()

