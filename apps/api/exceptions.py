from typing import Any

from rest_framework import status


class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        extra: dict[str, Any] | None = None,
    ):
        super().__init__(message)

        self.status = status
        self.message = message
        self.extra = extra or {}
