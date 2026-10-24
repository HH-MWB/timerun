---
title: Metadata
---

# Metadata

Key-value **metadata** can be attached to each measurement (e.g. run id, tags). It is stored on the **Measurement** and can be read or mutated for that run.

## Supplying metadata

Provide a dictionary when instantiating the Timer:

```python
with Timer(metadata={"run_id": "abc", "tag": "ingest"}) as m:
    do_work()

# m.metadata is {"run_id": "abc", "tag": "ingest"}
```

Each measurement receives a **shallow copy** of this dictionary at enter time (`self._metadata.copy()`). The Timer retains the original by reference but does not reuse the same dict for multiple measurements. Non-pickleable objects (such as locks, file handles, or network connections) can be safely included in metadata without crashing.

## Per-measurement copy; isolation between runs

- Each block or call receives its **own** dictionary copy of the initial metadata. Mutating `measurement.metadata` (e.g. adding or modifying keys) inside that block or in `on_start` affects only that measurement.
- If you reuse the same Timer for a second block, the second block’s measurement starts from a fresh copy of the Timer’s initial metadata. It does **not** inherit any keys or changes from the first block.

!!! tip "Metadata is per run"

    Metadata is scoped to the measurement. Use it to tag that run; it does not leak to the next run.

## Mutating metadata

You can mutate `measurement.metadata` inside the timed block or in `on_start` to add or change entries for that run (e.g. request id from context, or a tag set after checking a condition). For patterns such as adding a request id in `on_start`, see [Use metadata effectively](../cookbook/metadata.md).
