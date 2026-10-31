# Demo walkthrough

## Start

```bash
make setup
make demo
make test
make eval
```

## What to show

A job advances one durable step per transaction. The demonstrated business effect is stored in the same database transaction as its checkpoint, so a restart cannot duplicate that local effect.

## Failure case to discuss

A child process exits after committing a checkpoint; a new runner resumes and produces one effect. Cancellation stops subsequent effects.

## Evidence

Open the JSON evaluation report alongside the implementation. Distinguish synthetic fixture outputs, synthetic trace timing, actual elapsed evaluation time, and local model inference. Do not present a tiny test set as a production benchmark.

## Closing tradeoff

Exactly-once behavior is limited to the demonstrated local database transaction. Remote tools require idempotency keys or an outbox. There is no distributed scheduler or worker lease in this small runner.

The repository's `docs/demo.webm` or `docs/demo.mp4`, when present, records the demonstration. A terminal replay is also available for focused projects as `docs/demo.cast`.
