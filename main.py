import os
from pathlib import Path
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
load_dotenv()

DEFAULTS={"port":8000,"workers":1,"debug":False,"log_level":"info","api_key":"default-secret-000"}

def to_bool(v):
    if isinstance(v,bool): return v
    return str(v).strip().lower() in ("true","1","yes","on")

def coerce(k,v):
    if k in ("port","workers"): return int(v)
    if k=="debug": return to_bool(v)
    return str(v)

def load_config():
    cfg=DEFAULTS.copy()
    p=Path("config.development.yaml")
    if p.exists():
        data=yaml.safe_load(p.read_text()) or {}
        for k,v in data.items():
            cfg[k]=coerce(k,v)
    mapping={
        "APP_PORT":"port",
        "APP_WORKERS":"workers",
        "NUM_WORKERS":"workers",
        "APP_DEBUG":"debug",
        "APP_LOG_LEVEL":"log_level",
        "APP_API_KEY":"api_key",
    }
    for env,key in mapping.items():
        if env in os.environ:
            cfg[key]=coerce(key,os.environ[env])
    return cfg

@app.get("/effective-config")
def effective_config(set:list[str]=Query(default=[])):
    cfg=load_config()
    for item in set:
        if "=" in item:
            k,v=item.split("=",1)
            cfg[k]=coerce(k,v)
    cfg["api_key"]="****"
    return cfg
