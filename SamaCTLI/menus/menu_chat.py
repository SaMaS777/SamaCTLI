from SamaCTLI.core.ai_session import run_chat_session


async def run_model_chat(
    provider: str,
    model: str,
    api_key: str,
    base_url: str | None = None,
) -> None:
    await run_chat_session(provider, model, api_key, base_url)
