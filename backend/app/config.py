from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SICC API"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_db: str = "sicc_central"
    pg_user: str = "sicc_api"
    pg_password: str = "sicc_api_pass_2024"

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "sicc_cochabamba"
    mysql_user: str = "sicc_api"
    mysql_password: str = "sicc_api_pass_2024"
    # False: PyMySQL no intenta TLS (MySQL Docker / Tailscale sin SSL). True: negociar con el servidor.
    mysql_ssl: bool = False

    sede_central_id: int = 1
    sede_secundaria_id: int = 2
    rol_admin_nombre: str = "Administrador"
    reportes_cache_ttl_seconds: int = 300

    mongo_sc_host: str = "localhost"
    mongo_sc_port: int = 27017
    mongo_sc_db: str = "sicc_sc"
    mongo_sc_user: str = "sicc_mongo_api"
    mongo_sc_password: str = "sicc_mongo_api_pass_2024"

    mongo_cb_host: str = "localhost"
    mongo_cb_port: int = 27018
    mongo_cb_db: str = "sicc_cb"
    mongo_cb_user: str = "sicc_mongo_api"
    mongo_cb_password: str = "sicc_mongo_api_pass_2024"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
