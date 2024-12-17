# app/main.py
from app.utils import cache_manager
from app.utils.app_lifecycle import app_lifecycle
from datetime import datetime
import os
import logging
import uvicorn
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.routes import numbers
from app.config import load_all_service_configs, load_main_config, initialize_providers
from app.utils.cache_manager import CacheManager
from app.helpers.common_helper import CommonHelper
from app.helpers.onlinesim_helper import OnlinesimHelper
from app.routes.numbers import init_router
from app.config import load_all_service_configs, load_main_config

onlinesim_helper = OnlinesimHelper()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()
api_key = os.getenv("ONLINE_SIM_API_KEY")
log_filename = f"logs/log_{datetime.now().strftime('%Y-%m-%d')}.txt"

logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    # level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info(f"Main: Starting service...")
# Load configurations
main_config = load_main_config()
service_configs = load_all_service_configs(main_config)

# Загружаем конфиги
main_config = load_main_config()
service_configs = load_all_service_configs(main_config)

logging.debug(f"Loaded main configuration: {main_config.description}")  # Выводит содержимое main_config

title=main_config.title
description=main_config.description
version=main_config.version
author=main_config.author
logging.info(f"Main: Name: {title}, Version: {version}, (C)2024 by {author}, Description: {description}")
service_configs = load_all_service_configs(main_config)
sms_provider_factory = initialize_providers(main_config)
services = {}

valid_cache_service = None
for caching_service_name in main_config.cache_for_fresh_numbers:
    if caching_service_name not in main_config.exclude_from_cache:
        if caching_service_name in service_configs:
            cache_manager = CacheManager(service_configs[caching_service_name])
            valid_cache_service = caching_service_name
            break

if valid_cache_service is None:
    logging.error("No valid service specified for caching. Exiting.")
    raise ValueError("No valid service specified for caching.")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=title,
    description=description,
    version=version,
    lifespan=lambda app: app_lifecycle(app, cache_manager)
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
numbers.init_router(service_configs, cache_manager, onlinesim_helper)

app.include_router(numbers.router)

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    try:
        logging.info("Main: Root endpoint accessed")

        docs_routes = []
        api_routes = [
            {"path": "/", "description": "Получить список всех маршрутов"},
            {"path": "/countries", "description": "Получить список стран"},
            {"path": "/numbers/{country}", "description": "Получить список номеров по стране"},
            {"path": "/sms/{number}", "description": "Получить SMS для указанного номера"}
        ]

        for route in app.routes:
            if hasattr(route, "methods"):
                for method in route.methods:
                    if method in ["GET"]:  # "GET", "POST", "PUT", "DELETE", "PATCH"
                        route_info = {
                            "path": route.path,
                            "method": method,
                            "name": route.name
                        }

                        if route.path.startswith("/docs") or route.path.startswith("/redoc") or route.path.startswith("/openapi"):
                            docs_routes.append(route_info)
                            logging.debug(f"{docs_routes.__str__()}")
                        else:
                            if isinstance(route_info["path"], str) and isinstance(route_info["method"], str):
                                api_routes.append(route_info)
                                logging.debug(f"{api_routes.__dict__}")

        return {
            "title": app.title,
            "version": app.version,
            "description": app.description,
            "api_routes": api_routes,
            "documentation_routes": docs_routes,
        }
    except Exception as e:
        logging.exception(f"Error occurred in api, {e}")

if __name__ == "__main__":
    logging.info("Main: Loading certificates...")
    cert_path = os.path.join("certs", "selfsigned.crt")
    key_path = os.path.join("certs", "selfsigned.key")

    from app.utils.setup import setup_dependencies

    cache_manager, common_helper, onlinesim_helper = setup_dependencies(service_configs)

    # Подключаем роутер после инициализации
    from app.routes.numbers import init_router

    init_router(service_configs, cache_manager, common_helper, onlinesim_helper)

    logging.info("Main: Starting api service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path
    )
