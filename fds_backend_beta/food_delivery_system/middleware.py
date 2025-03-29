import logging
import time

logger = logging.getLogger("data.log")

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Incoming request to {request.path}: {request.body}")
        response = self.get_response(request)
        logger.info(f"response data: {response.data}")
        return response



class QueryProfilerMiddleware:
    def resolve(self, next, root, info, **args):
        start_time = time.time()
        result = next(root, info, **args)
        duration = time.time() - start_time
        logger.info(f"GraphQL Query: {info.field_name}, Duration: {duration:.4f} sec")
        return result


