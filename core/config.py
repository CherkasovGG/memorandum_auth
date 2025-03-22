import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


load_dotenv(override=True)


DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
API_HOST: str = os.environ.get("APP_HOST", "0.0.0.0")
API_PORT: int = int(os.environ.get("APP_PORT", "8000"))
DB_URL: str = os.environ.get("DB_URL")
JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certifications" / "jwt-private.key"
    public_key_path: Path = BASE_DIR / "certifications" / "jwt-public.key"
    algorithm: str = "RS256"
    access_token_exipre_minutes: int = 300_000


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
