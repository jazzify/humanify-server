from apps.users.models import BaseUser


def user_create(
    *,
    email: str,
    is_active: bool = True,
    is_admin: bool = False,
    password: str | None = None,
) -> BaseUser:
    return BaseUser.objects.create_user(
        email=email, is_active=is_active, is_admin=is_admin, password=password
    )
