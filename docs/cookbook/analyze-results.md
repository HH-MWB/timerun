---
title: Analyze results
---

# Analyze results

**Problem:** You have many measurements (e.g. from repeated runs or a decorator's `measurements` deque) and want to summarize or compare — mean, variance, confidence intervals.

**Idea:** TimeRun gives you the numbers; you use standard tools (e.g. numpy, scipy, pandas) for analysis. Collect `Measurement` objects, extract durations, then compute what you need.

## Collect measurements

Two common ways to get a list of measurements:

1. **From a decorated function** — use the wrapped callable’s `measurements` deque when you run the same function many times (e.g. benchmarks or repeated calls):

```python
from timerun import Timer

@Timer()
def my_func():
    pass

for _ in range(100):
    my_func()

measurements = list(my_func.measurements)
```

2. **From a context manager** — append each measurement in `on_end` to a list (or a queue for later processing) when you time one-off blocks or multiple different blocks.

## What to extract

Each measurement has **wall time** and **CPU time**; use the one that matches your question (e.g. wall for latency, CPU for compute-bound work). Use `wall_time.duration` (nanoseconds, int) or `wall_time.timedelta.total_seconds()` for float seconds. You can also use **metadata** to group or filter before computing stats (e.g. by `run_id`, `stage`) so you get per-group summaries.

```python
durations_ns = [m.wall_time.duration for m in measurements]
# or for seconds as float:
durations_s = [m.wall_time.timedelta.total_seconds() for m in measurements]
```

## Summarize

TimeRun does not implement statistics — it only records timings. Use numpy, scipy, pandas, or your own code for aggregation and inference.

### Mean and a simple confidence interval

Example using `scipy.stats` for a t-based 95% confidence interval:

```python
import numpy as np
import scipy.stats

durations_ns = [m.wall_time.duration for m in measurements]
a = np.array(durations_ns) / 1e9  # convert to seconds

mean_s = a.mean()
n = len(a)
ci = scipy.stats.t.interval(0.95, n - 1, loc=mean_s, scale=scipy.stats.sem(a))
# ci is (lower, upper) in seconds
print(f"mean = {mean_s:.6f} s, 95% CI = [{ci[0]:.6f}, {ci[1]:.6f}]")
```

### Variance and percentiles

Use the same duration array `a` (in seconds). Standard deviation and variance describe spread; percentiles (e.g. 50th, 99th) are useful for latency-style analysis:

```python
# a = np.array(durations_ns) / 1e9  # from above
std_s = a.std()
var_s = a.var()
p50, p99 = np.percentile(a, [50, 99])

print(f"std       = {std_s:.6f} s")
print(f"variance  = {var_s:.12f} s²")
print(f"p50 (median) = {p50:.6f} s")
print(f"p99       = {p99:.6f} s")
```

Example output:

```
std       = 0.002341 s
variance  = 0.000005481234 s²
p50 (median) = 0.052103 s
p99       = 0.058892 s
```

To group by metadata (e.g. by `run_id` or `stage`) and compute stats per group, put durations and metadata into a pandas DataFrame and use `groupby` before applying the same summaries.

## Plot the confidence interval

You can draw the mean and confidence interval (e.g. 95% CI) as a simple diagram. Reuse the same `mean_s` and `ci` from the summary above:

```python
import matplotlib.pyplot as plt

# mean_s and ci from the Summarize section above
lower, upper = ci
half_width = (upper - lower) / 2

fig, ax = plt.subplots()
ax.errorbar(0, mean_s, yerr=half_width, fmt="o", capsize=5, label="mean ± 95% CI")
ax.set_ylabel("Duration (s)")
ax.set_xticks([])
ax.legend()
ax.set_title("95% confidence interval")
plt.tight_layout()
plt.show()
```

This plots the mean as a point with an error bar spanning the confidence interval. For more on confidence intervals and benchmarking, see your preferred stats or benchmarking reference.

**See also:** [Measure function calls](../guide/measure-functions.md) for the `measurements` deque and `maxlen`. [Callbacks](../guide/callbacks.md) for collecting measurements in `on_end`.
