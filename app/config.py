import json
import os
from pathlib import Path

APP_NAME = "SA_R2_Downloader"


def get_appdata_dir() -> Path:
    base = Path(os.getenv("APPDATA"))
    app_dir = base / APP_NAME
    app_dir.mkdir(exist_ok=True)
    return app_dir


def get_config_path() -> Path:
    return get_appdata_dir() / "config.json"


def load_config() -> dict | None:
    path = get_config_path()
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(config: dict):
    path = get_config_path()
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
