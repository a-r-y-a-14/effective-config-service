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

DEFAULTS={
    "port":8000,
    "workers":1,
    "debug":False,
    "log_level":"info",
    "api_key":"default-secret-000",
}

SIM_OS={
    "APP_PORT":"8249",
    "APP_WORKERS":"5",
    "APP_DEBUG":"true",
}

MAP={
    "APP_PORT":"port",
    "APP_WORKERS":"workers",
    "NUM_WORKERS":"workers",
    "APP_DEBUG":"debug",
    "APP_LOG_LEVEL":"log_level",
    "APP_API_KEY":"api_key",
}

def to_bool(v):
    return str(v).strip().lower() in ("true","1","yes","on")

def cast(k,v):
    if k in ("port","workers"):
        return int(v)
    if k=="debug":
        return to_bool(v)
    return str(v)

@app.get("/effective-config")
def effective_config(set: list[str]=Query(default=[])):
    cfg=DEFAULTS.copy()

    p=Path("config.development.yaml")
    if p.exists():
        data=yaml.safe_load(p.read_text()) or {}
        for k,v in data.items():
            cfg[k]=cast(k,v)

    envf=dotenv_values(".env")
    for ek,ck in MAP.items():
        if ek in envf and envf[ek] is not None:
            cfg[ck]=cast(ck,envf[ek])

    for ek,val in SIM_OS.items():
        cfg[MAP[ek]]=cast(MAP[ek],val)

    for item in set:
        if "=" in item:
            k,v=item.split("=",1)
            cfg[k]=cast(k,v)

    cfg["api_key"]="****"
    return cfg
