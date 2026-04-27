import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    ha_url: str
    ha_token: str
    anthropic_api_key: str
    picovoice_access_key: str
    host: str
    port: int


def get_settings() -> Settings:
    ha_url = os.getenv("HA_URL", "").rstrip("/")
    ha_token = os.getenv("HA_TOKEN", "")
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    missing = [name for name, val in [("HA_URL", ha_url), ("HA_TOKEN", ha_token), ("ANTHROPIC_API_KEY", api_key)] if not val]
    if missing:
        raise RuntimeError(
            f"Missing required .env variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in the values."
        )

    return Settings(
        ha_url=ha_url,
        ha_token=ha_token,
        anthropic_api_key=api_key,
        picovoice_access_key=os.getenv("PICOVOICE_ACCESS_KEY", ""),
        host=os.getenv("JARVIS_HOST", "0.0.0.0"),
        port=int(os.getenv("JARVIS_PORT", "8000")),
    )
