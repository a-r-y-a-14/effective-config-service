import os
from pathlib import Path

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

def to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true","1","yes","on")

def coerce(key, value):
    if key in ("port","workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)

def load_config():
    cfg = DEFAULTS.copy()

    y = Path("config.development.yaml")
    if y.exists():
        with open(y, "r") as f:
            data = yaml.safe_load(f) or {}
        for k,v in data.items():
            cfg[k] = coerce(k,v)

    env_file = dotenv_values(".env")
    mapping = {
        "APP_PORT":"port",
        "APP_WORKERS":"workers",
        "NUM_WORKERS":"workers",
        "APP_DEBUG":"debug",
        "APP_LOG_LEVEL":"log_level",
        "APP_API_KEY":"api_key",
    }

    for env_name,key in mapping.items():
        if env_name in env_file and env_file[env_name] is not None:
            cfg[key] = coerce(key, env_file[env_name])

    for env_name,key in mapping.items():
        if env_name in os.environ:
            cfg[key] = coerce(key, os.environ[env_name])

    return cfg

@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    cfg = load_config()

    for item in set:
        if "=" in item:
            k,v = item.split("=",1)
            cfg[k] = coerce(k,v)

    cfg["api_key"] = "****"
    return cfg
