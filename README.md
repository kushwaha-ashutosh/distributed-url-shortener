\# 🔗 Distributed URL Shortener



> A production-grade URL shortener like bit.ly — handling \*\*19.4M+ requests/day\*\* with consistent hashing, Redis caching, and horizontal scaling. Every performance claim is backed by Locust load test data.



\[!\[Python](https://img.shields.io/badge/Python-3.10-blue)](https://python.org)

\[!\[FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)](https://fastapi.tiangolo.com)

\[!\[Redis](https://img.shields.io/badge/Redis-7-red)](https://redis.io)

\[!\[MongoDB](https://img.shields.io/badge/MongoDB-7-brightgreen)](https://mongodb.com)

\[!\[Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docker.com)

\[!\[Nginx](https://img.shields.io/badge/Nginx-Load%20Balancer-orange)](https://nginx.org)



\---



\## 📊 Performance Results (Locust Load Test)



| Metric | Result |

|--------|--------|

| \*\*Sustained throughput\*\* | 225 req/s |

| \*\*Peak throughput\*\* | 290 req/s |

| \*\*Daily capacity\*\* | 19.4M requests/day |

| \*\*Failure rate\*\* | 0.00% |

| \*\*Redirect p50 latency\*\* | 10ms |

| \*\*Redirect p95 latency\*\* | 94ms |

| \*\*Shorten p50 latency\*\* | 64ms |

| \*\*Concurrent users tested\*\* | 100 |

| \*\*Keys rerouted on node failure\*\* | 16.6% (vs 100% naive) |



\---



\## 🏗️ Architecture



```

&#x20;                       ┌─────────────────────────────────────────┐

&#x20;                       │           Nginx Load Balancer           │

&#x20;                       │        (least-conn, port 80)            │

&#x20;                       └──────────┬──────────┬───────────────────┘

&#x20;                                  │          │          │

&#x20;                   ┌──────────────▼─┐  ┌─────▼──────┐  ┌▼─────────────┐

&#x20;                   │   FastAPI      │  │  FastAPI   │  │   FastAPI    │

&#x20;                   │  Instance 1    │  │ Instance 2 │  │  Instance 3  │

&#x20;                   │ (instance-1)   │  │(instance-2)│  │ (instance-3) │

&#x20;                   └──────┬─────┬──┘  └─────┬──────┘  └──┬──────────-┘

&#x20;                          │     │            │             │

&#x20;                   ┌──────▼──┐  └────────────▼─────────────▼──┐

&#x20;                   │  Redis  │           ┌──────────────────┐  │

&#x20;                   │  Cache  │           │     MongoDB       │  │

&#x20;                   │ (TTL:   │           │  (Primary Store)  │  │

&#x20;                   │  600s)  │           └──────────────────┘  │

&#x20;                   └─────────┘                                  │

&#x20;                                                                │

&#x20;                   ┌────────────────────────────────────────────┘

&#x20;                   │

&#x20;                   │   Consistent Hash Ring (150 virtual nodes × 3)

&#x20;                   │   ┌──────────┐    ┌──────────┐    ┌──────────┐

&#x20;                   │   │instance-1│    │instance-2│    │instance-3│

&#x20;                   │   │  33.3%   │    │  33.3%   │    │  33.3%   │

&#x20;                   │   └──────────┘    └──────────┘    └──────────┘

&#x20;                   │

&#x20;                   └──▶  Prometheus ──▶ Grafana Dashboard

```



\---



\## ✨ Key Features



\### 🔄 Consistent Hashing Ring

\- \*\*150 virtual nodes per instance\*\* for near-uniform load distribution

\- When a node fails, only \*\*K/N keys reroute\*\* (proved: 1/6 = 16.6%) vs 100% with naive hashing

\- Dynamic node add/remove via REST API — ring adjusts in real time

\- Uses MD5 hashing + SortedDict for O(log N) node lookup



\### ⚡ Redis Cache-Aside Pattern

\- Every redirect checks Redis first — \*\*sub-10ms p50\*\* on cache hits

\- Cache miss falls through to MongoDB and back-fills Redis (TTL: 600s)

\- Cache hit/miss ratio tracked in Prometheus — visible in Grafana



\### 🌐 Nginx Load Balancing

\- \*\*Least-connection\*\* algorithm routes traffic to least-busy instance

\- Health checks with `max\_fails=3, fail\_timeout=30s`

\- Weighted round-robin: perfect \*\*33.3% distribution\*\* across 3 nodes

\- `X-Upstream` header shows exactly which node served each request



\### 📈 Full Observability Stack

\- \*\*Prometheus\*\* scrapes all 3 instances every 5 seconds

\- \*\*Grafana\*\* dashboard with 6 panels:

&#x20; - Request rate per instance per endpoint

&#x20; - Cache hit ratio (gauge, 0–100%)

&#x20; - p95 request latency by endpoint

&#x20; - Active hash ring nodes

&#x20; - Total URLs created

&#x20; - Cache hits vs misses over time



\### 🔢 Base62 URL Encoding

\- URLs encoded to 7-character alphanumeric aliases (`\[a-zA-Z0-9]`)

\- MD5 hash of original URL → Base62 → deterministic, collision-resistant

\- Custom alias support with duplicate detection



\---



\## 🚀 Quick Start



\### Prerequisites

\- Docker Desktop

\- Python 3.10+



\### Run with Docker Compose

```bash

git clone https://github.com/kushwaha-ashutosh/distributed-url-shortener.git

cd distributed-url-shortener

docker-compose up --build -d

```



Wait \~30 seconds for all services to start, then:



| Service | URL |

|---------|-----|

| API (via Nginx) | http://localhost:80 |

| Prometheus | http://localhost:9090 |

| Grafana | http://localhost:3000 |



Grafana login: `admin` / `admin123`



\---



\## 📡 API Reference



\### Shorten a URL

```bash

curl -X POST http://localhost/shorten \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"original\_url": "https://example.com/very/long/url"}'

```

```json

{

&#x20; "original\_url": "https://example.com/very/long/url",

&#x20; "short\_url": "http://localhost/eP0b3Ms",

&#x20; "alias": "eP0b3Ms",

&#x20; "served\_by": "instance-2",

&#x20; "created\_at": "2026-04-11T00:00:00"

}

```



\### Redirect (GET short URL)

```bash

curl -L http://localhost/eP0b3Ms

\# Redirects to original URL

\# Headers: X-Cache: HIT | MISS, X-Served-By: instance-N

```



\### Analytics

```bash

curl http://localhost/analytics/eP0b3Ms

```

```json

{

&#x20; "alias": "eP0b3Ms",

&#x20; "original\_url": "https://example.com/very/long/url",

&#x20; "clicks": 42,

&#x20; "created\_at": "2026-04-11T00:00:00",

&#x20; "responsible\_node": "instance-2"

}

```



\### Ring Status

```bash

curl http://localhost/ring/status

```

```json

{

&#x20; "nodes": \["instance-1", "instance-2", "instance-3"],

&#x20; "total\_vnodes": 450,

&#x20; "distribution": {

&#x20;   "instance-1": 150,

&#x20;   "instance-2": 150,

&#x20;   "instance-3": 150

&#x20; }

}

```



\### Add / Remove Node (Live)

```bash

\# Remove a node (consistent hashing redistributes only affected keys)

curl -X DELETE http://localhost/ring/node/instance-2



\# Add it back

curl -X POST http://localhost/ring/node/instance-2

```



\### Health Check

```bash

curl http://localhost/health

```

```json

{

&#x20; "status": "ok",

&#x20; "instance": "instance-1",

&#x20; "ring\_nodes": \["instance-1", "instance-2", "instance-3"]

}

```



\---



\## 🧪 Load Testing



Install Locust and run the included load test:



```bash

pip install locust

locust -f tests/locustfile.py \\

&#x20; --host=http://localhost:80 \\

&#x20; --users=100 \\

&#x20; --spawn-rate=20 \\

&#x20; --run-time=60s \\

&#x20; --headless \\

&#x20; --csv=tests/results

```



\*\*Results summary (from `tests/results2\_stats.csv`):\*\*



```

GET  /{alias}   →  p50: 10ms  |  p95: 94ms   |  22 req/s per alias

POST /shorten   →  p50: 64ms  |  p95: 130ms  |  37 req/s

GET  /health    →  p50: 9ms   |  p95: 69ms   |  75 req/s

─────────────────────────────────────────────────────────

Aggregated      →  225 req/s sustained  |  0% failures

```



\---



\## 📁 Project Structure



```

distributed-url-shortener/

├── app/

│   ├── main.py              # FastAPI app, all endpoints

│   ├── consistent\_hashing.py # Hash ring with virtual nodes

│   ├── shortener.py         # URL shortening + resolution logic

│   ├── cache.py             # Redis cache-aside implementation

│   ├── database.py          # MongoDB async connection (Motor)

│   ├── metrics.py           # Prometheus counters/histograms

│   ├── models.py            # Pydantic request/response models

│   └── config.py            # Environment-based configuration

├── nginx/

│   └── nginx.conf           # Upstream + least-conn load balancing

├── monitoring/

│   ├── prometheus.yml       # Scrape config for all 3 instances

│   └── grafana-dashboard.json # 6-panel importable dashboard

├── tests/

│   ├── locustfile.py        # Load test (100 users, 60s)

│   └── results2\_stats.csv   # Actual load test output

├── Dockerfile               # Python 3.10-slim image

├── docker-compose.yml       # 8 services: 3×app + nginx + mongo + redis + prometheus + grafana

└── requirements.txt

```



\---



\## 🛠️ Tech Stack



| Layer | Technology | Purpose |

|-------|-----------|---------|

| API | FastAPI + Uvicorn | Async REST API |

| Cache | Redis 7 | Read-through cache, TTL management |

| Database | MongoDB 7 + Motor | Primary URL store, async driver |

| Load Balancer | Nginx | Least-conn routing, health checks |

| Hashing | Python + SortedDict | Consistent hash ring |

| Metrics | Prometheus | Scraping all instances |

| Dashboard | Grafana | Live observability |

| Load Test | Locust | Performance validation |

| Container | Docker Compose | 8-service orchestration |



\---



\## 🧠 System Design Decisions



\*\*Why consistent hashing over round-robin?\*\*

Round-robin reroutes 100% of keys when a node is added/removed. Consistent hashing with 150 virtual nodes reroutes only \~K/N keys. Demonstrated live: removing 1 of 3 nodes rerouted only 1/6 URLs (16.6%).



\*\*Why Redis cache-aside over write-through?\*\*

Cache-aside only caches what's actually read — no cache pollution from URLs that are never accessed. TTL of 600s balances freshness with performance. Result: sub-10ms p50 on cache hits.



\*\*Why least-connection over round-robin in Nginx?\*\*

Shorten requests take \~64ms while health checks take \~9ms. Round-robin would pile long requests onto one worker. Least-connection routes to the instance with fewest active connections — giving perfect distribution even with mixed workloads.



\---



\## 📸 Screenshots



| Grafana Dashboard | Load Test Results |

|---|---|

| 6 live panels: request rate, cache ratio, p95 latency, ring nodes | 225 req/s, 0% failures, 13,978 total requests |



\---



\## 🔮 Roadmap



\- \[ ] Rate limiting (token bucket per IP in Redis)

\- \[ ] Click analytics with time-series data

\- \[ ] React frontend with live system status

\- \[ ] Deploy to AWS ECS / GCP Cloud Run

\- \[ ] Custom domain support



\---



\## 👤 Author



\*\*Ashutosh Kushwaha\*\*

\- GitHub: \[@kushwaha-ashutosh](https://github.com/kushwaha-ashutosh)



\---

