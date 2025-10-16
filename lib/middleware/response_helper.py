from fastapi.responses import JSONResponse
from fastapi import Request

async def response_helper(request: Request, call_next):
    response = await call_next(request)
    # You can wrap all responses here if needed
    return response
