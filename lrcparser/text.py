from typing import Dict, List, Optional

from .constants import MS_DIGITS
from .time import LrcTime
from .types import MsDigitsRange


class LrcTextSegment:
    def __init__(self, time: LrcTime, text: str):
        self.time = time
        self.text = text

    def to_str(
        self,
        ms_digits: MsDigitsRange = MS_DIGITS,
        word_timestamp: bool = False,
        time: Optional[LrcTime] = None,
    ) -> str:
        """
        Convert segment to string.

        `word_timestamp` and `time` is used to determine whether the "word" timestamp should be added.

        >>> seg = LrcTextSegment(time=LrcTime(3, 7, 500), text='test')
        >>> seg.to_str()
        'test'
        >>> seg.to_str(time=LrcTime(4, 7, 500))
        '<03:07.50>test'
        >>> seg.to_str(time=LrcTime(3, 7, 500))
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
        return f"{self.__class__.__name__}({repr(self.time)}, {repr(self.text)})"

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __eq__(self, other):
        return (
            self.time == other.time and self.text == other.text
            if isinstance(other, self.__class__)
            else False
        )

    def __lt__(self, other) -> bool:
        return self.time < other.time if isinstance(other, self.__class__) else False


class LrcText(List[LrcTextSegment]):
    def __init__(self, *args: LrcTextSegment):
        super().__init__(args)

    def to_str(
        self: List[LrcTextSegment],
        ms_digits: MsDigitsRange = MS_DIGITS,
        force_word_timestamp: Optional[bool] = None,
        time: Optional[LrcTime] = None,
    ):
        word_timestamp = False

        if force_word_timestamp is not None:
            word_timestamp = force_word_timestamp
        else:
            word_timestamp = len(self) > 1

        return "".join(
            [segment.to_str(ms_digits, word_timestamp, time) for segment in self]
        )

    def combine_duplicates(self: List[LrcTextSegment]):
        """
        Combines duplicate segments in list.

        >>> text = LrcText(
        ...     LrcTextSegment(LrcTime(0, 3, 750), "Segment 1, "),
        ...     LrcTextSegment(LrcTime(0, 3, 750), "Segment 2."),
        ...     LrcTextSegment(LrcTime(0, 4, 750), "Segment 3"),
        ... )
        >>> text.combine_duplicates()
        >>> text[0] == LrcTextSegment(LrcTime(0, 3, 750), "Segment 1, Segment 2.")
        True
        """
        dedup_dict: Dict[LrcTime, str] = {}

        for segment in self:
            if dedup_dict.get(segment.time) is not None:
                dedup_dict[segment.time] += segment.text
            else:
                dedup_dict[segment.time] = segment.text

        self.clear()
        self.extend(LrcTextSegment(time, text) for time, text in dedup_dict.items())

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(repr(line) for line in self.__iter__())})"

    def __getitem__(self, key: int) -> LrcTextSegment:
        return super().__getitem__(key)
