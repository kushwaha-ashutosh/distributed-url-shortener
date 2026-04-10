from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Counters
requests_total = Counter(
    'urlshortener_requests_total',
    'Total requests',
    ['endpoint', 'instance']
)

cache_hits = Counter(
    'urlshortener_cache_hits_total',
    'Redis cache hits',
    ['instance']
)

cache_misses = Counter(
    'urlshortener_cache_misses_total',
    'Redis cache misses',
    ['instance']
)

urls_created = Counter(
    'urlshortener_urls_created_total',
    'Total URLs shortened',
    ['instance']
)

# Histograms
request_latency = Histogram(
    'urlshortener_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint', 'instance'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Gauges
active_nodes = Gauge(
    'urlshortener_active_ring_nodes',
    'Number of active nodes in consistent hash ring'
)

def metrics_endpoint():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)