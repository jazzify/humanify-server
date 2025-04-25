from typing import Any

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager as DjangoBaseUserManager
from django.db import models


class BaseUserManager(DjangoBaseUserManager):
    def create_user(
        self,
        email: str,
        password: str | None = None,
        is_active: bool = True,
        is_admin: bool = False,
        is_superuser: bool = False,
    ) -> "BaseUser":
        if not email:
            raise ValueError("The Email field must be set")

        user = self.model(
            email=self.normalize_email(email.lower()),
            is_active=is_active,
            is_admin=is_admin,
            is_superuser=is_superuser,
        )
        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)
        return user  # type: ignore[no-any-return]

    def create_superuser(self, email: str, password: str | None = None) -> "BaseUser":
        user = self.create_user(
            email=email,
            password=password,
            is_admin=True,
            is_superuser=True,
        )

        return user


class BaseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = BaseUserManager()

    def __str__(self) -> str | Any:
        return self.email

    @property
    def is_staff(self) -> bool | Any:
        return self.is_admin
