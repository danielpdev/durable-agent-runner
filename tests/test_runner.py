import os
import subprocess
import sys
from app.core import Runner


def test_process_exit_and_resume(tmp_path):
    url = "sqlite:///" + str(tmp_path / "jobs.sqlite")
    r = Runner(url)
    jid = r.submit([4, 5])
    script = 'import os; from app.core import Runner; Runner(os.environ["TEST_DB"]).advance(os.environ["TEST_JOB"]); os._exit(17)'
    p = subprocess.run([sys.executable, "-c", script], env=dict(os.environ, TEST_DB=url, TEST_JOB=jid))
    assert p.returncode == 17
    r = Runner(url)
    for _ in range(5):
        r.advance(jid)
    assert r.status(jid)["state"] == "done" and r.effects() == [{"job_id": jid, "body": {"sum": 9}}]


def test_cancel_before_effect(tmp_path):
    r = Runner("sqlite:///" + str(tmp_path / "cancel.sqlite"))
    jid = r.submit([1])
    r.advance(jid)
    r.cancel(jid)
    r.advance(jid)
    assert r.status(jid)["state"] == "cancelled" and not r.effects()
