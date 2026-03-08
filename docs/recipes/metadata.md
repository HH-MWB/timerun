# Use metadata effectively

**Problem:** You want context on every measurement (e.g. request id, stage, experiment id) without repeating it in every `Timer()` call.

**Idea:** Metadata is attached to each measurement. You can **mutate `measurement.metadata` in `on_start`** (or inside the block) to add or change keys for that run. Each measurement gets its own copy of the initial metadata at enter time, so mutating it in `on_start` only affects that measurement.

## Why this works

You can edit metadata in `on_start` (or in the block) because the callback receives the **same** `Measurement` instance that is returned from `with Timer(...) as m`. When the block enters, the Timer creates that Measurement with `metadata=deepcopy(self._metadata)` — so each run already has its own dict. Mutating `m.metadata` in `on_start` or in the block therefore mutates that run’s copy only; the object is passed by reference.

You **cannot** set per-run values at Timer init because init runs once and there is no “current run” yet. The dict you pass to `Timer(metadata={...})` is stored and **deep-copied** into each new Measurement on every `__enter__`. So you can only supply a shared template at init; per-run edits must happen after the Measurement for that run exists — in `on_start` or inside the block.

## Example: add run context in `on_start`

Omit metadata (or pass a dict); an empty dict is the default when you pass `None`. Fill it per run in `on_start` from context vars or thread-local storage:

```python
from contextvars import ContextVar
from timerun import Timer

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

def add_request_id(m):
    m.metadata["request_id"] = request_id_ctx.get()

with Timer(on_start=add_request_id) as m:
    pass  # your code

# m.metadata now includes "request_id" for this run
print(m.metadata)  # e.g. {"request_id": "req-abc"}
```

## Example: set tags inside the block

Mutating `m.metadata` inside the timed block is **generally not recommended** — prefer **callbacks** (e.g. `on_start`) when the context is known at the start of the run (e.g. request id, stage). It is useful when metadata must be **dynamically computed from code logic** (e.g. outcome, branch taken, or a value only known after some work):

```python
with Timer(metadata={"stage": "ingest"}) as m:
    do_work()
    if some_condition:
        m.metadata["tag"] = "slow_path"
# m.metadata is {"stage": "ingest", "tag": "slow_path"} when relevant
```

## Example: invocation count with a singleton counter

Use a module-level (or singleton) counter and set it in `on_start` so each measurement carries the call number for that run (e.g. “call #1”, “#2”, …). Handy with a decorator to see invocation order:

```python
from timerun import Timer

_invocation_counter = 0

def set_invocation(m):
    global _invocation_counter
    _invocation_counter += 1
    m.metadata["invocation"] = _invocation_counter

with Timer(on_start=set_invocation) as m:
    pass  # your code

# m.metadata["invocation"] is 1, 2, 3, ... for each run
```

**Next:** [Share results](share-results.md)

For the API details (passing `metadata={...}`, reading `m.metadata`), see [Reference: Metadata](../guide/metadata.md).
