import os
import yaml
from pathlib import Path
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

MAP = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "NUM_WORKERS": "workers",
    "APP_DEBUG": "debug",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
}

def to_bool(v):
    return str(v).strip().lower() in {"true","1","yes","on"}

def cast(key,val):
    if key in ("port","workers"):
        return int(val)
    if key=="debug":
        return to_bool(val)
    return str(val)

def merge():
    cfg = DEFAULTS.copy()

    p = Path("config.development.yaml")
    if p.exists():
        data = yaml.safe_load(p.read_text()) or {}
        for k,v in data.items():
            cfg[k] = cast(k,v)

    file_env = dotenv_values(".env")
    for ek,ck in MAP.items():
        if ek in file_env and file_env[ek] is not None:
            cfg[ck] = cast(ck,file_env[ek])

    # explicit OS env override
    for ek,ck in MAP.items():
        val = os.getenv(ek)
        if val is not None:
            cfg[ck] = cast(ck,val)

    return cfg

@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    cfg = merge()
    for item in set:
        if "=" in item:
            k,v = item.split("=",1)
            cfg[k] = cast(k,v)
    cfg["api_key"] = "****"
    return cfg
