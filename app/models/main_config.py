# app/models/main_config.py
from typing import List
from pydantic import BaseModel

class MainConfig(BaseModel):
    title: str
    description: str
    version: str
    author: str
    services: List[str]
    cache_for_fresh_numbers: List[str] 
    exclude_from_cache: List[str]
