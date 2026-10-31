from functools import lru_cache
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core import Runner

app = FastAPI(title="durable-agent-runner")


@lru_cache
def service():
    return Runner()


def guarded(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except ValueError as e:
        raise HTTPException(409, str(e)) from e


class JobInput(BaseModel):
    items: list[int]


@app.post("/api/jobs", status_code=202)
def submit(b: JobInput):
    return {"id": guarded(service().submit, b.items), "state": "pending"}


@app.get("/api/jobs/{jid}")
def status(jid: str):
    return guarded(service().status, jid)


@app.post("/api/jobs/{jid}/advance")
def advance(jid: str):
    return guarded(service().advance, jid)


@app.post("/api/jobs/{jid}/cancel")
def cancel(jid: str):
    return service().cancel(jid)


@app.get("/api/effects")
def effects():
    return service().effects()
