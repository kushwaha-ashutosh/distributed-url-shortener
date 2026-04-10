from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "urlshortener"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ttl: int = 600
    base_url: str = "http://localhost:8000"
    app_port: int = 8000
    instance_id: str = "instance-1"

    class Config:
        env_file = ".env"

settings = Settings()