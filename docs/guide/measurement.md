---
title: Measurement
---

# Measurement

A **Measurement** represents a single timing result: wall-clock time, CPU time, and optional metadata. The Timer creates one Measurement per block or function call. You obtain it from the context manager (`with Timer() as m`) or from the decorator’s `measurements` deque.

## Attributes

| Attribute   | Type | Description |
|------------|------|-------------|
| `wall_time` | `TimeSpan \| None` | Wall-clock time for the measurement, or `None` until the block or call exits. |
| `cpu_time`  | `TimeSpan \| None` | CPU time for the measurement, or `None` until the block or call exits. |
| `metadata`  | `dict[str, object]` | Key-value metadata (e.g. run id, tags). Defaults to `{}`. Mutate in place to add or change entries for this measurement. |

## When wall_time and cpu_time are set

When the Timer creates the Measurement (at the start of a `with` block or a decorated call), `wall_time` and `cpu_time` are `None`. They are assigned when the block exits or the call completes. So in `on_start` the measurement does not yet have timings; in `on_end`, both are set.

## Metadata

Metadata is mutable. Initial metadata is supplied via `Timer(metadata={...})`; each measurement receives a deep copy when the timed block or call begins. You can mutate `measurement.metadata` inside the timed block or in `on_start` to add or change keys for that run only. See [Metadata](metadata.md) for copying and scope rules.

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

**Next:** [Timer (overview)](timer.md)
