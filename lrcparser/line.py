from datetime import timedelta
from .time import LrcTime, LrcTimeTuple
from .text import LrcTextSegment, LrcText
from .constants import TRANSLATION_DIVIDER, MS_DIGITS
from .types import MsDigitsRange


class LrcLine:
    def __init__(
        self,
        start_time: LrcTime | timedelta | LrcTimeTuple | str,
        text: LrcText | str,
        translations: list[LrcText] | list[str] | None = None,
    ):
        self.start_time = (
            start_time if isinstance(start_time, LrcTime) else LrcTime(start_time)
        )

        self.text: LrcText = (
            LrcText(LrcTextSegment(self.start_time, text))
            if isinstance(text, str)
            else text
        )

        self.translations: list[LrcText] | None = (
            [
                LrcText(LrcTextSegment(self.start_time, item))
                if isinstance(item, str)
                else item
                for item in translations
            ]
            if translations is not None
            else None
        )

    def to_str(
        self,
        force_word_timestamp: bool | None = None,
        ms_digits: MsDigitsRange = MS_DIGITS,
        translations: bool = False,
        translation_divider: str = TRANSLATION_DIVIDER,
    ) -> str:  # sourcery skip: use-fstring-for-formatting
        """
        to_str returns the string format of the lyric.

        >>> line = LrcLine(
        ...     start_time=LrcTime(0, 25, 478),
        ...     text='Line 1',
        ...     translations=['行 1']
        ... )
        >>> line.to_str()
        '[00:25.47]Line 1'
        >>> line.to_str(ms_digits=3, translations=True)
        '[00:25.478]Line 1 | 行 1'
        >>> line.to_str(ms_digits=3, translations=True, translation_divider='///')
        '[00:25.478]Line 1///行 1'
        >>> line.to_str(translations=True, translation_divider='\\n')
        '[00:25.47]Line 1\\n[00:25.47]行 1'

        """
        time_str = f"[{self.start_time.to_str(ms_digits)}]"
        text_list = [self.text.to_str(ms_digits, force_word_timestamp, self.start_time)]

        if translations and self.translations:
            text_list += [
                translation.to_str(ms_digits, force_word_timestamp, self.start_time)
                for translation in self.translations
            ]
            text_list = translation_divider.join(text_list).split("\n")

        return "\n".join(f"{time_str}{text}" for text in text_list)

    def __repr__(self) -> str:
        return f"LrcLine(start_time={repr(self.start_time)}, text={repr(self.text)}, translations={repr(self.translations)})"

    def __str__(self) -> str:
        return self.to_str()

    def __int__(self) -> int:
        """
        __int__ returns the seconds of the lyric start time.

        >>> line = LrcLine(start_time=LrcTime(0, 25, 485), text='')
        >>> int(line)
        25

        """
        return int(self.start_time)

    def __float__(self) -> float:
        """
        __float__ returns the seconds (including microseconds, in decimal form) of the lyric start time.

        >>> line = LrcLine(LrcTime(0, 25, 48525, microsecond=True), text='')
        >>> float(line)
        25.048525

        """
        return float(self.start_time)

    def __hash__(self) -> int:
        unique_str = repr(self.start_time) + repr(self.text) + repr(self.translations)
        return hash(unique_str)

    def __eq__(self, other: object) -> bool:
        return (
            self.__hash__() == other.__hash__()
            if isinstance(other, self.__class__)
            else False
        )

    def __lt__(self, other: object) -> bool:
        return (
            self.start_time < other.start_time
            if isinstance(other, self.__class__)
            else False
        )
