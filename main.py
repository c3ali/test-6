from fastapi import FastAPI
from middleware.cors import setup_cors
from middleware.logging import LoggingMiddleware
from api.v1.api import api_router
from config import settings
import uvicorn
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION
)
setup_cors(app)
app.add_middleware(LoggingMiddleware)
app.include_router(api_router, prefix="/api/v1")
@app.get("/health")
async def health_check():
    return {"status": "ok"}
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )