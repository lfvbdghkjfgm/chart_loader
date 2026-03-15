from __future__ import annotations

import json
import os
from pathlib import Path

APP_NAME = "ChartLoader"
CONFIG_FILE = "config.json"
LOG_DIR = "logs"

DEFAULT_CONFIG = {
    "default_directory": "",
    "last_icao": "",
}


def get_app_data_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        base = Path(appdata)
    else:
        base = Path.home() / "AppData" / "Roaming"
    primary_path = base / APP_NAME
    try:
        primary_path.mkdir(parents=True, exist_ok=True)
        return primary_path
    except OSError:
        fallback = Path.cwd() / ".chart_loader_data"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def get_config_path() -> Path:
    return get_app_data_dir() / CONFIG_FILE


def get_logs_dir() -> Path:
    logs_dir = get_app_data_dir() / LOG_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def load_config() -> dict[str, str]:
    config_path = get_config_path()
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()

    result = DEFAULT_CONFIG.copy()
    result.update({k: str(v) for k, v in data.items() if k in DEFAULT_CONFIG})
    return result


def save_config(config: dict[str, str]) -> None:
    data = DEFAULT_CONFIG.copy()
    data.update(config)
    config_path = get_config_path()
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_default_directory() -> str:
    return load_config().get("default_directory", "").strip()


def set_default_directory(directory: str) -> None:
    config = load_config()
    config["default_directory"] = directory.strip()
    save_config(config)


def clear_default_directory() -> None:
    config = load_config()
    config["default_directory"] = ""
    save_config(config)


def get_last_icao() -> str:
    return load_config().get("last_icao", "").strip().upper()


def set_last_icao(icao: str) -> None:
    config = load_config()
    config["last_icao"] = icao.strip().upper()
    save_config(config)
