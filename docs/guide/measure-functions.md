---
title: Measure functions
---

# Measure functions

Apply the **decorator** `@Timer()` to measure each call of a function or generator. One **Measurement** per call is appended to the wrapped callable’s `measurements` deque.

## Syntax

```python
from timerun import Timer

@Timer()
def func():
    return

func()
func.measurements[-1].wall_time.timedelta
func.measurements[-1].cpu_time.timedelta
```

Use `@Timer(maxlen=10)` to limit how many measurements are retained; the oldest entries are discarded when the deque reaches capacity. The default is unbounded.

## Callable types

| Type | Behavior |
|------|----------|
| Sync function | One measurement per call. |
| Async function | One measurement per call (covers the full `await` of the call). |
| Sync generator | One measurement per **full consumption** of the generator (from the first iteration until the generator is exhausted or closed). |
| Async generator | One measurement per **full consumption** of the async generator (same as sync: from first iteration until exhausted or closed). |

For generators, a single measurement covers the entire iteration, not each yielded value.

## measurements deque

The wrapped callable has a `measurements` attribute: a `deque` of `Measurement` instances in order from oldest to newest. Each call (or full generator consumption) appends one entry. When `maxlen` is set, the deque is bounded and discards the oldest entry when full.

## Thread safety

Concurrent calls from multiple threads each produce one measurement. Appends to `measurements` are thread-safe; for example, two threads calling the same timed function produce two measurements.

## Exceptions

If a timed function or generator raises, one measurement is still recorded for that run, and the exception is re-raised to the caller.

**Next:** [Metadata](metadata.md)
