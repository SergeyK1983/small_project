from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.core.config import settings
from src.core.lifespan import lifespan
from src.core.middleware import DBSessionMiddleware


app = FastAPI(
    lifespan=lifespan,
)

# middleware
app.add_middleware(SessionMiddleware, secret_key=settings.PASSWORD_FILE,)
app.add_middleware(DBSessionMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=2048, compresslevel=5)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
    expose_headers=["access_token", ],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost",  settings.ALLOWED_HOST])

