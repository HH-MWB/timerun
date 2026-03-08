---
title: Recipes
---

# Recipes

Real-world patterns for using TimeRun: use metadata effectively, share results with your stack, and analyze timing data.

You already know the API from the [Reference](../guide/index.md) (measure blocks, functions, metadata, callbacks). Here we show how to apply it to concrete problems.

1. **[Use metadata effectively](metadata.md)** — Add context (e.g. request id, stage) to every measurement by mutating metadata in `on_start`.
2. **[Share results](share-results.md)** — Send measurements to logs, files, or OpenTelemetry using `on_end`.
3. **[Analyze results](analyze-results.md)** — Collect measurements and compute summaries or confidence intervals with standard tools.
