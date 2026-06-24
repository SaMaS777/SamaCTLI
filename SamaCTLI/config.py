import json
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RoleConfig(BaseSettings):
    name: str
    model: str
    system_prompt: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nvidia_api_key: str = Field(default="", description="NVIDIA API Key")
    base_url: str = Field(default="https://integrate.api.nvidia.com/v1", description="OpenAI-compatible base URL")
    roles: dict[str, RoleConfig] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _load_roles(self) -> "Settings":
        config_path = Path(__file__).parent.parent / "ai_config.json"
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for key, role_data in data.get("roles", {}).items():
                        self.roles[key] = RoleConfig(**role_data)
            except (OSError, json.JSONDecodeError):
                pass
        return self


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
