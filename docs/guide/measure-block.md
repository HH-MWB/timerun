---
title: Measure a block
---

# Measure a block

Use the Timer as a **context manager** to measure a single block of code. The Timer creates one **Measurement** per block; `wall_time` and `cpu_time` are set on block exit.

## Syntax

=== "Synchronous"

    ```python
    from timerun import Timer

    with Timer() as m:
        pass  # code block to be measured

    m.wall_time.timedelta   # datetime.timedelta
    m.cpu_time.timedelta    # datetime.timedelta
    ```

=== "Asynchronous"

    ```python
    from timerun import Timer

    async with Timer() as m:
        await do_something()

    m.wall_time.timedelta   # datetime.timedelta
    m.cpu_time.timedelta    # datetime.timedelta
    ```

Wall vs CPU time and sampling order are explained in [Timer overview: How timing works](timer.md#how-timing-works).

## Behavior summary

| Scenario | Behavior |
|----------|----------|
| Single block | One measurement; `wall_time` and `cpu_time` set on exit. |
| Sequential blocks (same Timer) | One measurement per block; each block receives its own measurement with a fresh copy of the initial metadata. |
| Nested blocks (same Timer) | Outer and inner each receive one measurement; timings are independent (outer wall time includes the inner block’s wall time). |
| Multiple threads (same Timer) | One measurement per thread per enter/exit; each thread has its own independent stack, so threads do not interfere with each other. |
| Concurrent asyncio tasks (same Timer) | One measurement per task per enter/exit; each asyncio task has its own independent stack (like threads in sync mode), so concurrent tasks do not interfere with each other. |
| Invalid use: `async with` outside a task | `RuntimeError` with message `"no current asyncio task"` (for example if `async with Timer()` is used from synchronous code without a current asyncio task). |
| Exception in block | The measurement is still recorded (wall/cpu set on exit); the exception propagates to the caller. |
| Invalid use: `__exit__` without `__enter__` | `RuntimeError` with message `"__exit__ called without a matching __enter__"`. |

The same Timer instance can be reused for multiple blocks (sequential or nested). Each block receives its own Measurement; metadata mutations in one block do not appear in the next (see [Metadata](metadata.md)).
