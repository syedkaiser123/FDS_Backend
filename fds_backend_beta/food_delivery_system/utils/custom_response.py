from rest_framework.response import Response


class CustomResponse(Response):
    def __init__(self, data=None, message=None, success=True, status=None, **kwargs):
        response_data = {
            "success": success,
            "message": message if message else ("Success" if success else "Error"),
            "data": data if data is not None else {},
        }
        super().__init__(response_data, status=status, **kwargs)

