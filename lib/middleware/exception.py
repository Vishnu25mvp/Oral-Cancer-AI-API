# exception_middleware.py
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from ..utils import AppException

# FastAPI / Starlette imports
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Pydantic imports
from pydantic import ValidationError

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        # Custom application exception
        except AppException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "type": "AppException",
                    "message": e.message,
                    "details": e.details
                }
            )

        # FastAPI validation errors (request body / query / path)
        except RequestValidationError as e:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "type": "RequestValidationError",
                    "message": "Validation failed",
                    "details": e.errors()
                }
            )

        # Pydantic model validation errors (internal / model parsing)
        except ValidationError as e:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "type": "PydanticValidationError",
                    "message": "Data validation failed",
                    "details": e.errors()
                }
            )

        # HTTP exceptions (404, 403, 401 etc.)
        except StarletteHTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "type": "HTTPException",
                    "message": e.detail
                }
            )

        # SQLAlchemy / SQLModel errors
        except IntegrityError as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "type": "IntegrityError",
                    "message": "Database integrity error",
                    "details": str(e.orig)
                }
            )
        except SQLAlchemyError as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "type": "DatabaseError",
                    "message": "Database error occurred",
                    "details": str(e)
                }
            )

        # Catch-all for unexpected exceptions
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "details": str(e)
                }
            )
