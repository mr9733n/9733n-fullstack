import aiohttp
import logging
from fastapi import APIRouter, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.helper import is_relevant_number, sort_numbers
from app.services.onlinesim_service import OnlineSimService
from app.services.another_service import AnotherService
from app.utils import CacheManager

router = APIRouter(
    prefix="/numbers",
    tags=["Numbers"],
    responses={404: {"description": "Not found"}},
)
limiter = Limiter(key_func=get_remote_address)

# The service and cache manager will be injected during the router setup
service = None
cache_manager: CacheManager = None

def init_router(config, cache_mgr: CacheManager):
    global service
    global cache_manager
    cache_manager = cache_mgr
    services = {
        "onlinesim": OnlineSimService,
        "another": AnotherService
    }
    
    active_service_name = config.get("active_service", "onlinesim")
    service_class = services.get(active_service_name)
    
    if not service_class:
        logging.error(f"Routes: Service '{active_service_name}' not found in configuration.")
        raise ValueError(f"Routes: Service '{active_service_name}' not found.")

    service = service_class(config)
    logging.info(f"Routes: Service '{active_service_name}' initialized successfully.")

@router.get("/fresh-numbers", summary="Get the freshest numbers across all countries")
async def get_fresh_numbers(limit: int = Query(3, ge=1, le=100), max_age: int = Query(7, ge=1)):
    if not cache_manager.number_cache:
        raise HTTPException(status_code=500, detail="Cache is cooking. Wait a minute.")

    fresh_numbers = {}
    for country, numbers in cache_manager.number_cache.items():
        # Фильтруем номера по возрасту
        filtered_numbers = [num for num in numbers if is_relevant_number(num["age"], max_age)]
        if filtered_numbers:
            # Сортируем от самых свежих к старым
            logging.debug(f"Before sorting: {filtered_numbers}")
            sorted_numbers = sort_numbers(filtered_numbers)  # Используем отфильтрованные данные
            logging.debug(f"After sorting: {sorted_numbers}")

            # Ограничиваем количество возвращаемых номеров
            fresh_numbers[country] = sorted_numbers[:limit]

    if not fresh_numbers:
        raise HTTPException(status_code=404, detail="No fresh numbers found")

    return fresh_numbers

@router.get("/countries")
@limiter.limit("5/minute")
async def get_countries(request: Request):
    logging.info("Routes: Endpoint /countries accessed")
    try:
        countries = service.get_supported_countries()
        logging.info(f"Routes: Supported countries retrieved: {countries}")
        return countries
    except Exception as e:
        logging.error(f"Routes: Error retrieving countries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}")
async def get_numbers(country: str):
    logging.info(f"Endpoint /{country} accessed to fetch numbers")
    if country not in service.get_supported_countries():
        logging.warning(f"Routes: Country '{country}' not found in supported countries")
        raise HTTPException(status_code=404, detail="Country not found.")
    
    async with aiohttp.ClientSession() as session:
        try:
            fresh_numbers = await service.fetch_numbers(session, country)
            logging.info(f"Routes: Fetched {len(fresh_numbers)} numbers for country: {country}")
            return fresh_numbers
        except Exception as e:
            logging.error(f"Routes: Error fetching numbers for country '{country}': {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}/{number}/sms")
async def get_sms(country: str, number: str):
    logging.info(f"Endpoint /{country}/{number}/sms accessed to fetch SMS")
    if country not in service.get_supported_countries():
        logging.warning(f"Routes: Country '{country}' not found in supported countries")
        raise HTTPException(status_code=404, detail="Country not found.")
    
    async with aiohttp.ClientSession() as session:
        try:
            messages = await service.fetch_sms(session, country, number)
            logging.info(f"Fetched {len(messages)} SMS for number: {number} in country: {country}")
            return messages
        except Exception as e:
            logging.error(f"Routes: Error fetching SMS for number '{number}' in country '{country}': {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
