from fastapi.responses import JSONResponse
from typing import Optional, Dict

def success_response(
    data: Optional[Dict] = None, 
    message: str = "Success", 
    status_code: int = 200
) -> JSONResponse:
    """
    Standard success response
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data or {}
        }
    )


def error_response(
    message: str = "Error", 
    details: Optional[Dict] = None, 
    status_code: int = 400
) -> JSONResponse:
    """
    Standard error response
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "details": details or {}
        }
    )
