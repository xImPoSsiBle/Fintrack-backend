from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings

class CsrfSettings(BaseSettings):
    secret_key: str
    cookie_samesite: str = 'lax'
    token_location: str = 'header'


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    cookie_secure: bool
    csrf_secret_key: str
    json_logs: bool = True
    sql_echo: bool

    class Config:
        env_file = '.env'

settings = Settings()

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings(secret_key=settings.csrf_secret_key)