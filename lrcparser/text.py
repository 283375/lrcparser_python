from .time import LrcTime
from .constants import MS_DIGITS
from .types import MsDigitsRange


class LrcTextSegment:
    def __init__(self, time: LrcTime, text: str):
        self.time = time
        self.text = text

    def to_str(
        self,
        ms_digits: MsDigitsRange = MS_DIGITS,
        word_timestamp: bool = False,
        time: LrcTime | None = None,
    ) -> str:
        """
        Convert segment to string.

        `word_timestamp` is used to determine whether the "word" timestamp should be added.

        >>> seg = LrcTextSegment(time=LrcTime(3, 7, 500), text='test')
        >>> seg.to_str()
        'test'
        >>> seg.to_str(word_timestamp=True, time=LrcTime(3, 7, 500))
        '<03:07.50>test'
        """

        return (
            f"<{self.time.to_str(ms_digits)}>{self.text}"
            if word_timestamp or (time and time != self.time)
            else self.text
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(time={repr(self.time)}, text={repr(self.text)})"
        )

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __eq__(self, other):
        return (
            self.__hash__() == other.__hash__()
            if isinstance(other, self.__class__)
            else False
        )

    def __lt__(self, other) -> bool:
        return self.time < other.time if isinstance(other, self.__class__) else False


class LrcText(list):
    def __init__(self, *args: LrcTextSegment):
        super().__init__(args)

    def to_str(
        self: list[LrcTextSegment],
        ms_digits: MsDigitsRange = MS_DIGITS,
        force_word_timestamp: bool | None = None,
        time: LrcTime | None = None,
    ):
        word_timestamp = False

        if force_word_timestamp is not None:
            word_timestamp = force_word_timestamp
        else:
            word_timestamp = len(self) > 1

        return "".join(
            [segment.to_str(ms_digits, word_timestamp, time) for segment in self]
        )

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(tuple(self))})"
