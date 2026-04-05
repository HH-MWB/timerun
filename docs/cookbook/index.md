---
title: Cookbook
---

# Cookbook

Real-world patterns for using TimeRun: use metadata effectively, share results with your stack, time web traffic, and analyze timing data.

You already know the API from the [Guide](../guide/index.md): timer overview, measure a block, measure function calls, metadata, and callbacks. Here we show how to apply it to concrete problems.

1. **[Use metadata effectively](metadata.md)** — Add context (e.g. request id, stage) to every measurement by mutating metadata in `on_start`.
2. **[Share results](share-results.md)** — Send measurements to logs, files, OpenTelemetry, or Prometheus using `on_end`.
3. **[Time web requests](web-framework.md)** — Wrap HTTP requests with `Timer` in FastAPI, Flask, or Django.
4. **[Analyze results](analyze-results.md)** — Collect measurements and compute summaries or confidence intervals with standard tools.
