---
title: TimeSpan
---

# TimeSpan

A **TimeSpan** represents an immutable time interval with start and end timestamps. The Timer uses it for `wall_time` and `cpu_time` on each measurement. You can also construct TimeSpan instances directly (e.g. for tests or custom logic).

## Attributes

| Attribute   | Type | Description |
|------------|------|-------------|
| `duration` | `int` | Elapsed time in nanoseconds (`end - start`). Computed automatically when the object is created — not a constructor argument. Used for equality, ordering, and hashing. |
| `start`    | `int` | Start timestamp in nanoseconds. |
| `end`      | `int` | End timestamp in nanoseconds. |
| `timedelta`| `datetime.timedelta` | Read-only. Duration as a `datetime.timedelta`; nanoseconds are converted to whole microseconds (`duration // 1000`) to match `timedelta` resolution. |

## Comparison and hashing

Equality and ordering are based **only on `duration`**. `start` and `end` are excluded from comparison, so two spans with the same duration compare equal even if their intervals differ. TimeSpan is hashable and supports sorting.

## Validation

`end` must be greater than or equal to `start`. If `end` is less than `start`, the constructor raises `ValueError` with message `"end must be >= start"`.

## Example

```python
from datetime import timedelta
from timerun import TimeSpan

span = TimeSpan(start=0, end=1_000_000)  # 1 ms
span.duration   # 1000000 (nanoseconds)
span.timedelta  # datetime.timedelta(microseconds=1000)

# Comparison by duration only
TimeSpan(start=0, end=100) == TimeSpan(start=200, end=300)  # True (same duration)
```
