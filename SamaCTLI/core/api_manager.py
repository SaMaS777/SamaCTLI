import base64
import json
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from SamaCTLI.ui import print_error, print_success

CONFIG_DIR = Path.home() / ".samactli"
API_KEYS_FILE = CONFIG_DIR / "api_keys.enc"
SALT_FILE = CONFIG_DIR / ".salt"
MASTER_KEY_FILE = CONFIG_DIR / ".master"


def _get_or_create_salt() -> bytes:
    if SALT_FILE.exists():
        return SALT_FILE.read_bytes()
    salt = os.urandom(16)
    SALT_FILE.write_bytes(salt)
    return salt


def _get_or_create_master_key() -> bytes:
    if MASTER_KEY_FILE.exists():
        return MASTER_KEY_FILE.read_bytes()
    master_key = os.urandom(32)
    MASTER_KEY_FILE.write_bytes(master_key)
    return master_key


def _derive_key(salt: bytes, master_key: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(master_key)


def _get_fernet() -> Fernet:
    salt = _get_or_create_salt()
    master_key = _get_or_create_master_key()
    key = _derive_key(salt, master_key)
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


class APIKeyManager:
    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._fernet = _get_fernet()
        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if API_KEYS_FILE.exists():
            try:
                encrypted = API_KEYS_FILE.read_bytes()
                decrypted = self._fernet.decrypt(encrypted)
                self._data = json.loads(decrypted.decode())
            except Exception as e:
                print_error(f"Failed to load API keys: {e}")
                self._data = {}

    def _save(self) -> None:
        try:
            encrypted = self._fernet.encrypt(json.dumps(self._data).encode())
            API_KEYS_FILE.write_bytes(encrypted)
        except Exception as e:
            print_error(f"Failed to save API keys: {e}")

    def add_key(self, provider: str, api_key: str) -> bool:
        provider_lower = provider.lower().strip()
        if provider_lower in self._data:
            print_error(f"Provider '{provider}' already exists. Delete it first.")
            return False

        self._data[provider_lower] = {
            "name": provider.strip(),
            "key": api_key.strip(),
        }
        self._save()
        print_success(f"API key for '{provider}' saved and encrypted")
        return True

    def list_keys(self) -> dict[str, dict[str, Any]]:
        result = {}
        for provider, info in self._data.items():
            result[provider] = {
                "name": info["name"],
                "masked_key": _mask_key(info["key"]),
            }
        return result

    def get_key(self, provider: str) -> str | None:
        provider_lower = provider.lower().strip()
        info = self._data.get(provider_lower)
        if info:
            return info["key"]
        return None

    def delete_key(self, provider: str) -> bool:
        provider_lower = provider.lower().strip()
        if provider_lower in self._data:
            del self._data[provider_lower]
            self._save()
            print_success(f"API key for '{provider}' deleted")
            return True
        print_error(f"Provider '{provider}' not found")
        return False

    def has_keys(self) -> bool:
        return len(self._data) > 0

    def get_all_providers(self) -> list[str]:
        return [info["name"] for info in self._data.values()]


_api_manager: APIKeyManager | None = None


def get_api_manager() -> APIKeyManager:
    global _api_manager
    if _api_manager is None:
        _api_manager = APIKeyManager()
    return _api_manager
