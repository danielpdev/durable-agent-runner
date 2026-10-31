# Design record

## Decision

A job advances one durable step per transaction. The demonstrated business effect is stored in the same database transaction as its checkpoint, so a restart cannot duplicate that local effect.

## Failure model

A child process exits after committing a checkpoint; a new runner resumes and produces one effect. Cancellation stops subsequent effects.

## Tradeoffs

Exactly-once behavior is limited to the demonstrated local database transaction. Remote tools require idempotency keys or an outbox. There is no distributed scheduler or worker lease in this small runner.

## Next change to defend in review

Add worker leases, retry policy and a remote outbox adapter.

## Reproducibility

`uv.lock` pins Python dependencies; the web lockfile pins the React build where present. Model-backed evaluations use a separately installed local service. Dataset examples are synthetic and intentionally small. Reported timing is a local observation, not a throughput SLA. Run `make test` after changing state transitions and `make eval` after changing decisions. Keep inference quality separate from deterministic invariant checks.
