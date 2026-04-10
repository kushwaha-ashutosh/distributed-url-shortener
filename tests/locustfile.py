from locust import HttpUser, task, between
import random

EXISTING_ALIASES = [
    "hOpPJPx", "gX50Mqn", "e81G6l6", "esnOZMN", "cqBlEwZ"
]
class URLShortenerUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def redirect_url(self):
        alias = random.choice(EXISTING_ALIASES)
        with self.client.get(
            f"/{alias}",
            allow_redirects=False,
            catch_response=True
        ) as response:
            if response.status_code in [307, 308, 301, 302]:
                response.success()

    @task(1)
    def shorten_url(self):
        n = random.randint(1, 10000)
        self.client.post(
            "/shorten",
            json={"original_url": f"https://example.com/page{n}"},
        )

    @task(2)
    def health_check(self):
        self.client.get("/health")