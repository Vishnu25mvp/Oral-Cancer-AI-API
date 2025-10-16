from fastapi import FastAPI
from lib.middleware import register_middleware, register_middleware_at_last
from lib.routes import register_routes
from lib.utils import success_response, error_response
from lib.config.settings import settings  # import centralized settings
from lib.config.database import init_databases

app = FastAPI()

# Register middleware and routes
register_middleware(app)
@app.on_event("startup")
async def startup_event():
    await init_databases()
register_routes(app)
register_middleware_at_last(app)

# =========================
# Sample routes
# =========================
@app.get("/")
def home():
    return success_response(message="Server is running perfectly")

@app.get("/error")
def error_demo():
    return error_response(message="This is an error demo")

# =========================
# Run Uvicorn server
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
