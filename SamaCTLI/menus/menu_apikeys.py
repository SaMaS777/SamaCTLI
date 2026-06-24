from SamaCTLI.core.api_manager import APIKeyManager, get_api_manager
from SamaCTLI.core.model_discovery import discover_models_for_provider, load_models, save_models
from SamaCTLI.ui import (
    clear,
    print_banner,
    print_error,
    print_info,
    print_menu,
    print_success,
    print_warning,
    prompt_input,
    wait_for_enter,
)


def print_apikeys_banner() -> None:
    print_banner("API KEY MANAGEMENT", "Manage your AI provider API keys")


async def run_apikeys_menu() -> None:
    manager = get_api_manager()

    while True:
        clear()
        print_apikeys_banner()

        if manager.has_keys():
            keys = manager.list_keys()
            print_info("Saved providers:")
            for _provider, info in keys.items():
                print(f"  • {info['name']}: {info['masked_key']}")
        else:
            print_info("No API keys configured yet")

        print()
        print_menu(
            [
                ("1", "Add API Key"),
                ("2", "List Saved Providers"),
                ("3", "Delete a Provider"),
                ("4", "Re-sync Models for Provider"),
            ],
            "Back to Main Menu",
        )

        choice = prompt_input("Choose")

        if choice == "0":
            break

        elif choice == "1":
            await add_api_key(manager)

        elif choice == "2":
            list_providers(manager)

        elif choice == "3":
            await delete_provider(manager)

        elif choice == "4":
            await resync_models(manager)

        else:
            print_error("Invalid option")
            wait_for_enter()


async def add_api_key(manager: APIKeyManager) -> None:
    clear()
    print_banner("ADD API KEY", "Enter provider name and API key")

    provider = prompt_input("Provider name (e.g. Google, Nvidia, OpenAI, Anthropic)").strip()
    if not provider:
        print_error("Provider name is required")
        wait_for_enter()
        return

    api_key = prompt_input("API Key").strip()
    if not api_key:
        print_error("API Key is required")
        wait_for_enter()
        return

    if manager.add_key(provider, api_key):
        print_info("Discovering models for provider...")
        models = discover_models_for_provider(provider, api_key, show_progress=True)

        if models:
            all_models = load_models()
            all_models[provider.lower()] = models
            save_models(all_models)
            print_success(f"Discovered and saved {len(models)} models for {provider}")
        else:
            print_warning("No models discovered. You can re-sync later from option [4]")

        wait_for_enter()


def list_providers(manager: APIKeyManager) -> None:
    clear()
    print_banner("SAVED PROVIDERS")

    if not manager.has_keys():
        print_info("No API keys configured")
    else:
        keys = manager.list_keys()
        for i, (_provider, info) in enumerate(keys.items(), 1):
            print(f"  [{i}] {info['name']}: {info['masked_key']}")

    wait_for_enter()


async def delete_provider(manager: APIKeyManager) -> None:
    clear()
    print_banner("DELETE PROVIDER", "Select a provider to remove")

    if not manager.has_keys():
        print_info("No API keys configured")
        wait_for_enter()
        return

    keys = manager.list_keys()
    providers = list(keys.items())

    for i, (provider, info) in enumerate(providers, 1):
        print(f"  [{i}] {info['name']}: {info['masked_key']}")
    print("  [0] Cancel")

    choice = prompt_input("Choose provider to delete")

    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if not 0 <= idx < len(providers):
            print_error("Invalid selection")
            wait_for_enter()
            return
    except ValueError:
        print_error("Invalid input")
        wait_for_enter()
        return

    provider, info = providers[idx]
    confirm = prompt_input(f"Delete '{info['name']}'? [y/N]").strip().lower()

    if confirm == "y":
        manager.delete_key(provider)

        models = load_models()
        if provider.lower() in models:
            del models[provider.lower()]
            save_models(models)
            print_success(f"Removed models for {provider}")

        wait_for_enter()


async def resync_models(manager: APIKeyManager) -> None:
    clear()
    print_banner("RE-SYNC MODELS", "Select a provider to re-discover models")

    if not manager.has_keys():
        print_info("No API keys configured")
        wait_for_enter()
        return

    keys = manager.list_keys()
    providers = list(keys.items())

    for i, (_provider, info) in enumerate(providers, 1):
        print(f"  [{i}] {info['name']}: {info['masked_key']}")
    print("  [0] Cancel")

    choice = prompt_input("Choose provider to re-sync")

    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if not 0 <= idx < len(providers):
            print_error("Invalid selection")
            wait_for_enter()
            return
    except ValueError:
        print_error("Invalid input")
        wait_for_enter()
        return

    provider, info = providers[idx]
    api_key = manager.get_key(provider)

    if not api_key:
        print_error(f"Failed to retrieve API key for {provider}")
        wait_for_enter()
        return

    print_info(f"Re-discovering models for {provider}...")
    models = discover_models_for_provider(provider, api_key, show_progress=True)

    if models:
        from SamaCTLI.core.model_discovery import load_models, save_models
        all_models = load_models()
        all_models[provider.lower()] = models
        save_models(all_models)
        print_success(f"Re-discovered and saved {len(models)} models for {provider}")
    else:
        print_error("Failed to discover models")

    wait_for_enter()
