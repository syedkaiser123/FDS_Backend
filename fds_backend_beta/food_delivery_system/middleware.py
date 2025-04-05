import logging
import time
import json
import uuid
from graphql.execution.execute import ExecutionResult

from food_delivery_system.utils.utilities import generate_request_id


logger = logging.getLogger("data.log")

class LogRequestMiddleware:
    """
    Custom middleware to log only Django/REST based requests and responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = generate_request_id()
        request.request_id = request_id  # attach request_id to request object

        # Only log non-GraphQL requests
        if request.path != "/graphql/":
            try:
                body = request.body.decode().strip()
                request_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                request_data = body  # just raw text
            logger.info(f"[{request_id}] - Incoming request to {request.path}:\n{request.method} call\n{json.dumps(request_data, indent=2)}")

        response = self.get_response(request)
        # Only log non-GraphQL responses
        if request.path != "/graphql/":
            try:
                # response_data = response.content.decode("utf-8")
                response_body = response.content.decode("utf-8")
                response_json = json.loads(response_body)
                pretty_response = json.dumps(response_json, indent=2)
                logger.info(f"[{request_id}] - Response from {request.path}:\n{pretty_response}")
            except Exception:
                response_data = str(response)
                # fallback if it's not valid JSON
                logger.info(f"[{request_id}] - Raw response from {request.path}:\n{response.content}")

        return response


class QueryProfilerMiddleware:
    def resolve(self, next, root, info, **args):
        request = info.context

        # Only proceed with logging once per top-level query/mutation
        is_top_level = info.path.prev is None
        if is_top_level:
            request_id = getattr(request, "request_id", str(uuid.uuid4()))
            request.request_id = request_id
            request._start_time = time.time()

            try:
                body = request.body.decode("utf-8")
                graphql_data = json.loads(body)
                query_str = graphql_data.get("query", "").strip()
                operation_name = graphql_data.get("operationName", "")

                logger.info(f"[{request_id}] - GraphQL operation: {operation_name}")
                logger.info(f"[{request_id}] - GraphQL query:\n{request.method} call\n{query_str}")
            except Exception as e:
                logger.warning(f"[{request_id}] - Failed to log GraphQL request: {e}")

        try:
            result = next(root, info, **args)

            if is_top_level:
                # Check if it's an async resolution
                if hasattr(result, "__await__"):
                    async def await_and_log():
                        resolved = await result
                        self._log_response(request, resolved)
                        return resolved
                    return await_and_log()

                self._log_response(request, result)

            return result

        except Exception as e:
            if is_top_level:
                logger.warning(f"[{request.request_id}] - Error during GraphQL execution: {e}")
                self._log_response(request)
            raise

    def _log_response(self, request, result=None):
        duration = time.time() - getattr(request, "_start_time", time.time())
        request_id = getattr(request, "request_id", "unknown")

        try:
            if isinstance(result, ExecutionResult):
                formatted_response = json.dumps(result.to_dict(), indent=2)
                logger.info(f"[{request_id}] - GraphQL response:\n{formatted_response}")
        except Exception as e:
            logger.warning(f"[{request_id}] - Failed to format GraphQL response: {e}")

        logger.info(f"[{request_id}] - Total Duration: {duration:.4f} sec")





