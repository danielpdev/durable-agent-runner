"""Persistent step state with a transactional local side effect and cancellation."""

import json
import tempfile
import uuid
from pathlib import Path
from sqlalchemy import String, select, update
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base, database


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[str]
    state: Mapped[str]
    step: Mapped[int]
    result: Mapped[str | None]


class Effect(Base):
    __tablename__ = "effects"
    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    body: Mapped[str]


class Runner:
    def __init__(self, url=None):
        self.engine, self.sessions = database(url)

    def submit(self, items):
        if not isinstance(items, list) or any(type(x) is not int for x in items):
            raise ValueError("integer list required")
        with self.sessions.begin() as s:
            j = Job(id=str(uuid.uuid4()), payload=json.dumps(items), state="pending", step=0, result=None)
            s.add(j)
            return j.id

    def advance(self, jid):
        with self.sessions.begin() as s:
            j = s.scalar(select(Job).where(Job.id == jid).with_for_update())
            if not j:
                raise ValueError("unknown job")
            if j.state in {"cancelled", "done"}:
                return self._view(j)
            expected = j.step
            claimed = s.execute(
                update(Job)
                .where(Job.id == jid, Job.step == expected, Job.state.in_(["pending", "running"]))
                .values(state="running", step=expected + 1)
            )
            if claimed.rowcount != 1:
                raise ValueError("job changed; retry")
            if expected == 0:
                j.result = json.dumps({"sum": sum(json.loads(j.payload))})
            elif expected == 1:
                # Effect and checkpoint share a transaction. Remote APIs require an idempotency key/outbox.
                if not s.get(Effect, jid):
                    s.add(Effect(job_id=jid, body=j.result))
            else:
                j.state = "done"
            s.flush()
            return self._view(j)

    def cancel(self, jid):
        with self.sessions.begin() as s:
            r = s.execute(
                update(Job)
                .where(Job.id == jid, Job.state.in_(["pending", "running"]))
                .values(state="cancelled")
            )
            return {"cancelled": r.rowcount == 1}

    @staticmethod
    def _view(j):
        return dict(id=j.id, state=j.state, step=j.step, result=json.loads(j.result) if j.result else None)

    def status(self, jid):
        with self.sessions() as s:
            j = s.get(Job, jid)
            if not j:
                raise ValueError("unknown job")
            return self._view(j)

    def effects(self):
        with self.sessions() as s:
            return [dict(job_id=e.job_id, body=json.loads(e.body)) for e in s.scalars(select(Effect))]


def demo(mode="fixture"):
    with tempfile.TemporaryDirectory() as d:
        url = "sqlite:///" + str(Path(d) / "jobs.sqlite")
        r = Runner(url)
        jid = r.submit([1, 2, 3])
        checkpoint = r.advance(jid)
        restarted = Runner(url)
        while restarted.status(jid)["state"] != "done":
            restarted.advance(jid)
        restarted.advance(jid)
        return dict(checkpoint=checkpoint, completed=restarted.status(jid), effects=restarted.effects())


def evaluate(mode="fixture"):
    r = demo(mode)
    return dict(passed=len(r["effects"]) == 1 and r["completed"]["result"]["sum"] == 6, scenario=r)
