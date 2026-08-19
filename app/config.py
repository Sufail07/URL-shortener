from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    shorten_rate_limit: str = "10/minute"
    redirect_rate_limit: str = "60/minute"
    rate_limit_storage: str = "memory://"
    model_config = {"env_file": ".env"}

settings = Settings()