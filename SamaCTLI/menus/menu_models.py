from SamaCTLI.core.api_manager import get_api_manager
from SamaCTLI.core.model_discovery import load_models
from SamaCTLI.menus.menu_chat import run_model_chat
from SamaCTLI.ui import (
    clear,
    print_banner,
    print_error,
    print_info,
    print_warning,
    prompt_input,
    wait_for_enter,
)


def print_models_banner() -> None:
    print_banner("AI MODELS", "Select a provider and model to chat with")


async def run_models_menu() -> None:
    api_manager = get_api_manager()

    while True:
        clear()
        print_models_banner()

        if not api_manager.has_keys():
            print_error("No API keys configured. Go to [A] API Keys to add one first.")
            wait_for_enter()
            return

        models_data = load_models()

        if not models_data:
            print_warning("No models discovered yet. Go to [A] API Keys → [4] Re-sync Models")
            wait_for_enter()
            return

        providers = list(models_data.items())

        print_info(f"Found {len(providers)} provider(s) with models:")
        for i, (provider, models) in enumerate(providers, 1):
            print(f"  [{i}] {provider.capitalize()} ({len(models)} models)")
        print("  [0] Back to Main Menu")

        choice = prompt_input("Choose provider")

        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(providers):
                print_error("Invalid selection")
                wait_for_enter()
                continue
        except ValueError:
            print_error("Invalid input")
            wait_for_enter()
            continue

        provider, models = providers[idx]
        await select_model(provider, models)


async def select_model(provider: str, models: list[str]) -> None:
    api_manager = get_api_manager()

    while True:
        clear()
        print_banner(f"MODELS: {provider.upper()}", "Select a model to chat with")

        for i, model in enumerate(models, 1):
            print(f"  [{i}] {model}")
        print("  [0] Back to Providers")

        choice = prompt_input("Choose model")

        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(models):
                print_error("Invalid selection")
                wait_for_enter()
                continue
        except ValueError:
            print_error("Invalid input")
            wait_for_enter()
            continue

        model = models[idx]
        api_key = api_manager.get_key(provider)

        if not api_key:
            print_error(f"Failed to retrieve API key for {provider}")
            wait_for_enter()
            continue

        base_url = get_base_url_for_provider(provider)
        await run_model_chat(provider, model, api_key, base_url)
        break


def get_base_url_for_provider(provider: str) -> str | None:
    urls = {
        "google": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "openai": "https://api.openai.com/v1",
        "nvidia": "https://integrate.api.nvidia.com/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }
    return urls.get(provider.lower())
