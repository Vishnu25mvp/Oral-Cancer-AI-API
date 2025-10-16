# auth_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from ..utils import verify_access_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude paths like login or public endpoints
        if request.url.path in ["/login", "/", "/error"]:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse({"detail": "Authorization header missing"}, status_code=401)
        
        try:
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                return JSONResponse({"detail": "Invalid token type"}, status_code=401)
            payload = verify_access_token(token)
            # Attach user info to request.state for use in routes
            request.state.user = payload
        except Exception as e:
            return JSONResponse({"detail": str(e)}, status_code=401)
        
        response = await call_next(request)
        return response
