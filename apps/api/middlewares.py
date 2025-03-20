import logging
import uuid

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    def __init__(self, get_response) -> None:  # type: ignore[no-untyped-def]
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        If the request is to the API, then set the request ID and log it, excluding the docs.
        """
        supports_api_tracking = False
        supported_versions = ["v1"]
        for version in supported_versions:
            if request.path.startswith(
                f"/api/{version}/"
            ) and not request.path.startswith(f"/api/{version}/docs/"):
                supports_api_tracking = True
                break

        if supports_api_tracking:
            request_id = str(uuid.uuid4())
            request._request_id = request_id
            logger.info(f"Start Request ID: {request_id}")
            response = self.get_response(request)
            response["X-Request-ID"] = request._request_id
            logger.info(f"Finish Request ID: {request_id}")
            return response

        return self.get_response(request)
