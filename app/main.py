from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_db, close_db
from app.cache import connect_cache, close_cache
from app.shortener import create_short_url, resolve_url
from app.models import ShortenRequest, ShortenResponse
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await connect_cache()
    yield
    await close_db()
    await close_cache()

app = FastAPI(title="Distributed URL Shortener", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "instance": settings.instance_id}

@app.post("/shorten", response_model=ShortenResponse)
async def shorten(req: ShortenRequest):
    alias = await create_short_url(req.original_url, req.custom_alias)
    return ShortenResponse(
        original_url=req.original_url,
        short_url=f"{settings.base_url}/{alias}",
        alias=alias,
        created_at=datetime.utcnow()
    )

@app.get("/{alias}")
async def redirect(alias: str):
    url, cache_hit = await resolve_url(alias)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=url, headers={"X-Cache": "HIT" if cache_hit else "MISS"})

@app.get("/analytics/{alias}")
async def analytics(alias: str):
    from app.database import get_db
    db = get_db()
    record = await db.urls.find_one({"alias": alias}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    return record