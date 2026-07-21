from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = ""
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "alerts@yourcompany.com"
    database_url: str = "sqlite:///./regulatory_monitor.db"
    federal_register_base_url: str = "https://www.federalregister.gov/api/v1"
    api_key: str = ""
    allowed_source_hosts: str = "www.federalregister.gov"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
