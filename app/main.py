import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import main_config, onlinesim_config
from app.routes.onlinesim_routes import router as onlinesim_router, limiter
from app.services.onlinesim_service import OnlinesimService
from app.utils.logger import logger
logging = logger
cache = {}

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)
with open("app/config/onlinesim_config.json", "r", encoding="utf-8") as file:
    onlinesim_config = json.load(file)
api_key = os.getenv("ONLINE_SIM_API_KEY")

title = main_config.get("app_name", "OnlineSim API"),
version = main_config.get("version", "0.1.0.0"),
description = main_config.get("description", "Default API description"),
author = main_config.get("author", "9733n")

async def periodic_cache_update():
    while True:
        await onlinesim_service.update_cache()
        logging.info("Background: Cache updated.")
        await asyncio.sleep(300)  # Обновлять каждые 5 минут

# В lifespan добавьте фоновую задачу
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.task = asyncio.create_task(periodic_cache_update())
    yield
    app.state.task.cancel()
    await app.state.task

app = FastAPI(
    title=title,
    version=version,
    description=description,
    lifespan=lifespan
)
logger.info(f"FASTAPI: {title} {version} {description}")
if api_key:
    onlinesim_config["headers"]["Authorization"] = api_key
else:
    raise ValueError("ONLINE_SIM_API_KEY environment variable is not set.")

onlinesim_service = OnlinesimService(onlinesim_config)

app.include_router(onlinesim_router, prefix="/numbers", tags=["OnlineSim Numbers"])

logger.info("Application initialized successfully.")

@app.get("/")
def read_root():
    """Корневой эндпоинт для получения списка маршрутов API."""
    try:
        logging.info("Main: Root endpoint accessed")

        routes = [
            {"path": route.path, "method": list(route.methods), "name": route.name}
            for route in app.routes
            if hasattr(route, "methods") and "GET" in route.methods
        ]

        return {
            "title": app.title,
            "version": app.version,
            "description": app.description,
            "routes": routes,
        }
    except Exception as e:
        logging.exception(f"Error occurred in root endpoint: {e}")
        return {"error": "Internal Server Error"}

if __name__ == "__main__":
    logging.info("Main: Loading certificates...")
    cert_dir = "app/certs"

    cert_path = os.path.join(cert_dir, "selfsigned.crt")
    key_path = os.path.join(cert_dir, "selfsigned.key")
    logging.info(f"Main: {cert_path}, {key_path}")
    logging.info("Main: Starting api service...")
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path,
        reload = True
    )