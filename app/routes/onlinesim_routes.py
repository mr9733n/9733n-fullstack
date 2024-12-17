from fastapi import APIRouter, HTTPException, Query, Request
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

@router.get("/countries", summary="Get list of fresh countries with numbers")
@limiter.limit("5/minute")
async def get_countries(request: Request):
    """Возвращает страны, которые содержат свежие номера."""
    try:
        fresh_countries = onlinesim_service.get_fresh_countries()
        if not fresh_countries:
            raise HTTPException(status_code=404, detail="No fresh countries available.")
        return {"countries": fresh_countries}
    except Exception as e:
        logging.exception(f"Error fetching countries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{country}", summary="Get numbers for a specific country")
async def get_numbers(country: str):
    """Возвращает номера для указанной страны из кеша."""
    try:
        numbers = await onlinesim_service.get_numbers(country)
        if not numbers:
            raise HTTPException(status_code=404, detail="No numbers found")
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