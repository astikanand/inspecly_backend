""" This is main file -> Entry to the project """
import uvicorn

from apis.inspection_apis.routers import router as inspections_router
from config.setup import app_settings
from core.server import app

# App Routes
V1_APIS = "/api/v1"

# Inspection Routes
app.include_router(inspections_router, tags=["inspections"], prefix=f"{V1_APIS}/inspections")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.HOST,
        reload=app_settings.DEBUG_MODE,
        port=app_settings.PORT,
    )
