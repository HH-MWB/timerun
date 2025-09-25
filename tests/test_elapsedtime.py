"""A collection of tests for class ``ElapsedTime``."""

from dataclasses import FrozenInstanceError
from datetime import timedelta

from pytest import raises

from timerun import ElapsedTime


class TestInit:
    """Test suite for Elapsed Time initialization."""

    def test_init_without_keyword(self) -> None:
        """Test initiate ElapsedTime."""
        duration: ElapsedTime = ElapsedTime(1)
        assert duration.nanoseconds == 1

    def test_init_using_keyword(self) -> None:
        """Test initiate ElapsedTime using keyword."""
        duration: ElapsedTime = ElapsedTime(nanoseconds=1)
        assert duration.nanoseconds == 1


class TestImmutable:  # pylint: disable=too-few-public-methods
    """Test ElapsedTime is immutable."""

    def test_modify_after_init(self, elapsed_1_ns: ElapsedTime) -> None:
        """Test modify after initialization.

        ElapsedTime is expected to be immutable. Update attribute after
        would fail and raise ``FrozenInstanceError``.

        Parameters
        ----------
        elapsed_1_ns : ElapsedTime
            A ElapsedTime instance will be using to update attribute.
        """
        with raises(FrozenInstanceError):
            elapsed_1_ns.nanoseconds = 0  # type: ignore
        assert elapsed_1_ns.nanoseconds == 1


class TestComparable:
    """Test ElapsedTime is comparable."""

    def test_equal(self) -> None:
        """Test '==' operator for ElapsedTime."""
        assert ElapsedTime(nanoseconds=1000) == ElapsedTime(nanoseconds=1000)

    def test_not_equal(self) -> None:
        """Test '!=' operator for ElapsedTime."""
        assert ElapsedTime(nanoseconds=1000) != ElapsedTime(nanoseconds=2000)

    def test_greater_than(self) -> None:
        """Test '>' operator for ElapsedTime."""
        assert ElapsedTime(nanoseconds=2000) > ElapsedTime(nanoseconds=1000)

    def test_smaller_than(self) -> None:
        """Test '<' operator for ElapsedTime."""
        assert ElapsedTime(nanoseconds=1000) < ElapsedTime(nanoseconds=2000)

    def test_greater_or_equal(self) -> None:
        """Test '>=' operator for ElapsedTime."""
        assert ElapsedTime(nanoseconds=1000) >= ElapsedTime(nanoseconds=1000)
        assert ElapsedTime(nanoseconds=2000) >= ElapsedTime(nanoseconds=1000)

    def test_smaller_or_equal(self) -> None:
        """Test '<=' operator for ElapsedTime."""
        assert ElapsedTime(nanoseconds=1000) <= ElapsedTime(nanoseconds=1000)
        assert ElapsedTime(nanoseconds=1000) <= ElapsedTime(nanoseconds=2000)


class TestTimedeltaAttribute:
    """Test using timedelta attribute."""

    def test_microseconds_accuracy(self, elapsed_1_ms: ElapsedTime) -> None:
        """Test using ElapsedTime of 1 microsecond.

        Given ElapsedTime of ``1`` microsecond, expected timedelta is
        ``1`` microsecond.

        Parameters
        ----------
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        """
        assert elapsed_1_ms.timedelta == timedelta(microseconds=1)

    def test_nanoseconds_accuracy(
        self, elapsed_1_pt_5_ms: ElapsedTime
    ) -> None:
        """Test using ElapsedTime of 1.5 microseconds.

        Given ElapsedTime of ``1.5`` microseconds expected timedelta to
        be ``1`` microsecond, because of the accuracy lost.

        Parameters
        ----------
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """
        assert elapsed_1_pt_5_ms.timedelta == timedelta(microseconds=1)


class TestStr:
    """Test suite for calling str function on ElapsedTime."""

    def test_elapsed_time_seconds_as_decimals(
        self, elapsed_100_ns: ElapsedTime
    ) -> None:
        """Test elapsed time in seconds is in decimal.

        Given an elapsed time, expected to see the part after seconds as
        a decimal part.

        Parameters
        ----------
        elapsed_100_ns : ElapsedTime
            Elapsed Time to be used to call ``str``.
        """
        assert str(elapsed_100_ns) == "0:00:00.000000100"

    def test_elapsed_time_seconds_as_integer(
        self, elapsed_1_sec: ElapsedTime
    ) -> None:
        """Test elapsed time in seconds is an integer.

        Given an elapsed time in integer seconds, the decimal part
        should be hidden.

        Parameters
        ----------
        elapsed_1_sec : ElapsedTime
            Elapsed Time to be used to call ``str``.
        """
        assert str(elapsed_1_sec) == "0:00:01"


class TestRepr:  # pylint: disable=too-few-public-methods
    """Test suite for calling repr function on ElapsedTime."""

    def test_repr(self, elapsed_100_ns: ElapsedTime) -> None:
        """Test call function repr.

        Given an ElapsedTime, call repr would get an output can be used
        to re-create this ElapsedTime.

        Parameters
        ----------
        elapsed_100_ns : ElapsedTime
            Elapsed Time to be used to call ``repr``.
        """
        assert repr(elapsed_100_ns) == "ElapsedTime(nanoseconds=100)"
