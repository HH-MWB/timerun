---
title: Cookbook
---

# Cookbook

Real-world recipes and production patterns for TimeRun: web frameworks, telemetry pipelines, AI/LLM token streaming, structured logging, and latency analysis.

---

## Observability & Telemetry

- **[Share results](share-results.md)** — Push measurements to standard logging, JSONL files, OpenTelemetry traces, or Prometheus histograms in `on_end`.
- **[Structured logging with Structlog & Loguru](structured-logging.md)** — Emit structured JSON execution events with wall time, CPU time, and metadata.
- **[Use metadata effectively](metadata.md)** — Add contextual tags (e.g., request id, user id, experiment stage) to every measurement in `on_start`.

## Web & AI Applications

- **[Time web requests](web-framework.md)** — Middleware patterns for FastAPI (Starlette), Flask, and Django to capture wall and CPU latency per HTTP request.
- **[Time LLM token streaming](llm-streaming.md)** — Measure Time to First Token (TTFT) and total generation time across streaming AI/LLM responses.

## Analysis & Performance

- **[Analyze results](analyze-results.md)** — Collect measurements to compute statistical summaries, confidence intervals, and percentiles (p50, p99) using NumPy and SciPy.
- **[Overhead & benchmarks](benchmarks-overhead.md)** — Verification of TimeRun's sub-microsecond overhead and patterns for micro-benchmarking algorithms.
