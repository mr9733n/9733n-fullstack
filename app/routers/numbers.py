import aiohttp
import logging
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.onlinesim_service import OnlineSimService
from app.services.another_service import AnotherService

router = APIRouter(
    prefix="/numbers",
    tags=["Numbers"],
    responses={404: {"description": "Not found"}},
)
limiter = Limiter(key_func=get_remote_address)

# Функция для инициализации сервиса
def get_service(config):
    services = {
        "onlinesim": OnlineSimService, 
        "another": AnotherService
    }
    active_service_name = config.get("active_service", "onlinesim")  # Определяем активный сервис из конфига
    service_class = services.get(active_service_name)
    
    if not service_class:
        logging.error(f"Service '{active_service_name}' not found in configuration.")
        raise ValueError(f"Service '{active_service_name}' not found.")

    return service_class(config)

# Инициализация сервиса при старте маршрутов
service = None

def init_router(config):
    global service
    service = get_service(config)
    logging.info(f"Service '{config.get('active_service', 'onlinesim')}' initialized successfully.")

@router.get("/countries")
@limiter.limit("5/minute")  # Максимум 5 запросов в минуту
async def get_countries(request: Request):
    logging.info("Endpoint /countries accessed")
    try:
        countries = service.get_supported_countries()
        logging.info(f"Supported countries retrieved: {countries}")
        return countries
    except Exception as e:
        logging.error(f"Error retrieving countries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}")
async def get_numbers(country: str):
    logging.info(f"Endpoint /{country} accessed to fetch numbers")
    if country not in service.get_supported_countries():
        logging.warning(f"Country '{country}' not found in supported countries")
        raise HTTPException(status_code=404, detail="Country not found.")
    
    async with aiohttp.ClientSession() as session:
        try:
            fresh_numbers = await service.fetch_numbers(session, country)
            logging.info(f"Fetched {len(fresh_numbers)} numbers for country: {country}")
            return fresh_numbers
        except Exception as e:
            logging.error(f"Error fetching numbers for country '{country}': {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}/{number}/sms")
async def get_sms(country: str, number: str):
    logging.info(f"Endpoint /{country}/{number}/sms accessed to fetch SMS")
    if country not in service.get_supported_countries():
        logging.warning(f"Country '{country}' not found in supported countries")
        raise HTTPException(status_code=404, detail="Country not found.")
    
    async with aiohttp.ClientSession() as session:
        try:
            messages = await service.fetch_sms(session, country, number)
            logging.info(f"Fetched {len(messages)} SMS for number: {number} in country: {country}")
            return messages
        except Exception as e:
            logging.error(f"Error fetching SMS for number '{number}' in country '{country}': {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
