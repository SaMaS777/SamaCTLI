import json
from pathlib import Path

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from SamaCTLI.core.api_manager import get_api_manager
from SamaCTLI.ui import print_error, print_info, print_success

console = Console()

CONFIG_DIR = Path.home() / ".samactli"
MODELS_FILE = CONFIG_DIR / "models.json"

KNOWN_PROVIDERS = {
    "google": {
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
        "headers": {},
        "parser": "google",
    },
    "openai": {
        "url_template": "https://api.openai.com/v1/models",
        "headers": {"Authorization": "Bearer {api_key}"},
        "parser": "openai",
    },
    "nvidia": {
        "url_template": "https://integrate.api.nvidia.com/v1/models",
        "headers": {"Authorization": "Bearer {api_key}"},
        "parser": "openai",
    },
    "anthropic": {
        "url_template": None,
        "headers": {},
        "parser": "anthropic",
    },
}

ANTHROPIC_MODELS = [
    "claude-opus-4-5",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
]


def _parse_google_response(data: dict) -> list[str]:
    models = []
    for item in data.get("models", []):
        name = item.get("name", "")
        if name.startswith("models/"):
            name = name[7:]
        models.append(name)
    return models


def _parse_openai_response(data: dict) -> list[str]:
    models = []
    for item in data.get("data", []):
        model_id = item.get("id", "")
        if model_id:
            models.append(model_id)
    return models


def _get_parser(parser_name: str):
    parsers = {
        "google": _parse_google_response,
        "openai": _parse_openai_response,
        "anthropic": lambda _: ANTHROPIC_MODELS,
    }
    return parsers.get(parser_name, _parse_openai_response)


def discover_models_for_provider(provider: str, api_key: str, show_progress: bool = True) -> list[str]:
    provider_lower = provider.lower().strip()

    if provider_lower == "anthropic":
        return ANTHROPIC_MODELS

    provider_config = KNOWN_PROVIDERS.get(provider_lower)
    if not provider_config:
        provider_config = {
            "url_template": f"https://api.{provider_lower}.com/v1/models",
            "headers": {"Authorization": "Bearer {api_key}"},
            "parser": "openai",
        }

    url_template = provider_config["url_template"]
    headers_template = provider_config["headers"]
    parser_name = provider_config["parser"]

    if not url_template:
        print_error(f"No endpoint known for provider '{provider}'")
        return []

    url = url_template.format(api_key=api_key)
    headers = {}
    for k, v in headers_template.items():
        headers[k] = v.format(api_key=api_key)

    parser = _get_parser(parser_name)

    try:
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"Discovering models for {provider}...", total=None)
                response = requests.get(url, headers=headers, timeout=30)
                progress.update(task, completed=True)
        else:
            print_info(f"Discovering models for {provider}...")
            response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 401:
            print_error(f"Invalid API key for {provider}")
            return []
        if response.status_code == 429:
            print_error(f"Rate limited by {provider}. Try again later.")
            return []
        if response.status_code != 200:
            print_error(f"Failed to fetch models from {provider}: HTTP {response.status_code}")
            return []

        data = response.json()
        models = parser(data)
        return models

    except requests.exceptions.Timeout:
        print_error(f"Timeout connecting to {provider}")
        return []
    except requests.exceptions.ConnectionError:
        print_error(f"Network error connecting to {provider}")
        return []
    except json.JSONDecodeError:
        print_error(f"Invalid response from {provider}")
        return []
    except Exception as e:
        print_error(f"Unexpected error discovering models for {provider}: {e}")
        return []


def discover_all_models(show_progress: bool = True) -> dict[str, list[str]]:
    api_manager = get_api_manager()
    if not api_manager.has_keys():
        return {}

    result = {}
    for provider in api_manager.get_all_providers():
        api_key = api_manager.get_key(provider)
        if not api_key:
            continue
        models = discover_models_for_provider(provider, api_key, show_progress)
        if models:
            result[provider.lower()] = models
            if show_progress:
                print_success(f"Found {len(models)} models for {provider}")
    return result


def save_models(models: dict[str, list[str]]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        MODELS_FILE.write_text(json.dumps(models, indent=2), encoding="utf-8")
        print_success(f"Models saved to {MODELS_FILE}")
    except Exception as e:
        print_error(f"Failed to save models: {e}")


def load_models() -> dict[str, list[str]]:
    if MODELS_FILE.exists():
        try:
            return json.loads(MODELS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def get_models_for_provider(provider: str) -> list[str]:
    models = load_models()
    return models.get(provider.lower(), [])


def get_all_providers_with_models() -> dict[str, list[str]]:
    return load_models()
