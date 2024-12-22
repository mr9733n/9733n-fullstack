import asyncio
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.api.config import main_config, onlinesim_config
from backend.api.routes.onlinesim_routes import router as onlinesim_router, limiter
from backend.api.services.onlinesim_service import OnlinesimService
from backend.api.routes.rna_routes import router as rna_router
from backend.api.utils.logger import logger
logging = logger
cache = {}

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

api_key = os.getenv('ONLINE_SIM_API_KEY', 'default_secret_key')

title = main_config.get("app_name", "9733n API"),
version = main_config.get("version", "0.1.0.0"),
description = main_config.get("description", "Default API description"),
author = main_config.get("author", "9733n")

onlinesim_service = OnlinesimService(onlinesim_config)


async def periodic_cache_update():
    while True:
        # TODO:
        logging.info("RELOAD SMTHNG.")
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

# Подключение маршрутов
app.include_router(onlinesim_router, prefix="/numbers", tags=["OnlineSim Numbers"])
app.include_router(rna_router, prefix="/rna", tags=["RNA Project"])

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
    cert_dir = "api/certs"

    cert_path = os.path.join(cert_dir, "selfsigned.crt")
    key_path = os.path.join(cert_dir, "selfsigned.key")
    logging.info(f"Main: {cert_path}, {key_path}")
    logging.info("Main: Starting api service...")
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path,
        reload = True
    )