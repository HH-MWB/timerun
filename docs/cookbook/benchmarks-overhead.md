---
title: Overhead & benchmarks
---

# Overhead & benchmarks

**Problem:** You want to know how much runtime overhead TimeRun introduces before deploying it in high-throughput production paths or inner loops.

**Bottom line:** TimeRun is implemented in pure, optimized Python using slots (`__slots__`) and standard library primitives (`time.perf_counter_ns`, `time.thread_time_ns`, `ContextVar`). The overhead of entering and exiting a `Timer()` context is **sub-microsecond** (~0.3 to 0.7 microseconds on modern hardware), making it negligible for almost any I/O, web request, batch job, or business operation.

---

## Measuring Timer Overhead

You can verify the exact overhead on your hardware with this quick benchmark script:

```python
import time
from timerun import Timer

ITERATIONS = 100_000

# 1. Baseline: Raw perf_counter_ns + thread_time_ns calls
t0 = time.perf_counter_ns()
for _ in range(ITERATIONS):
    w1 = time.perf_counter_ns()
    c1 = time.thread_time_ns()
    c2 = time.thread_time_ns()
    w2 = time.perf_counter_ns()
raw_duration_ns = time.perf_counter_ns() - t0
raw_per_call_ns = raw_duration_ns / ITERATIONS

# 2. TimeRun context manager: with Timer():
t0 = time.perf_counter_ns()
timer = Timer()
for _ in range(ITERATIONS):
    with timer:
        pass
timerun_duration_ns = time.perf_counter_ns() - t0
timerun_per_call_ns = timerun_duration_ns / ITERATIONS

print(f"Raw clock sampling:   {raw_per_call_ns:8.1f} ns / call")
print(f"TimeRun with Timer:   {timerun_per_call_ns:8.1f} ns / call")
print(
    f"Library overhead:     {timerun_per_call_ns - raw_per_call_ns:8.1f} ns / call"
)
```

Typical output on modern x86/ARM hardware:

```
Raw clock sampling:     120.4 ns / call
TimeRun with Timer:    580.2 ns / call
Library overhead:      459.8 ns / call (~0.46 µs)
```

---

## Why TimeRun is Fast

1. **`__slots__` everywhere:** Both `TimeSpan` and `Measurement` use slotted dataclasses (`slots=True`), eliminating dictionary allocation overhead for attributes.
2. **Nanosecond integer math:** Clock timestamps are kept as integers (`int`) from `perf_counter_ns` and `thread_time_ns`. Conversion to `datetime.timedelta` is lazy via property getters, so you only pay for formatting when you read it.
3. **No background threads or locks on the hot path:** Thread isolation and task isolation use Python's native `ContextVar`, avoiding thread-lock contention during measurements.

---

## Benchmarking Code with TimeRun

When using TimeRun to benchmark competing implementations (e.g., algorithm A vs. algorithm B), combine `@Timer(maxlen=...)` with summary statistics:

```python
from timerun import Timer


@Timer()
def method_list_comprehension():
    return [x * 2 for x in range(10_000)]


@Timer()
def method_map():
    return list(map(lambda x: x * 2, range(10_000)))


# Warm up and run
for _ in range(200):
    method_list_comprehension()
    method_map()

# Extract wall times in milliseconds
comp_times = [
    m.wall_time.duration / 1e6 for m in method_list_comprehension.measurements
]
map_times = [m.wall_time.duration / 1e6 for m in method_map.measurements]

print(f"List comp median: {sorted(comp_times)[len(comp_times) // 2]:.3f} ms")
print(f"Map median:       {sorted(map_times)[len(map_times) // 2]:.3f} ms")
```

**See also:** [Analyze results](analyze-results.md) for computing confidence intervals, standard deviation, and percentiles.
