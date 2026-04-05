---
title: Measurement
---

# Measurement

A **Measurement** represents a single timing result: wall-clock time, CPU time, and optional metadata. The Timer creates one Measurement per timed block, or one per call when you use the decorator to time function calls. You obtain it from the context manager (`with Timer() as m`) or from the decorator’s `measurements` deque.

## Attributes

| Attribute   | Type | Description |
|------------|------|-------------|
| `wall_time` | `TimeSpan \| None` | Wall-clock time for the measurement (set on block/call exit; `None` before that, including during `on_start`). |
| `cpu_time`  | `TimeSpan \| None` | CPU time for the measurement (set on block/call exit; `None` before that, including during `on_start`). |
| `metadata`  | `dict[str, object]` | Key-value metadata (e.g. run id, tags). Defaults to `{}`. Mutate in place to add or change entries for this measurement. |

## Metadata

`metadata` is a mutable dict scoped to this measurement. See [Metadata](metadata.md) for copy semantics, isolation, and mutation patterns.

## Example

```python
from timerun import Timer, Measurement

with Timer(metadata={"run_id": "exp-1"}) as m:
    pass  # your code

# After block exit:
m.wall_time       # TimeSpan (set)
m.cpu_time        # TimeSpan (set)
m.wall_time.timedelta   # datetime.timedelta
m.metadata        # {"run_id": "exp-1"} (your copy; mutable)
```

You can also construct a Measurement manually (e.g. for tests) by passing `wall_time`, `cpu_time`, and optional `metadata` to the constructor.
