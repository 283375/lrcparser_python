from datetime import timedelta
from typing import NamedTuple, Tuple, Union

from .constants import LRC_TIMESTAMP, MS_DIGITS
from .types import MsDigitsRange


class LrcTimeTuple(NamedTuple):
    minutes: int
    seconds: int
    ms: int


class LrcTime:
    @staticmethod
    def __get_time_from_timedelta(td: timedelta) -> LrcTimeTuple:
        hours, mins_and_secs = divmod(td.seconds, 3600)
        hours += td.days * 24
        mins, secs = divmod(mins_and_secs, 60)
        mins += hours * 60

        return LrcTimeTuple(mins, secs, td.microseconds)

    @classmethod
    def __get_time(cls, minutes: int, seconds: int, microseconds: int):
        # when user input seconds >= 60 or microseconds >= 999999,
        # we should correct it. timedelta made this easy.
        return cls.__get_time_from_timedelta(
            timedelta(minutes=minutes, seconds=seconds, microseconds=microseconds)
        )

    @classmethod
    def __get_time_from_str(cls, s: str) -> LrcTimeTuple:
        re_match = LRC_TIMESTAMP.search(s)

        try:
            assert re_match is not None
            minutes = int(re_match["min"])
            seconds = int(re_match["sec"])
            microseconds = int(re_match["ms"].ljust(6, "0"))

            return cls.__get_time(minutes, seconds, microseconds)
        except IndexError as e:
            raise ValueError(f"Cannot find timestamp in {repr(s)}.") from e

    def __init__(
        self,
        arg: Union[timedelta, Tuple[int, int, int], str, int],
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

        minutes = None
        seconds = None
        microseconds = None

        if isinstance(arg, timedelta):
            (
                minutes,
                seconds,
                microseconds,
            ) = self.__get_time_from_timedelta(arg)
        elif (
            isinstance(arg, tuple)
            and len(arg) == 3
            and all(isinstance(item, int) for item in arg)
        ):
            minutes = arg[0]
            seconds = arg[1]
            microseconds = arg[2] if microsecond else arg[2] * 1000
        elif isinstance(arg, str):
            (
                minutes,
                seconds,
                microseconds,
            ) = self.__get_time_from_str(arg)
        elif (
            isinstance(arg, int)
            and len(args) == 2
            and all(isinstance(item, int) for item in args)
        ):
            minutes = arg
            seconds = args[0]
            microseconds = args[1] if microsecond else args[1] * 1000
        else:
            raise ValueError(f"Invalid argument(s): {repr(args)}.")

        # call __get_time to make sure we're getting valid results
        self.minutes, self.seconds, self.microseconds = self.__get_time(
            minutes, seconds, microseconds
        )

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

    def __tuple__(self) -> Tuple[int, int, int]:
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
