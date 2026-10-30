---
title: Structured logging
---

# Structured logging with Structlog & Loguru

**Problem:** You want timing metrics directly inside your JSON or structured logs (e.g., for Datadog Log Management, ElasticSearch, or CloudWatch) without manual boilerplate.

**Idea:** Use **`on_end`** to emit the measurement with your favorite logging library. Because `Measurement` provides both `wall_time` and `cpu_time` along with custom `metadata`, your log entries contain clean, machine-parsable duration fields.

---

## Structlog

[structlog](https://www.structlog.org/) is the standard for structured JSON logging in production Python services.

```python
import structlog
from timerun import Timer

log = structlog.get_logger()


def log_to_structlog(m):
    log.info(
        "execution_completed",
        wall_time_ms=round(m.wall_time.duration / 1e6, 3),
        cpu_time_ms=round(m.cpu_time.duration / 1e6, 3),
        **m.metadata,
    )


# Attach context and run
with Timer(
    metadata={"service": "payment", "action": "charge_card"},
    on_end=log_to_structlog,
):
    # Simulated workload
    total = sum(i * i for i in range(100_000))
```

This generates structured JSON output like:

```json
{
  "event": "execution_completed",
  "wall_time_ms": 7.412,
  "cpu_time_ms": 7.398,
  "service": "payment",
  "action": "charge_card",
  "level": "info",
  "timestamp": "2026-10-26T22:30:00.000000Z"
}
```

---

## Loguru

[Loguru](https://github.com/Delgan/loguru) provides a simple, expressive logging interface with contextual bindings.

```python
from loguru import logger
from timerun import Timer


def log_to_loguru(m):
    logger.bind(
        wall_ms=round(m.wall_time.duration / 1e6, 3),
        cpu_ms=round(m.cpu_time.duration / 1e6, 3),
        **m.metadata,
    ).info("Task executed successfully")


with Timer(
    metadata={"task_id": "sync_users", "batch_size": 500},
    on_end=log_to_loguru,
):
    # Timed operation
    pass
```

---

## Reusable Logging Decorator

You can create a reusable helper to measure and log any critical function:

```python
from timerun import Timer
import structlog

logger = structlog.get_logger()


def timed_operation(name: str):
    return Timer(
        metadata={"op_name": name},
        on_end=lambda m: logger.info(
            "timerun_metric",
            operation=m.metadata.get("op_name"),
            duration_ms=m.wall_time.duration / 1e6,
            cpu_ms=m.cpu_time.duration / 1e6,
        ),
    )


@timed_operation("sync_catalog")
def sync_catalog():
    # your logic here
    pass
```

**See also:** [Share results](share-results.md) for standard `logging`, OpenTelemetry, and Prometheus integrations.
