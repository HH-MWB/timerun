---
title: Use metadata effectively
---

# Use metadata effectively

**Problem:** You want context on every measurement (e.g. request id, stage, experiment id) without repeating it in every `Timer()` call.

**Idea:** Metadata is attached to each measurement. You can **mutate `measurement.metadata` in `on_start`** (or inside the block) to add or change keys for that run. Each measurement gets its own copy of the initial metadata when the run starts, so mutating it in `on_start` only affects that measurement.

## Why this works

Each measurement gets its own deep copy of the metadata dict, so mutations in `on_start` or the block affect only that run. See [Guide: Metadata](../guide/metadata.md) for copy and isolation rules.

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

When context is fixed at the start of the run (request id, stage), **`on_start` is often clearer** than mutating inside the block. Mutating `m.metadata` in the block is still valid when values depend on **work you do inside the timed region** (outcome, branch taken, or a value known only after some steps):

```python
with Timer(metadata={"stage": "ingest"}) as m:
    do_work()
    if some_condition:
        m.metadata["tag"] = "slow_path"
# m.metadata is {"stage": "ingest", "tag": "slow_path"} when relevant
```

## Example: invocation count with a closure

Use a factory that returns an `on_start` callback with its own counter so each measurement gets a monotonic call number (e.g. for a decorated hot path):

```python
from timerun import Timer


def make_invocation_callback():
    count = 0  # (1)!

    def set_invocation(m):
        nonlocal count  # (2)!
        count += 1
        m.metadata["invocation"] = count

    return set_invocation  # (3)!


on_start = make_invocation_callback()
for _ in range(3):
    with Timer(on_start=on_start) as m:
        pass  # your code

# After each block, invocation is 1, 2, 3, ...; last m.metadata["invocation"] is 3
```

1. Counter lives in the closure; each factory call gets its own independent sequence.
2. `nonlocal` updates the enclosing `count` so every invocation of `set_invocation` sees the same running total.
3. Return the inner function so `Timer` receives a stable `on_start` callback with shared state.

**See also:** [Guide: Metadata](../guide/metadata.md) for passing `metadata={...}` and copy rules.
