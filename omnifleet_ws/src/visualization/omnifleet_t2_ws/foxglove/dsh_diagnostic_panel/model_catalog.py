"""Read the provider model catalog without exposing its credential."""
import json
import re
import time
import urllib.request
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = json.loads((HERE / "qwen-policy.json").read_text())["model"]
CACHE = Path.home() / ".local/share/omnifleet_t2/diagnostic-models.json"
MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
NON_CHAT = ("audio", "tts", "realtime", "image", "embedding", "rerank")


def is_chat_model(model):
    return (
        isinstance(model, str)
        and MODEL_NAME.fullmatch(model) is not None
        and not any(token in model.lower() for token in NON_CHAT)
    )


def fetch_catalog(timeout=20):
    settings = yaml.safe_load(Path("/home/iecme/.dsh-t2/settings.yaml").read_text())
    provider_name = settings["agent-default-model"]["provider"]
    provider = settings["llm-pi-ai"]["providers"][provider_name]
    credentials = yaml.safe_load(Path("/home/iecme/.dsh-t2/.credentials.yaml").read_text())
    key = credentials["refs"][provider["apiKeyEnv"]]
    if not isinstance(key, str) or not key:
        raise RuntimeError("Configured model credential unavailable")
    url = provider["baseURL"].rstrip("/") + "/models"
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.load(response)
    models = sorted({
        item.get("id") for item in body.get("data", [])
        if isinstance(item, dict) and is_chat_model(item.get("id"))
    })
    if not models:
        raise RuntimeError("Provider returned no compatible text models")
    default = DEFAULT_MODEL if DEFAULT_MODEL in models else models[0]
    return {
        "provider": provider_name,
        "source": url,
        "models": models,
        "default_model": default,
        "fetched_at": time.time(),
    }


def save_catalog(catalog, path=CACHE):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    temporary.replace(path)


def load_catalog(path=CACHE):
    try:
        data = json.loads(path.read_text())
        models = [model for model in data.get("models", []) if is_chat_model(model)]
        if models:
            default = data.get("default_model")
            return {**data, "models": models,
                    "default_model": default if default in models else models[0]}
    except (OSError, ValueError, TypeError):
        pass
    return {"provider": "", "source": "cache unavailable", "models": [DEFAULT_MODEL],
            "default_model": DEFAULT_MODEL, "fetched_at": 0.0}
