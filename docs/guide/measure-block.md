---
title: Measure a block
---

# Measure a block

Use the Timer as a **context manager** to measure a single block of code. The Timer creates one **Measurement** per block; `wall_time` and `cpu_time` are set on block exit.

## Syntax

Synchronous:

```python
from timerun import Timer

with Timer() as m:
    pass  # code block to be measured

m.wall_time.timedelta   # datetime.timedelta
m.cpu_time.timedelta    # datetime.timedelta
```

Asynchronous:

```python
async with Timer() as m:
    await do_something()

m.wall_time.timedelta
```

Wall time is typically equal to or greater than CPU time because wall time counts all elapsed time (including waiting for I/O, sleep, or OS scheduling), while CPU time only counts time the processor actively ran your code.

## Behavior summary

| Scenario | Behavior |
|----------|----------|
| Single block | One measurement; `wall_time` and `cpu_time` set on exit. |
| Sequential blocks (same Timer) | One measurement per block; each block receives its own measurement with a fresh copy of the initial metadata. |
| Nested blocks (same Timer) | Outer and inner each receive one measurement; timings are independent (outer wall time includes the inner block’s wall time). |
| Multiple threads (same Timer) | One measurement per thread per enter/exit; each thread has its own independent stack, so threads do not interfere with each other. |
| Exception in block | The measurement is still recorded (wall/cpu set on exit); the exception propagates to the caller. |
| Invalid use: `__exit__` without `__enter__` | `RuntimeError` with message `"__exit__ called without a matching __enter__"`. |

The same Timer instance can be reused for multiple blocks (sequential or nested). Each block receives its own Measurement; metadata mutations in one block do not appear in the next (see [Metadata](metadata.md)).

**Next:** [Measure functions](measure-functions.md)
