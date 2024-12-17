# app/main.py
from app.models import service_config
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
from app.config import load_all_service_configs, load_main_config, load_service_config
from app.services.onlinesim_service import OnlineSimService
from app.routes import numbers
from app.utils.cache_manager import CacheManager

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
logging.debug(f"Loaded main configuration: {main_config.description}")  # Выводит содержимое main_config

title=main_config.title
description=main_config.description
version=main_config.version
author=main_config.author
logging.info(f"Main: Name: {title}, Version: {version}, (C)2024 by {author}, Description: {description}")
service_configs = load_all_service_configs(main_config)

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
numbers.init_router(services, cache_manager)
app.include_router(numbers.router)

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    logging.info("Main: Root endpoint accessed")
    
    docs_routes = []
    api_routes = []

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
                    else:
                        api_routes.append(route_info)

    return {
        "title": app.title, 
        "version": app.version,
        "description": app.description,
        "api_routes": api_routes,
        "documentation_routes": docs_routes,
    }

if __name__ == "__main__":
    logging.info("Main: Loading certificates...")
    cert_path = os.path.join(BASE_DIR, "..", "certs", "selfsigned.crt")
    key_path = os.path.join(BASE_DIR, "..", "certs", "selfsigned.key")
    logging.info("Main: Starting api service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path
    )
