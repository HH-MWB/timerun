---
title: Measure function calls
---

# Measure function calls

Apply the **decorator** `@Timer()` to time every call to a function or generator. One **Measurement** per call is appended to the wrapped callable’s `measurements` deque.

## Syntax

=== "Sync function"

    ```python
    from timerun import Timer

    @Timer()
    def func():
        return

    func()
    func.measurements[-1].wall_time.timedelta
    func.measurements[-1].cpu_time.timedelta
    ```

=== "Async function"

    ```python
    import asyncio
    from timerun import Timer

    @Timer()
    async def func():
        return

    async def main():
        await func()
        func.measurements[-1].wall_time.timedelta

    asyncio.run(main())
    ```

=== "Sync generator"

    ```python
    from timerun import Timer

    @Timer()
    def gen():
        yield 1
        yield 2

    list(gen())  # one measurement after full consumption
    gen.measurements[-1].wall_time.timedelta
    ```

=== "Async generator"

    ```python
    import asyncio
    from timerun import Timer

    @Timer()
    async def agen():
        yield 1
        yield 2

    async def main():
        async for _ in agen():
            pass
        agen.measurements[-1].wall_time.timedelta

    asyncio.run(main())
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

You do not need to exhaust the generator: stopping early (for example `break` out of a `for` loop) or calling `.close()` on the iterator still ends the timed region and records **one** measurement for that run.

## The `measurements` deque

The wrapped callable has a `measurements` attribute: a `deque` of `Measurement` instances in order from oldest to newest. Each call (or full generator consumption) appends one entry. When `maxlen` is set, the deque is bounded and discards the oldest entry when full.

## Thread safety

Concurrent calls from multiple threads each produce one measurement. Appends to `measurements` are thread-safe; for example, two threads calling the same timed function produce two measurements.

## Exceptions

If a timed function or generator raises, one measurement is still recorded for that run, and the exception is re-raised to the caller.
