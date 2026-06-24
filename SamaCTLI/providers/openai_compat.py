
import httpx
from openai import AsyncOpenAI

from SamaCTLI.providers.base import ModelInfo, Provider


class OpenAICompatibleProvider(Provider):
    name = "openai_compat"
    base_url = "https://api.openai.com/v1"
    models_url = "/models"

    # Known model mappings for providers that don't expose /models
    KNOWN_MODELS: dict[str, list[ModelInfo]] = {
        "openai": [
            ModelInfo(id="gpt-4o", name="GPT-4o", description="Latest GPT-4 omni model"),
            ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", description="Faster, cheaper GPT-4o"),
            ModelInfo(id="gpt-4-turbo", name="GPT-4 Turbo", description="GPT-4 with 128k context"),
            ModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", description="Fast, cost-effective"),
        ],
        "nvidia": [
            ModelInfo(id="deepseek-ai/deepseek-v4-pro", name="DeepSeek V4 Pro", description="Expert coding model"),
            ModelInfo(id="moonshotai/kimi-k2.6", name="Kimi K2.6", description="General assistant"),
            ModelInfo(id="mistralai/mistral-medium-3.5-128b", name="Mistral Medium 3.5", description="Pentesting & analysis"),
            ModelInfo(id="nvidia/nemotron-3-ultra", name="Nemotron 3 Ultra", description="NVIDIA's flagship"),
            ModelInfo(id="meta/llama-3.1-405b-instruct", name="Llama 3.1 405B", description="Largest open model"),
        ],
        "groq": [
            ModelInfo(id="llama-3.1-70b-versatile", name="Llama 3.1 70B", description="Fast inference"),
            ModelInfo(id="llama-3.1-8b-instant", name="Llama 3.1 8B", description="Ultra fast"),
            ModelInfo(id="mixtral-8x7b-32768", name="Mixtral 8x7B", description="MoE model"),
            ModelInfo(id="gemma2-9b-it", name="Gemma 2 9B", description="Google's model"),
        ],
        "together": [
            ModelInfo(id="meta-llama/Llama-3.1-405B-Instruct-Turbo", name="Llama 3.1 405B", description="Largest open model"),
            ModelInfo(id="meta-llama/Llama-3.1-70B-Instruct-Turbo", name="Llama 3.1 70B", description="Balanced"),
            ModelInfo(id="mistralai/Mixtral-8x7B-Instruct-v0.1", name="Mixtral 8x7B", description="MoE"),
            ModelInfo(id="Qwen/Qwen2.5-72B-Instruct-Turbo", name="Qwen 2.5 72B", description="Alibaba's model"),
        ],
        "anthropic": [
            ModelInfo(id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet", description="Best for coding"),
            ModelInfo(id="claude-3-5-haiku-20241022", name="Claude 3.5 Haiku", description="Fast & smart"),
            ModelInfo(id="claude-3-opus-20240229", name="Claude 3 Opus", description="Most capable"),
        ],
        "google": [
            ModelInfo(id="gemini-1.5-pro", name="Gemini 1.5 Pro", description="Large context window"),
            ModelInfo(id="gemini-1.5-flash", name="Gemini 1.5 Flash", description="Fast & efficient"),
            ModelInfo(id="gemini-1.0-pro", name="Gemini 1.0 Pro", description="Balanced"),
        ],
    }

    PROVIDER_PRESETS = {
        "openai": {"base_url": "https://api.openai.com/v1", "name": "OpenAI"},
        "nvidia": {"base_url": "https://integrate.api.nvidia.com/v1", "name": "NVIDIA"},
        "groq": {"base_url": "https://api.groq.com/openai/v1", "name": "Groq"},
        "together": {"base_url": "https://api.together.xyz/v1", "name": "Together AI"},
        "anthropic": {"base_url": "https://api.anthropic.com/v1", "name": "Anthropic (OpenAI compat)"},
        "google": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "name": "Google (OpenAI compat)"},
        "custom": {"base_url": "", "name": "Custom OpenAI-Compatible"},
    }

    async def fetch_models(self) -> list[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    self.get_models_endpoint(),
                    headers=self.get_headers(),
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return self._parse_models_response(data)
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            pass

        return self._get_fallback_models()

    def _parse_models_response(self, data: dict) -> list[ModelInfo]:
        models = []
        for item in data.get("data", []):
            model_id = item.get("id", "")
            if model_id:
                models.append(ModelInfo(
                    id=model_id,
                    name=model_id,
                    description=item.get("description", ""),
                    context_window=item.get("context_window"),
                ))
        return models

    def _get_fallback_models(self) -> list[ModelInfo]:
        for key, models in self.KNOWN_MODELS.items():
            if key in self.base_url.lower():
                return models
        return [ModelInfo(id="unknown", name="Unknown Model", description="Could not fetch models")]

    def create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    @classmethod
    def get_presets(cls) -> dict[str, dict]:
        return cls.PROVIDER_PRESETS
