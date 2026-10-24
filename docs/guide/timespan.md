---
title: TimeSpan
---

# TimeSpan

A **TimeSpan** represents an immutable time interval with start and end timestamps. The Timer uses it for `wall_time` and `cpu_time` on each measurement. You can also construct TimeSpan instances directly (e.g. for tests or custom logic).

## Attributes

| Attribute      | Type | Description |
|---------------|------|-------------|
| `duration`    | `int` | Elapsed time in nanoseconds (`end - start`). Computed automatically when the object is created — not a constructor argument. |
| `start`       | `int` | Start timestamp in nanoseconds. Used for equality and hashing. |
| `end`         | `int` | End timestamp in nanoseconds. Used for equality and hashing. |
| `timedelta`   | `datetime.timedelta` | Read-only. Duration as a `datetime.timedelta`; nanoseconds are converted to whole microseconds (`duration // 1000`) to match `timedelta` resolution. |

## Comparison and hashing

- **Equality (`==`, `!=`) and hashing (`hash()`):** Based on the interval identity (`start` and `end`). Two spans compare equal only if their start and end timestamps match. This ensures distinct intervals do not collide when used in a `set` or as `dict` keys.
- **Duration comparison:** To compare or sort durations, use `span.duration` directly (e.g. `span_a.duration < span_b.duration`). Direct ordering comparisons (`<`, `<=`, `>`, `>=`) on `TimeSpan` objects raise `TypeError`.

## Validation

`end` must be greater than or equal to `start`. If `end` is less than `start`, the constructor raises `ValueError` with message `"end must be >= start"`.

## Example

```python
from datetime import timedelta
from timerun import TimeSpan

span = TimeSpan(start=0, end=1_000_000)  # 1 ms
span.duration  # 1000000 (nanoseconds)
span.timedelta  # datetime.timedelta(microseconds=1000)

# Float seconds can be calculated directly if needed:
seconds = span.duration / 1e9  # 0.001

# Interval equality
s1 = TimeSpan(start=0, end=100)
s2 = TimeSpan(start=200, end=300)
s1 == s2  # False (different intervals)
s1.duration == s2.duration  # True (equal duration of 100ns)
```
