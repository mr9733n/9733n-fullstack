import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, HTTPException, Query, Request, FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.onlinesim_service import OnlinesimService
from app.config import onlinesim_config
from app.utils.logger import logger
logging = logger

# Лимитер запросов
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
    tags=["Numbers"],
    responses={404: {"description": "Not found"}},
)

onlinesim_service = OnlinesimService(onlinesim_config)
__version__ = '0.0.1.3'


@router.get("/", summary="Root endpoint for Onlinesim Free API Service")
async def index():
    """Возвращает базовую информацию о проекте."""
    return {"message": "Welcome to Onlinesim Free API Service", "version": __version__}

@router.get("/countries", summary="Get list of fresh countries with numbers")
async def get_countries():
    try:
        # Возвращаем текущий кеш
        fresh_countries = await onlinesim_service.get_cache()
        return {"countries": fresh_countries}
    except Exception as e:
        logger.exception(f"Error fetching fresh countries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/update", summary="Manually trigger cache update")
async def cache_update():
    try:
        if onlinesim_service.update_in_progress:
            return {"message": "Cache update already in progress."}

        asyncio.create_task(onlinesim_service.update_cache())
        return {"message": "Cache update started."}
    except Exception as e:
        logger.exception(f"Error starting cache update: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}", summary="Get numbers for a specific country and update if missing")
async def get_country_numbers(country: str):
    """
    Возвращает номера для указанной страны.
    Если данные отсутствуют в кэше, они обновляются.
    """
    try:
        numbers = await onlinesim_service.get_numbers(country)
        if not numbers:
            raise HTTPException(status_code=404, detail=f"No numbers found for country: {country}")
        return {"country": country, "numbers": numbers}
    except Exception as e:
        logging.exception(f"Error fetching numbers for country {country}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}/{number}/sms", summary="Get SMS for a specific number")
async def get_sms(country: str, number: str):
    try:
        sms = await onlinesim_service.get_sms(country, number)
        if not sms:
            raise HTTPException(status_code=404, detail="No SMS found")
        return {"country": country, "number": number, "sms": sms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))