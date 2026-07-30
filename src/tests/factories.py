from factory.base import Factory
from factory.declarations import Sequence, LazyAttribute

from src.auth.models.user import User
from src.auth.utils.hasher import hasher


class UserFactory(Factory):

    class Meta: # type: ignore
        model = User

    username = Sequence(lambda number: f"user_{number}")
    email = LazyAttribute(lambda user: f"{user.username}@example.com")
    password = hasher.hashing_password("test_password")
    is_superuser = False
    is_active = True
    is_staff = False

