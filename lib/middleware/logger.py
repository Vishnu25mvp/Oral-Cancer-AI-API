# logging_middleware.py
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        logging.info(f"Incoming request: {request.method} {request.url}")
        
        try:
            response: Response = await call_next(request)
        except Exception as e:
            logging.exception(f"Exception occurred: {str(e)}")
            raise e
        
        process_time = time.time() - start_time
        logging.info(f"Completed request: {request.method} {request.url} "
                     f"Status: {response.status_code} Time: {process_time:.4f}s")
        
        # Optional: Add process time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        return response
