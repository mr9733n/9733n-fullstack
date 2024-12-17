# app/routes/numpers.py
import aiohttp
import logging
from fastapi import APIRouter, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import initialize_providers
from app.main import services, limiter
from app.utils.cache_manager import CacheManager
from app.helpers.common_helper import CommonHelper
from app.helpers.onlinesim_helper import OnlinesimHelper
from app.core.sms_provider_factory import SmsProviderFactory
from fastapi import APIRouter, HTTPException
import logging

router = APIRouter(
    prefix="/numbers",
    tags=["Numbers"],
    responses={404: {"description": "Not found"}},
)

# Глобальные переменные для хранения экземпляров
factory: SmsProviderFactory = None
cache_manager: CacheManager = None
common_helper: CommonHelper = None
onlinesim_helper: OnlinesimHelper = None


def init_router(service_configs, cache_mgr, common_hlp, onlinesim_hlp):
    global factory, cache_manager, common_helper, onlinesim_helper
    cache_manager = cache_mgr
    common_helper = common_hlp
    onlinesim_helper = onlinesim_hlp

    # Инициализируем фабрику провайдеров
    factory = initialize_providers(service_configs)
    logging.info("Routes: Services, cache manager, and helpers initialized successfully.")


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
async def get_fresh_numbers(limit: int = Query(3, ge=1, le=100), max_age: int = Query(7, ge=1), helper=None):
    if not cache_manager.number_cache:
        raise HTTPException(status_code=500, detail="Cache is cooking. Wait a minute.")

    fresh_numbers = []
    for country, numbers in cache_manager.number_cache.items():
        filtered_numbers = []
        for num in numbers:
            age_id = num.get("age_id")
            if age_id is not None:
                common_helper = helper
                age_days = common_helper.get_age_days_by_id(age_id)
                if age_days is not None and age_days <= max_age:
                    filtered_numbers.append(num)
            else:
                logging.warning(f"Number {num['number']} in country {country} has no valid age_id.")

        if filtered_numbers:
            sorted_numbers = sorted(filtered_numbers, key=lambda x: common_helper.get_age_days_by_id(x["age_id"]))
            fresh_numbers.extend(sorted_numbers)

    limited_numbers = fresh_numbers[:limit]

    if not limited_numbers:
        raise HTTPException(status_code=404, detail="No fresh numbers found")

    return limited_numbers


@router.get("/countries")
@limiter.limit("5/minute")
async def get_countries():
    try:
        # Используем common_helper
        countries = common_helper.get_supported_countries()

        # Используем фабрику для получения провайдеров
        provider_names = factory.providers.keys()
        logging.info(f"Available providers: {provider_names}")

        return {"countries": countries, "providers": list(provider_names)}
    except Exception as e:
        logging.exception("Error retrieving countries")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{country}")
async def get_numbers(country: str):
    logging.info(f"Endpoint /{country} accessed to fetch numbers")
    if country not in common_helper.get_supported_countries():
        logging.warning(f"Routes: Country '{country}' not found in supported countries")
        raise HTTPException(status_code=404, detail="Country not found.")

    service = services.get("textr")  # Укажите конкретный сервис, если нужно
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
    try:
        provider = SmsProviderFactory.get_provider("onlinesim")  # Укажи конкретного провайдера
        messages = await provider.fetch_sms(country, number)
        return messages
    except Exception as e:
        logging.error(f"Error fetching SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch SMS")


@router.get("/numbers/countries/{service_name}")
def get_countries(service_name: str):
    if service_name not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    service = services[service_name]
    return service.get_supported_countries()


@router.get("/numbers/countries")
async def get_numbers_by_country(country: str):
    try:
        # Используем onlinesim_helper для сортировки
        provider = factory.get_provider("onlinesim")  # Пример получения провайдера
        numbers = provider.get_numbers(country)
        sorted_numbers = onlinesim_helper.sort_numbers(numbers)
        return {"country": country, "numbers": sorted_numbers}
    except Exception as e:
        logging.exception(f"Error fetching numbers for country: {country}")
        raise HTTPException(status_code=500, detail=str(e))
