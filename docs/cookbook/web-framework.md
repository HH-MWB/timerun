---
title: Time web requests
---

# Time web requests

**Problem:** You want **wall and CPU time per HTTP request** so you can log latency or export metrics without ad-hoc timers in every view.

**Idea:** Run the request (or the ASGI/WSGI pipeline) inside a **`Timer`** and handle the `Measurement` in **`on_end`** (logging, metrics, etc.). TimeRun stays dependency-free; framework imports live only in your app.

=== "FastAPI (Starlette)"

    ```python
    import logging
    from starlette.middleware.base import BaseHTTPMiddleware
    from timerun import Timer

    logger = logging.getLogger(__name__)


    class RequestTimerMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            async with Timer(
                on_end=lambda m: logger.info(
                    "request",
                    extra={
                        "path": str(request.url.path),
                        "wall_s": m.wall_time.timedelta.total_seconds(),
                        "cpu_s": m.cpu_time.timedelta.total_seconds(),
                    },
                ),
            ):
                return await call_next(request)


    # app.add_middleware(RequestTimerMiddleware)
    ```

=== "Flask"

    ```python
    import logging
    from flask import Flask, g
    from timerun import Timer

    logger = logging.getLogger(__name__)
    app = Flask(__name__)


    @app.before_request
    def _timer_enter():
        g._timer = Timer()
        g._measurement = g._timer.__enter__()


    @app.teardown_request
    def _timer_exit(exc):
        if not hasattr(g, "_timer"):
            return
        g._timer.__exit__(
            type(exc) if exc else None,
            exc,
            exc.__traceback__ if exc else None
        )
        m = g._measurement
        logger.info(
            "request",
            extra={
                "wall_s": m.wall_time.timedelta.total_seconds(),
                "cpu_s": m.cpu_time.timedelta.total_seconds(),
            },
        )
    ```

=== "Django"

    ```python
    import logging
    from timerun import Timer

    logger = logging.getLogger(__name__)


    class RequestTimerMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            def log_request(m):
                logger.info(
                    "request",
                    extra={
                        "path": request.path,
                        "wall_s": m.wall_time.timedelta.total_seconds(),
                        "cpu_s": m.cpu_time.timedelta.total_seconds(),
                    },
                )

            with Timer(on_end=log_request):
                return self.get_response(request)
    ```

    Add the class to `MIDDLEWARE`. Using `with Timer()` ensures `on_end` runs even when the view raises.

For richer context (request id, user), combine with [Use metadata effectively](metadata.md) and `on_start`.

**See also:** [Share results](share-results.md) for logs, Prometheus, and OpenTelemetry.
