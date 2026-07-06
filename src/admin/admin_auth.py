from fastapi import HTTPException
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.auth.schemas.input.user_auth_schema import UserAuthSchema
from src.auth.schemas.output.token import UserTokenSchema
from src.auth.services.auth_service import AuthUserService
from src.auth.utils.depends import authenticate_middleware
from src.auth.utils.token import app_token
from src.core.logger import logger


class AdminAuth(AuthenticationBackend):

    def __init__(
        self,
        secret_key: str,
    ):
        super().__init__(secret_key)
        self.secret_key = secret_key

    async def login(self, request: Request) -> bool:

        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        try:
            user = UserAuthSchema.model_validate(
                {"username": username, "password": password}
            )
            response: UserTokenSchema = await AuthUserService().login_user(
                user=user,
                db=request.state.db,
            )
            token = response.token
        except Exception as exp:
            logger.error("Ошибка при входе в админ панель: {}", str(exp))
            return False

        if not token:
            return False

        request.session["token"] = "JWT " + token
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        try:
            app_token.verify_access_token(token)
        except HTTPException:
            return False

        res = await authenticate_middleware(request, token)
        if not res:
            return False

        user = request.state.user
        return user.is_superuser
