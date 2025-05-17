import logging
import uuid
from datetime import timedelta
from timeit import default_timer as timer
from typing import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class RequestTrackingMiddleware:
    def __init__(
        self,
        get_response: Callable[
            [
                HttpRequest,
            ],
            HttpResponse,
        ],
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        If the request is to the API (excluding the docs):
        Set the X-Request-ID header and log the request and response
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
            client_ip = request.META["REMOTE_ADDR"]
            request_body: str | None = None

            if request.method != "GET":
                if request.FILES:
                    files_body: dict[str, list[str]] = {}
                    for key in request.FILES:
                        files_body[key] = []
                        for f in request.FILES.getlist(key):
                            files_body[key].append(str(f.name))
                    request_body = str(files_body)
                else:
                    request_body = (
                        request.body.decode("utf-8") if request.body else None
                    )

            logger.info(
                f"Request<{request_id}>: {client_ip=} {request.method=} {request.path=} request_body={request_body}"
            )
            response_start = timer()
            response = self.get_response(request)
            response_end = timer()
            response_time = timedelta(seconds=response_end - response_start)
            response["X-Request-ID"] = request_id
            logger.info(
                f"Response<{request_id}>: {response.status_code=}, execution_time={response_time}"
            )
            return response

        return self.get_response(request)
