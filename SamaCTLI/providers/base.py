from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ModelInfo:
    id: str
    name: str
    description: str = ""
    context_window: int | None = None
    supports_streaming: bool = True
    supports_tools: bool = False


class Provider(ABC):
    name: str
    base_url: str
    models_url: str = "/v1/models"
    requires_api_key: bool = True

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url or self.base_url

    @abstractmethod
    async def fetch_models(self) -> list[ModelInfo]:
        pass

    @abstractmethod
    def create_client(self) -> Any:
        pass

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_models_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.models_url}"
