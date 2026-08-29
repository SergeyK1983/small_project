from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.admin.admin_setup import setup_admin
from src.auth.api.v1.api_router import router as auth_v1_router
from src.pay_system.api.v1.api_router import router as pay_system_v1_router
from src.core.config import settings
from src.core.lifespan import lifespan
from src.core.middleware import DBSessionMiddleware, LoggingMiddleware
from src.core.templates import index_router
from src.middleware.auth_middleware import AuthMiddleware


app = FastAPI(
    lifespan=lifespan,
    title="Small Project API",
    version="1.0.0",
    description="""
        Небольшой проект для отработки аутентификации и авторизации с применением JWT токенов.
        Имитация работы со сторонней платежной системой.
    """,
)

# middleware
app.add_middleware(LoggingMiddleware)
# app.add_middleware(SessionMiddleware, secret_key=settings.PASSWORD_FILE,)
app.add_middleware(AuthMiddleware)
app.add_middleware(DBSessionMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=2048, compresslevel=5)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
    expose_headers=["access_token", "Authorization"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["0.0.0.0", "127.0.0.1", "localhost"].extend(settings.ALLOWED_HOST)
)

# admin-panel
setup_admin(app)

# static
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# endpoints
app.include_router(index_router)
app.include_router(auth_v1_router)
app.include_router(pay_system_v1_router)
