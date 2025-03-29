import logging

logger = logging.getLogger(__name__)

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Incoming request to {request.path}: {request.body}")
        response = self.get_response(request)
        logger.info(f"response data: {response.data}")
        return response

