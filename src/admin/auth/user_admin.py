from sqladmin import ModelView

from src.auth.models.user import User
from src.auth.schemas.input.user_auth_schema import UserSignupSchema
from src.auth.utils.password import password


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id, 
        User.username, 
        User.email, 
        User.first_name, 
        User.second_name, 
        User.last_name, 
        User.is_active, 
        User.is_superuser, 
        User.is_staff,
        User.created,
        User.updated,
    ]
    column_searchable_list = [User.username]
    column_sortable_list = [User.id]
    form_create_rules = ["username", "email", "password", "is_superuser", "is_active"]
    form_edit_rules = ["is_active", "is_superuser", "is_staff"]
    name = "Пользователь"
    name_plural = "Пользователи"
    category = "auth"

    async def on_model_change(self, data, model, is_created, request) -> None:
        username: str = data.get("username", "")
        email: str = data.get("email", "")
        pwd: str = data.get("password", "")

        if is_created:
            try:
                user = UserSignupSchema(username=username, email=email, password=pwd)
                user.password = password.hashing_password(user.password)
            except Exception as e:
                raise ValueError("Переданы не валидные данные: {err}".format(err=str(e)))
        
            data["password"] = user.password
            model.password = user.password
        return

