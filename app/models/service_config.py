# app/models/service_config.py
from pydantic import BaseModel
from typing import List, Dict

class ServiceConfig(BaseModel):
    countries: List[str]
    headers: Dict[str, str]
    urls: Dict[str, str]
