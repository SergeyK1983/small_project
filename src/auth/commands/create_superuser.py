from src.auth.repository.user_register_repository import UserRegisterRepo
from src.auth.schemas.input.user_auth_schema import UserAuthSchema
from src.auth.utils.password import password
from src.core.database import db_helper


async def create_superuser(username: str, pwd: str) -> str:
    """
    Создает суперпользователя.
    Args:
        username: name of the user
        pwd: <PASSWORD>
    Return:
        Massage: str
    """

    admin = UserAuthSchema(username=username, password=pwd)
    admin.password = password.hashing_password(admin.password)
    
    session = db_helper.get_scoped_session()
    exists = None
    result = None

    try:
        exists = await UserRegisterRepo._is_exists_user_by_username(admin.username, session) # type: ignore

        if exists is False:
            result = await UserRegisterRepo.create_superuser(admin.username, admin.password, session) # type: ignore
    except Exception:
        pass
    finally:
        await session.close()
 
    if exists:
        return f"Суперпользователь c {username} уже существует!"

    if not result:
        return f"Суперпользователя {username} создать не удалось"

    return f"Суперпользователь {username} создан!"
