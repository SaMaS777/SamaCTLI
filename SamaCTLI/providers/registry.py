import json
from pathlib import Path

from SamaCTLI.providers.base import ModelInfo, Provider
from SamaCTLI.providers.openai_compat import OpenAICompatibleProvider
from SamaCTLI.ui import print_error, print_success

CONFIG_DIR = Path.home() / ".config" / "samactli"
CONFIG_FILE = CONFIG_DIR / "providers.json"


class ProviderConfig:
    def __init__(self, provider_id: str, name: str, base_url: str, api_key: str) -> None:
        self.provider_id = provider_id
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self._models: list[ModelInfo] | None = None
        self._provider: Provider | None = None

    def to_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "base_url": self.base_url,
            "api_key": self.api_key,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProviderConfig":
        return cls(
            provider_id=data["provider_id"],
            name=data["name"],
            base_url=data["base_url"],
            api_key=data["api_key"],
        )

    def create_provider(self) -> Provider:
        if self._provider is None:
            self._provider = OpenAICompatibleProvider(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._provider

    async def get_models(self) -> list[ModelInfo]:
        if self._models is None:
            provider = self.create_provider()
            self._models = await provider.fetch_models()
        return self._models

    def invalidate_models(self) -> None:
        self._models = None


class ProviderRegistry:
    def __init__(self) -> None:
        self.configs: dict[str, ProviderConfig] = {}
        self._load()

    def _load(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                for item in data.get("providers", []):
                    config = ProviderConfig.from_dict(item)
                    self.configs[config.provider_id] = config
            except Exception as e:
                print_error(f"Failed to load provider config: {e}")

    def _save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {"providers": [c.to_dict() for c in self.configs.values()]}
        CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_provider(self, provider_id: str, name: str, base_url: str, api_key: str) -> bool:
        if provider_id in self.configs:
            print_error(f"Provider '{provider_id}' already exists")
            return False
        config = ProviderConfig(provider_id, name, base_url, api_key)
        self.configs[provider_id] = config
        self._save()
        print_success(f"Provider '{name}' added")
        return True

    def remove_provider(self, provider_id: str) -> bool:
        if provider_id in self.configs:
            del self.configs[provider_id]
            self._save()
            print_success("Provider removed")
            return True
        return False

    def get_provider(self, provider_id: str) -> ProviderConfig | None:
        return self.configs.get(provider_id)

    def list_providers(self) -> list[ProviderConfig]:
        return list(self.configs.values())

    def has_providers(self) -> bool:
        return len(self.configs) > 0

    async def get_all_models(self) -> dict[str, list[ModelInfo]]:
        result = {}
        for provider_id, config in self.configs.items():
            try:
                models = await config.get_models()
                result[provider_id] = models
            except Exception as e:
                print_error(f"Failed to fetch models for {provider_id}: {e}")
                result[provider_id] = []
        return result


_registry: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry
