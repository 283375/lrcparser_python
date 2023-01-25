from datetime import timedelta
from .constants import MS_DIGITS, LRC_TIMESTAMP
from .types import MsDigitsRange

from typing import NamedTuple


class LrcTimeTuple(NamedTuple):
    minutes: int
    seconds: int
    ms: int


class LrcTime:
    @classmethod
    def get_time_from_timedelta(cls, timedelta: timedelta) -> LrcTimeTuple:
        hours, mins_and_secs = divmod(timedelta.seconds, 3600)
        hours += timedelta.days * 24
        mins, secs = divmod(mins_and_secs, 60)
        mins += hours * 60

        return LrcTimeTuple(mins, secs, timedelta.microseconds)

    @classmethod
    def get_time_from_str(cls, s: str) -> LrcTimeTuple:
        re_match = LRC_TIMESTAMP.search(s)
        if re_match is None:
            raise ValueError(f"Cannot find timestamp in '{s}'.")
        try:
            minutes = int(re_match["min"])
            seconds = int(re_match["sec"])
            microseconds = int(re_match["ms"].ljust(6, "0"))

            time_tuple = cls.get_time_from_timedelta(
                timedelta(
                    minutes=minutes,
                    seconds=seconds,
                    microseconds=microseconds,
                )
            )

            if seconds >= 60 or microseconds > 999999:
                # TODO: use log warning here
                print(f"Got invalid timestamp {s}, converting to {str(cls(time_tuple))}")

            return time_tuple

        except IndexError as e:
            raise ValueError(f"Cannot find timestamp in '{s}'.") from e

    def __init__(
        self,
        arg: timedelta | tuple[int, int, int] | str | int,
        *args: int,
        microsecond: bool = False,
    ):
        """
        __init__

        `microsecond` determines whether the 3rd `int` (or the 3rd element of `tuple`)
        should be considered as microsecond.

        Please notice that `microsecond` does not affect `str` argument.

        >>> time1 = LrcTime(0, 3, 375)  # equals to [00:03.375]
        >>> time1.microseconds
        375000
        >>> time2 = LrcTime(0, 3, 375, microsecond=True)  # equals to [00:03.000375]
        >>> time2.microseconds
        375
        """

        if isinstance(arg, timedelta):
            (
                self.minutes,
                self.seconds,
                self.microseconds,
            ) = self.get_time_from_timedelta(arg)
        elif (
            isinstance(arg, tuple)
            and len(arg) == 3
            and all(isinstance(item, int) for item in arg)
        ):
            self.minutes = arg[0]
            self.seconds = arg[1]
            self.microseconds = arg[2] if microsecond else arg[2] * 1000
        elif isinstance(arg, str):
            (
                self.minutes,
                self.seconds,
                self.microseconds,
            ) = self.get_time_from_str(arg)
        elif (
            isinstance(arg, int)
            and len(args) == 2
            and all(isinstance(item, int) for item in args)
        ):
            self.minutes = arg
            self.seconds = args[0]
            self.microseconds = args[1] if microsecond else args[1] * 1000
        else:
            raise ValueError(f"Invalid argument(s): {repr(args)}.")

    def to_str(self, ms_digits: MsDigitsRange = MS_DIGITS):
        # sourcery skip: use-fstring-for-formatting
        return "{}:{}.{}".format(
            str(self.minutes).rjust(2, "0"),
            str(self.seconds).rjust(2, "0"),
            str(self.microseconds)[:ms_digits],
        )

    def __int__(self) -> int:
        return self.minutes * 60 + self.seconds

    def __float__(self) -> float:
        return self.minutes * 60 + self.seconds + self.microseconds / 1000000

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        if self.microseconds % 1000 == 0:
            return f"{self.__class__.__name__}({self.minutes}, {self.seconds}, {self.microseconds // 1000})"
        return f"{self.__class__.__name__}({self.minutes}, {self.seconds}, {self.microseconds}, microsecond=True)"

    def __tuple__(self) -> tuple[int, int, int]:
        return (self.minutes, self.seconds, self.microseconds)

    def __hash__(self) -> int:
        return hash(
            f"{repr(self.minutes)}_{repr(self.seconds)}_{repr(self.microseconds)}"
        )

    def __eq__(self, other) -> bool:
        return (
            self.__tuple__() == other.__tuple__()
            if isinstance(other, self.__class__)
            else False
        )

    def __lt__(self, other) -> bool:
        return (
            self.__tuple__() < other.__tuple__()
            if isinstance(other, self.__class__)
            else False
        )
