---
title: Share results
---

# Share results

**Problem:** You need to get measurements out of the process — to a log, a file, OpenTelemetry, Prometheus, or another metrics backend.

**Idea:** Use **`on_end`** (and optionally `on_start`) to push each measurement out when the run finishes. The callback receives the `Measurement` with `wall_time`, `cpu_time`, and `metadata` set.

## Log

```python hl_lines="16"
import logging
from timerun import Timer

logger = logging.getLogger(__name__)

def log_measurement(m):
    logger.info(
        "timing",
        extra={
            "wall_s": m.wall_time.timedelta.total_seconds(),
            "cpu_s": m.cpu_time.timedelta.total_seconds(),
            **m.metadata,
        },
    )

with Timer(on_end=log_measurement):
    do_work()
```

## File

Append a line per measurement (e.g. JSON or CSV) in `on_end`. For high throughput, consider buffering and flushing in batches.

```python
import json
from pathlib import Path
from timerun import Timer

path = Path("measurements.jsonl")

def append_measurement(m):
    record = {
        "wall_ns": m.wall_time.duration,
        "cpu_ns": m.cpu_time.duration,
        **m.metadata,
    }
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")

with Timer(metadata={"run": "1"}, on_end=append_measurement):
    do_work()
```

## OpenTelemetry

Create a span in `on_start`, end it in `on_end`, and set attributes from the measurement. TimeRun does not depend on OpenTelemetry; you use its API from your callback.

```python
from timerun import Timer

# Assume you have a Tracer (e.g. from opentelemetry.trace import get_tracer)
# tracer = get_tracer(__name__)

def on_start(m):
    m.metadata["span"] = tracer.start_span("timerun")  # (1)!

def on_end(m):
    span = m.metadata.get("span")  # (2)!
    if span is None:
        return  # If on_start didn't set a span, skip.
    span.set_attribute("wall_time_ns", m.wall_time.duration)
    span.set_attribute("cpu_time_ns", m.cpu_time.duration)
    for k, v in m.metadata.items():
        if k != "span" and v is not None:
            span.set_attribute(k, str(v))
    span.end()  # (3)!

with Timer(on_start=on_start, on_end=on_end):
    do_work()
```

1. Start the span before the timed work runs so nested operations can attach to the same trace context if your tracer supports it.
2. Retrieve the span object you stashed on the `Measurement`; guard in case `on_start` failed or was skipped.
3. End the span after attributes are set so duration and metadata are recorded on the same span.

## Prometheus

Use the [Prometheus Python client](https://github.com/prometheus/client_python) (`pip install prometheus-client`). Register a histogram (or summary) and observe wall-clock seconds in `on_end`:

```python
from prometheus_client import Histogram
from timerun import Timer

OPERATION_SECONDS = Histogram(
    "timerun_operation_seconds",
    "Wall time for timed operations (seconds)",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, float("inf")),
)


def observe_wall_time(m):
    OPERATION_SECONDS.observe(m.wall_time.timedelta.total_seconds())


with Timer(on_end=observe_wall_time):
    do_work()
```

Expose metrics from your process with `start_http_server` or your framework’s integration so Prometheus can scrape them.

**See also:** [Guide: Callbacks](../guide/callbacks.md) for when callbacks run. For the OpenTelemetry API, see the [OpenTelemetry Python docs](https://opentelemetry.io/docs/languages/python/).
