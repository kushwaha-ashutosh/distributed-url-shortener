from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShortenRequest(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None

class ShortenResponse(BaseModel):
    original_url: str
    short_url: str
    alias: str
    created_at: datetime

class URLRecord(BaseModel):
    alias: str
    original_url: str
    clicks: int = 0
    created_at: datetime