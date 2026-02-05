"""TimeRun is a Python library for time measurements."""

from dataclasses import dataclass, field
from datetime import timedelta

__version__: str = "0.5.0"


@dataclass(order=True, frozen=True)
class TimeSpan:
    """A time interval with start and end timestamps.

    Instances are immutable. Equality and ordering are based only on
    ``duration``; ``start`` and ``end`` are excluded from comparison.

    Attributes
    ----------
    duration : int
        Elapsed time in nanoseconds (end - start). Set in ``__post_init__``,
        not a constructor argument. Used for equality, ordering, and hashing.
    start : int
        Start timestamp in nanoseconds.
    end : int
        End timestamp in nanoseconds.
    timedelta : timedelta
        Read-only. Duration as a ``datetime.timedelta``; nanoseconds are
        converted to whole microseconds (``duration // 1000``) to match
        timedelta's resolution.

    Notes
    -----
    ``start`` and ``end`` use ``field(compare=False)``, so two spans with
    the same length compare equal even if their intervals differ.

    """

    duration: int = field(init=False)
    start: int = field(compare=False)
    end: int = field(compare=False)

    def __post_init__(self) -> None:
        """Set duration to end minus start (nanoseconds)."""
        object.__setattr__(self, "duration", self.end - self.start)

    @property
    def timedelta(self) -> timedelta:
        """Duration as a datetime.timedelta."""
        return timedelta(microseconds=self.duration // 1000)


@dataclass
class Measurement:
    """A measurement collection: wall time, CPU time, and optional metadata.

    Stores one measurement only. Use this to collect the result of a single
    timing run: wall-clock time, CPU time, and any user-defined metadata.

    Attributes
    ----------
    wall_time : TimeSpan
        Elapsed (wall-clock) time for the measurement.
    cpu_time : TimeSpan
        CPU time for the measurement.
    metadata : dict
        Optional key-value metadata (e.g., tags, run id). Defaults to ``{}``;
        mutate in place to add or change entries.

    """

    wall_time: TimeSpan
    cpu_time: TimeSpan
    metadata: dict[object, object] = field(default_factory=dict)
