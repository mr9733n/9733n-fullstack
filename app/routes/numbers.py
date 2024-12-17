# app/routes/numpers.py
import aiohttp
import logging
from fastapi import APIRouter, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.helpers.common_helper import get_supported_countries, get_age_days_by_id
from app.services.textr_service import TextrService
from app.services.onlinesim_service import OnlineSimService
from app.services.another_service import AnotherService
from app.utils.cache_manager import CacheManager
from app.helpers.constants import AGE_MAP

router = APIRouter(
    prefix="/numbers",
    tags=["Numbers"],
    responses={404: {"description": "Not found"}},
)
limiter = Limiter(key_func=get_remote_address)

# The service and cache manager will be injected during the router setup
service_instances = {}
cache_manager: CacheManager = None

def init_router(service_instances, cache_mgr: CacheManager):
    global services, cache_manager
    services = service_instances
    cache_manager = cache_mgr
    logging.info("Routes: Services and cache manager initialized successfully.")

@router.get("/textr-numbers")
async def get_filtered_numbers():
    # Now we can access the textr service dynamically
    textr_service = services.get("textr")
    if not textr_service:
        raise HTTPException(status_code=500, detail="Textr service is not configured.")
    
    numbers = textr_service.fetch_numbers()
    if not numbers:
        return {"detail": "No numbers found"}
    
    return numbers

@router.get("/fresh-numbers", summary="Get the freshest numbers across all countries")
async def get_fresh_numbers(limit: int = Query(3, ge=1, le=100), max_age: int = Query(7, ge=1)):
    if not cache_manager.number_cache:
        raise HTTPException(status_code=500, detail="Cache is cooking. Wait a minute.")

    fresh_numbers = []
    for country, numbers in cache_manager.number_cache.items():
        filtered_numbers = []
        for num in numbers:
            age_id = num.get("age_id")
            if age_id is not None:
                age_days = get_age_days_by_id(age_id)
                if age_days is not None and age_days <= max_age:
                    filtered_numbers.append(num)
            else:
                logging.warning(f"Number {num['number']} in country {country} has no valid age_id.")
        
        if filtered_numbers:
            sorted_numbers = sorted(filtered_numbers, key=lambda x: get_age_days_by_id(x["age_id"]))
            fresh_numbers.extend(sorted_numbers)

    limited_numbers = fresh_numbers[:limit]

    if not limited_numbers:
        raise HTTPException(status_code=404, detail="No fresh numbers found")

    return limited_numbers

@router.get("/countries")
@limiter.limit("5/minute")
async def get_countries(request: Request):
    logging.info("Routes: Endpoint /countries accessed")
    try:
        countries = get_supported_countries()
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
    if country not in get_supported_countries():
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
