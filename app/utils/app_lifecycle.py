# app/utils/app_lifecycle.py
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.utils.cache_manager import CacheManager

@asynccontextmanager
async def app_lifecycle(app: FastAPI, cache_manager: CacheManager):
    logging.info("Utils: Starting preloading cache...")
    task = asyncio.create_task(cache_manager.preload_numbers())
    
    yield

    task.cancel()
    logging.info("Utils: Service stopped.")
