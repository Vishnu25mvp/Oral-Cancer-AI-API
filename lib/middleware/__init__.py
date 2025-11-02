# middleware/__init__.py

# Custom middleware
from .logger import LoggingMiddleware
from .exception import ExceptionMiddleware

# Third-party / built-in middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

def register_middleware(app):
    """
    Register all middleware that should run early (order matters)
    """
    # 1. Security / HTTPS
    # app.add_middleware(HTTPSRedirectMiddleware)
    
    # 2. CORS for cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # change to your frontend domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. GZip for response compression
    app.add_middleware(GZipMiddleware, minimum_size=500)
    

    # 4. Session Middleware (if needed)
    app.add_middleware(SessionMiddleware, secret_key="your_session_secret")

    # 5. Custom Logging Middleware
    app.add_middleware(LoggingMiddleware)

    # 6. JWT / Auth Middleware
    # app.add_middleware(AuthMiddleware)


def register_middleware_at_last(app):
    """
    Register middleware that should run last (e.g., exception handling)
    """
    app.add_middleware(ExceptionMiddleware)
