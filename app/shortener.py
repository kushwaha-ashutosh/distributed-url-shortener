import hashlib
import string
from datetime import datetime
from app.database import get_db
from app.cache import get_cached, set_cached
from app.config import settings
from app.consistent_hashing import ring, init_ring

BASE62 = string.ascii_letters + string.digits

def encode_base62(num: int, length: int = 7) -> str:
    chars = []
    while num:
        chars.append(BASE62[num % 62])
        num //= 62
    return ''.join(reversed(chars)).zfill(length)

def generate_alias(url: str) -> str:
    hash_int = int(hashlib.md5(url.encode()).hexdigest(), 16)
    return encode_base62(hash_int)[:7]

async def create_short_url(original_url: str, custom_alias: str = None):
    db = get_db()
    alias = custom_alias or generate_alias(original_url)

    # Use consistent hashing to determine responsible node
    responsible_node = ring.get_node(alias)

    existing = await db.urls.find_one({"alias": alias})
    if existing:
        return alias, responsible_node

    record = {
        "alias": alias,
        "original_url": original_url,
        "clicks": 0,
        "created_at": datetime.utcnow(),
        "served_by": responsible_node
    }
    await db.urls.insert_one(record)
    await set_cached(alias, original_url)
    return alias, responsible_node

async def resolve_url(alias: str):
    # Cache-aside: check Redis first
    cached = await get_cached(alias)
    if cached:
        return cached, True, ring.get_node(alias)

    # Cache miss: go to MongoDB
    db = get_db()
    record = await db.urls.find_one({"alias": alias})
    if not record:
        return None, False, None

    await set_cached(alias, record["original_url"])
    return record["original_url"], False, ring.get_node(alias)