from fastapi import FastAPI, APIRouter, Depends
from .mail import router as mail_router
from .user import router as user_router
from .profile import router as profile_router
from .result import router as result_router
# Create a router instance
router = APIRouter()

router.include_router(user_router, prefix='/user')
router.include_router(profile_router, prefix='/profile')
router.include_router(mail_router, prefix='/mail')
router.include_router(result_router, prefix='/result')

# Function to register routes to the main app
def register_routes(app: FastAPI):
    app.include_router(router, prefix="/api/v1")


__all__ = ["register_routes"]
