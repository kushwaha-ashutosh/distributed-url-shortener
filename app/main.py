from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_db, close_db
from app.cache import connect_cache, close_cache
from app.shortener import create_short_url, resolve_url
from app.consistent_hashing import ring, init_ring
from app.models import ShortenRequest, ShortenResponse
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await connect_cache()
    init_ring()
    yield
    await close_db()
    await close_cache()

app = FastAPI(title="Distributed URL Shortener", lifespan=lifespan)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "instance": settings.instance_id,
        "ring_nodes": list(ring.nodes)
    }

@app.post("/shorten")
async def shorten(req: ShortenRequest):
    alias, node = await create_short_url(req.original_url, req.custom_alias)
    return {
        "original_url": req.original_url,
        "short_url": f"{settings.base_url}/{alias}",
        "alias": alias,
        "served_by": node,
        "created_at": datetime.utcnow()
    }

@app.get("/analytics/{alias}")
async def analytics(alias: str):
    from app.database import get_db
    db = get_db()
    record = await db.urls.find_one({"alias": alias}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    record["responsible_node"] = ring.get_node(alias)
    return record

@app.get("/ring/status")
async def ring_status():
    return {
        "nodes": list(ring.nodes),
        "total_vnodes": len(ring.ring),
        "distribution": ring.get_distribution()
    }


@app.delete("/ring/node/{node_id}")
async def remove_ring_node(node_id: str):
    if node_id not in ring.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    ring.remove_node(node_id)
    return {"removed": node_id, "remaining_nodes": list(ring.nodes)}

@app.post("/ring/node/{node_id}")
async def add_ring_node(node_id: str):
    ring.add_node(node_id)
    return {"added": node_id, "all_nodes": list(ring.nodes)}

@app.get("/{alias}")
async def redirect(alias: str):
    url, cache_hit, node = await resolve_url(alias)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(
        url=url,
        headers={
            "X-Cache": "HIT" if cache_hit else "MISS",
            "X-Served-By": node or "unknown"
        }
    )