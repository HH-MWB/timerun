"""Structured timing for Python: wall-clock and CPU time per block or call.

TimeRun is a single-file package with no dependencies beyond the standard
library. It records wall-clock time (``perf_counter_ns``) and CPU time
(``process_time_ns``) for code blocks and function calls, producing one
:class:`Measurement` per run. Each measurement carries two
:class:`TimeSpan` objects and optional user-defined metadata.

Use :class:`Timer` as a context manager to time a block::

    with Timer() as m:
        ...
    print(m.wall_time.timedelta)

Or as a decorator to time every call::

    @Timer()
    def func():
        ...
    func()
    print(func.measurements[-1].wall_time.timedelta)

Measurements support optional ``metadata`` (shallow-copied per run) and
``on_start`` / ``on_end`` callbacks. Timer is reusable: thread-safe for
sync blocks, and task-safe for concurrent asyncio tasks.

Public API
----------
TimeSpan
    Immutable nanosecond interval (``duration``, ``start``, ``end``,
    ``timedelta``).
Measurement
    Wall time, CPU time, and metadata for a single timing run.
Timer
    Context manager and decorator that records measurements.

"""

from asyncio import current_task
from collections import deque
from collections.abc import AsyncGenerator, Callable, Generator
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from functools import wraps
from inspect import (
    isasyncgenfunction,
    iscoroutinefunction,
    isgeneratorfunction,
)
from threading import Lock, current_thread
from time import perf_counter_ns, process_time_ns, thread_time_ns
from types import TracebackType
from typing import (
    Literal,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    overload,
)

__version__: str = "0.6.2"

__all__ = [
    "Measurement",
    "TimeSpan",
    "Timer",
]

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)
Y = TypeVar("Y")


@dataclass(frozen=True)
class TimeSpan:
    """A time interval with start and end timestamps.

    Instances are immutable. Equality and hashing are based on interval
    identity (``start`` and ``end``). To compare or sort durations, use
    ``span.duration``.

    Attributes
    ----------
    duration : int
        Elapsed time in nanoseconds (end - start). Set in ``__post_init__``.
    start : int
        Start timestamp in nanoseconds.
    end : int
        End timestamp in nanoseconds.
    timedelta : timedelta
        Read-only. Duration as a ``datetime.timedelta``; nanoseconds are
        converted to whole microseconds (``duration // 1000``) to match
        timedelta's resolution.

    Raises
    ------
    ValueError
        If ``end < start``.

    """

    duration: int = field(init=False)
    start: int
    end: int

    def __post_init__(self) -> None:
        """Validate end >= start, then set duration (nanoseconds)."""
        if self.end < self.start:
            msg = "end must be >= start"
            raise ValueError(msg)
        object.__setattr__(self, "duration", self.end - self.start)

    @property
    def timedelta(self) -> timedelta:
        """Duration as a datetime.timedelta."""
        return timedelta(microseconds=self.duration // 1000)


@dataclass
class Measurement:
    """A single measurement record: wall time, CPU time, and optional metadata.

    Use this to collect the result of a single timing run: wall-clock time,
    CPU time, and any user-defined metadata.

    When created by Timer (context manager or decorator), ``wall_time`` and
    ``cpu_time`` are ``None`` until the block exits, then they are set to the
    measured spans.

    Attributes
    ----------
    wall_time : TimeSpan or None
        Wall-clock time for the measurement, or ``None`` if not yet set.
    cpu_time : TimeSpan or None
        CPU time for the measurement, or ``None`` if not yet set.
    metadata : dict
        Optional key-value metadata (e.g., tags, run id). Defaults to ``{}``;
        mutate in place to add or change entries.

    """

    wall_time: TimeSpan | None = None
    cpu_time: TimeSpan | None = None
    metadata: dict[str, object] = field(default_factory=dict)


class _ContextMode(Enum):
    """Sync vs async execution context for timer stack ownership."""

    SYNC = "sync"
    ASYNC = "async"


# pylint: disable=too-few-public-methods
class _TimedCallable(Protocol[P, R_co]):
    measurements: deque[Measurement]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class Timer:
    """Times execution and records wall-clock and CPU time per run.

    Use as a context manager (``with Timer() as m:`` or ``async with
    Timer() as m:``) to time a block: on exit, the yielded
    :class:`Measurement` has its ``wall_time`` and ``cpu_time`` set.

    Use as a decorator (``@Timer()`` or ``@Timer(metadata={...},
    maxlen=100)``) to time each call: supports sync and async functions and
    generators; one :class:`Measurement` per run is appended to the wrapped
    callable's ``measurements`` deque.

    Parameters
    ----------
    metadata : dict or None, optional
        Key-value metadata for the measurement(s). Stored by reference; each
        measurement gets a shallow copy at enter time. Defaults to ``{}``.
    on_start : callable or None, optional
        Called once per measurement when timing is about to start. Receives the
        :class:`Measurement` (with ``metadata`` set; ``wall_time`` and
        ``cpu_time`` are ``None``). Use for logging or setting up external span
        context. Defaults to ``None``.
    on_end : callable or None, optional
        Called once per measurement when timing has just ended. Receives the
        :class:`Measurement` with ``wall_time`` and ``cpu_time`` set. Use for
        logging duration, sending to OpenTelemetry, or enqueueing to a metrics
        pipeline. Defaults to ``None``.
    maxlen : int or None, optional
        Only used in decorator mode. Maximum number of measurements to keep on
        the wrapped callable. Ignored when used as a context manager. Defaults
        to ``None`` (unbounded).

    Notes
    -----
    One context variable is used for both sync and async; each thread (sync)
    or asyncio task (async) has its own stack, so concurrent async tasks
    sharing one Timer get correct timings regardless of finish order.

    Callbacks are synchronous only. For async exporters (e.g. OpenTelemetry),
    schedule work from the callback (e.g. ``asyncio.create_task(export(m))``
    when in an async context, or a thread/queue).

    Yields (context manager)
    -----------------------
    Measurement
        The measurement record. ``wall_time`` and ``cpu_time`` are set on block
        exit.

    Attributes (decorator mode, on wrapped callable)
    -----------------------------------------------
    measurements : deque of Measurement
        Deque of measurements (oldest to newest).

    Examples
    --------
    Context manager::

        with Timer() as m:
            pass  # code block to be measured
        print(m.wall_time.timedelta)

    Decorator::

        @Timer()
        def func():
            return
        func()
        print(func.measurements[-1].wall_time.timedelta)

    """

    def __init__(
        self,
        *,
        metadata: dict[str, object] | None = None,
        on_start: Callable[[Measurement], None] | None = None,
        on_end: Callable[[Measurement], None] | None = None,
        maxlen: int | None = None,
    ) -> None:
        """Init with optional metadata, callbacks, and maxlen (decorator)."""
        # Store base metadata used to seed each new measurement.
        self._metadata = metadata if isinstance(metadata, dict) else {}

        # Register lifecycle callbacks invoked at measurement start/end.
        self._on_start = on_start
        self._on_end = on_end

        # Keep decorator-mode retention policy for wrapped call history.
        self._maxlen = maxlen

        # Create per-instance context-local stack storage for active timings.
        self._stack_var: ContextVar[
            tuple[int | None, deque[tuple[Measurement, int, int]] | None]
        ] = ContextVar(f"timerun_timer_stack_{id(self)}")

    def _get_context_stack(
        self,
        mode: _ContextMode,
    ) -> deque[tuple[Measurement, int, int]]:
        """Return the stack for the current execution context.

        "Owner" is the execution identity that owns the stack: thread id in
        sync mode, task id in async mode. See :class:`_ContextMode`.
        Binds (owner_id, stack) for this context when the context has no
        bound stack yet (e.g. first use in this thread/task), so callers
        always get the stack for this owner (possibly empty).

        Parameters
        ----------
        mode : _ContextMode
            SYNC for thread-local, ASYNC for task-local stack.

        Returns
        -------
        deque
            The stack for this owner.

        Raises
        ------
        RuntimeError
            If mode is ASYNC and there is no current asyncio task.

        """
        # Resolve owner id for this context (thread or task).
        if mode is _ContextMode.ASYNC:
            task = current_task()
            if task is None:
                msg = "no current asyncio task"
                raise RuntimeError(msg)
            owner_id = id(task)
        else:
            owner_id = id(current_thread())

        # Get or bind stack for this context and return it.
        owner, stack = self._stack_var.get((None, None))
        if owner != owner_id or stack is None:
            stack = deque()
            self._stack_var.set((owner_id, stack))
        return stack

    def _enter(self, mode: _ContextMode) -> Measurement:
        """Start a measurement and push it onto the context stack.

        Returns
        -------
        Measurement
            Newly created measurement record for this enter operation.

        """
        # Create measurement and run on_start callback if set.
        measurement = Measurement(metadata=self._metadata.copy())
        if self._on_start is not None:
            self._on_start(measurement)

        # Push onto context stack and return.
        stack = self._get_context_stack(mode)
        wall_start = perf_counter_ns()
        cpu_start = (
            thread_time_ns()
            if mode is _ContextMode.SYNC
            else process_time_ns()
        )
        stack.append((measurement, wall_start, cpu_start))
        return measurement

    def _exit(self, mode: _ContextMode) -> None:
        """Finalize and pop the latest measurement from the context stack.

        Raises
        ------
        RuntimeError
            If no matching active measurement (e.g. exit without enter).

        """
        # Capture end timestamps before popping.
        cpu_end = (
            thread_time_ns()
            if mode is _ContextMode.SYNC
            else process_time_ns()
        )
        wall_end = perf_counter_ns()

        # Pop measurement or raise if no matching enter.
        stack = self._get_context_stack(mode)
        if not stack:
            msg = "__exit__ called without a matching __enter__"
            raise RuntimeError(msg)
        measurement, wall_start, cpu_start = stack.pop()

        # Set spans on measurement and run on_end callback if set.
        measurement.wall_time = TimeSpan(start=wall_start, end=wall_end)
        measurement.cpu_time = TimeSpan(start=cpu_start, end=cpu_end)
        if self._on_end is not None:
            self._on_end(measurement)

    def __enter__(self) -> Measurement:
        """Start timing; return the measurement record."""
        return self._enter(_ContextMode.SYNC)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Stop timing; update the measurement."""
        self._exit(_ContextMode.SYNC)
        return False

    async def __aenter__(self) -> Measurement:
        """Start timing (async); return the measurement record."""
        return self._enter(_ContextMode.ASYNC)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Stop timing (async); update the measurement."""
        self._exit(_ContextMode.ASYNC)
        return False

    @overload
    def __call__(
        self,
        f: Callable[P, AsyncGenerator[Y, None]],
    ) -> _TimedCallable[P, AsyncGenerator[Y, None]]: ...

    @overload
    def __call__(
        self,
        f: Callable[P, Generator[Y, None, None]],
    ) -> _TimedCallable[P, Generator[Y, None, None]]: ...

    @overload
    def __call__(
        self,
        f: Callable[P, R],
    ) -> _TimedCallable[P, R]: ...

    def __call__(  # noqa: C901
        self,
        f: Callable[P, R],
    ) -> _TimedCallable[P, R]:
        """When given a callable, wrap it with timing (decorator usage)."""
        # Shared state and helper for all wrapper branches.
        measurements: deque[Measurement] = deque(maxlen=self._maxlen)
        lock = Lock()

        def append_measurement(m: Measurement) -> None:
            with lock:
                measurements.append(m)

        # Build wrapper by callable type: async gen, coroutine, sync gen, sync.
        if isasyncgenfunction(f):

            @wraps(f)
            async def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> AsyncGenerator[Y, None]:
                inner = cast(
                    "Callable[P, AsyncGenerator[Y, None]]",
                    f,
                )(*args, **kwargs)
                recorded: list[Measurement] = []
                try:
                    async with self as m:
                        recorded.append(m)
                        async for x in inner:
                            yield x
                finally:
                    if recorded:
                        append_measurement(recorded[0])

        elif iscoroutinefunction(f):

            @wraps(f)
            async def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                m: Measurement | None = None
                try:
                    async with self as m:
                        return cast("R", await f(*args, **kwargs))
                finally:
                    if m is not None:
                        append_measurement(m)

        elif isgeneratorfunction(f):

            @wraps(f)
            def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> Generator[Y, None, None]:
                inner = cast(
                    "Callable[P, Generator[Y, None, None]]",
                    f,
                )(*args, **kwargs)
                recorded: list[Measurement] = []
                try:
                    with self as m:
                        recorded.append(m)
                        yield from inner
                finally:
                    if recorded:
                        append_measurement(recorded[0])

        else:

            @wraps(f)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                m: Measurement | None = None
                try:
                    with self as m:
                        return f(*args, **kwargs)
                finally:
                    if m is not None:
                        append_measurement(m)

        # Attach measurements to wrapper and return.
        wrapped = cast(
            "_TimedCallable[P, R]",
            wrapper,
        )
        wrapped.measurements = measurements
        return wrapped
