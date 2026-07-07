from sqladmin import Admin

from src.admin.admin_auth import AdminAuth
from src.admin.auth.user_admin import UserAdmin
from src.core.database import db_helper
from src.core.config import settings


def setup_admin(app):
    admin = Admin(
        app,
        db_helper.engine,
        authentication_backend=AdminAuth(secret_key=settings.PASSWORD_FILE),
    )

    admin.add_view(UserAdmin)
    