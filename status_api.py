import asyncio
from time import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcstatus import JavaServer
import a2s  # python-a2s

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://rcfg.xyz"]
    allow_methods=["GET"],
    allow_headers=["*"],
)

SERVERS = {
    "minecraft": {
        "host": "mc.rcfg.xyz",
        "port": 25565,
        "type": "minecraft",
    },
    "craftoria": {
        "host": "46.4.224.70",
        "port": 25580,
        "type": "minecraft",
    },
    "cs2": {
        "host": "135.181.19.52",
        "port": 27020,
        "type": "source",
    },
    "arma": {
        "host": "135.181.19.52",
        "port": 2001,
        "type": "tcp",
    },
}
_cache = {}
TTL = 30  # seconds


class Status(BaseModel):
    online:      bool
    players:     int = 0
    max_players: int = 0


def get_cached(key: str):
    ent = _cache.get(key)
    if ent and time() - ent["ts"] < TTL:
        return ent["val"]
    return None


def set_cache(key: str, val: Status):
    _cache[key] = {"val": val, "ts": time()}


async def ping_minecraft(host: str, port: int) -> Status:
    try:
        srv = JavaServer(host, port)
        loop = asyncio.get_event_loop()
        stat = await loop.run_in_executor(None, srv.status)
        return Status(
            online=True,
            players=stat.players.online,
            max_players=stat.players.max,
        )
    except Exception:
        return Status(online=False)


async def ping_source(host: str, port: int) -> Status:
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: a2s.info((host, port)))
        return Status(
            online=True,
            players=info.player_count,
            max_players=info.max_players,
        )
    except Exception:
        return Status(online=False)


async def ping_tcp(host: str, port: int) -> Status:
    try:
        reader, writer = await asyncio.open_connection(host, port)
        writer.close()
        await writer.wait_closed()
        return Status(online=True)
    except Exception:
        return Status(online=False)


@app.get("/api/status/{srv_name}", response_model=Status)
async def get_status(srv_name: str):
    cfg = SERVERS.get(srv_name)
    if not cfg:
        return Status(online=False)
    cached = get_cached(srv_name)
    if cached:
        return cached

    if cfg["type"] == "minecraft":
        res = await ping_minecraft(cfg["host"], cfg["port"])
    elif cfg["type"] == "source":
        res = await ping_source(cfg["host"], cfg["port"])
    else:
        res = await ping_tcp(cfg["host"], cfg["port"])

    set_cache(srv_name, res)
    return res
