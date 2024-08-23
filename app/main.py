import os
import json
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from app.routers import numbers
from datetime import datetime
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

api_key = os.getenv("ONLINE_SIM_API_KEY")


log_filename = f"logs/log_{datetime.now().strftime('%Y-%m-%d')}.txt"
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load service configs
def load_config(service_name):
    config_path = f"config/{service_name}_config.json"
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        logging.error(f"Failed to load service configuration from {config_path}: {e}")
        raise

# Load main config
try:
    with open('config/main_config.json', 'r') as main_config_file:
        main_config = json.load(main_config_file)
        logging.info("Main configuration loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load main configuration: {e}")
    raise

active_service = main_config.get("active_service", "onlinesim")
service_config = load_config(active_service)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SMS API",
    description="API for fetching and monitoring SMS messages via various services.",
    version="1.0.0"
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
numbers.init_router(service_config)
app.include_router(numbers.router)

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    logging.info("Root endpoint accessed")
    
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
    cert_path = os.path.join(BASE_DIR, "..", "certs", "selfsigned.crt")
    key_path = os.path.join(BASE_DIR, "..", "certs", "selfsigned.key")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path
    )
