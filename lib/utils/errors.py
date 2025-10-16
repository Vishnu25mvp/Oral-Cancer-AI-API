# errors.py
from starlette.responses import JSONResponse

class AppException(Exception):
    """Custom application exception"""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}

def raise_error(message: str, status_code: int = 400, details: dict = None):
    """Utility to throw AppException

        @app.get("/test-error")
        async def test_error():
            # Throw a custom error
            raise_error("This is a custom error", status_code=422, details={"field": "value"})
    
    """
    raise AppException(message=message, status_code=status_code, details=details)


