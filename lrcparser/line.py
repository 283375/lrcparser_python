from datetime import timedelta
from .constants import TRANSLATION_DIVIDER

from typing import Literal


class LrcLine:
    """
    Represents a lyric line

    Take `[00:01.26]Lyric text` for example.
    :param start_timedelta: The start time of the lyric, `[00:01.26]`Lyric text
    :type start_timedelta: timedelta
    :param text: The text of the lyric. [00:01.26]`Lyric text`
    :type text: str
    :param translations: The translations, defaults to None
    :type translations: list or None, optional
    """

    def __init__(
        self,
        start_timedelta: timedelta,
        text: str,
        translations: list[str] | None = None,
    ):
        self.start_timedelta = start_timedelta
        self.text = text
        self.translations = translations

    def get_time(self) -> dict[Literal["minutes", "seconds", "microseconds"], int]:
        """
        get_time returns a dict that contains the time of the lyric.

        :return: A dict contains `minutes`, `seconds`, and `microseconds`(micro, *not* milli) of the lyric
        :rtype: dict

        >>> line = LrcLine(start_timedelta=timedelta(minutes=3, seconds=28, milliseconds=492), text='')
        >>> line.get_time() == {'minutes': 3, 'seconds': 28, 'microseconds': 492000}
        True

        """
        hours, mins_and_secs = divmod(self.start_timedelta.seconds, 3600)
        hours += self.start_timedelta.days * 24
        mins, secs = divmod(mins_and_secs, 60)
        mins += hours * 60
        return {
            "minutes": mins,
            "seconds": secs,
            "microseconds": self.start_timedelta.microseconds,
        }

    def to_str(
        self,
        ms_digits: Literal[2, 3] = 2,
        translations: bool = False,
        translation_divider: str = TRANSLATION_DIVIDER,
    ) -> str:  # sourcery skip: use-fstring-for-formatting
        """
        to_str returns the string format of the lyric.

        :param ms_digits: The digits of the microseconds, defaults to 2
        :type ms_digits: int, optional
        :param translations: Whether display translation or not, defaults to False
        :type translations: bool, optional
        :param translation_divider: The translation divider, defaults to None
        :type translation_divider: str, optional
        :return: The string format of the lyric
        :rtype: str

        >>> line = LrcLine(
        ...     start_timedelta=timedelta(seconds=25, milliseconds=478),
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
        time = self.get_time()
        time_str = "[{}:{}.{}]".format(
            str(time["minutes"]).rjust(2, "0"),
            str(time["seconds"]).rjust(2, "0"),
            str(time["microseconds"])[:ms_digits],
        )
        text_list = [self.text]

        if translations and self.translations:
            text_list += self.translations
            text_list = translation_divider.join(text_list).split("\n")

        return "\n".join(f"{time_str}{text}" for text in text_list)

    def __repr__(self) -> str:
        return f"LrcLine(start_timedelta={repr(self.start_timedelta)}, text={repr(self.text)}, translations={repr(self.translations)})"

    def __str__(self) -> str:
        return self.to_str()

    def __int__(self) -> int:
        """
        __int__ returns the total milliseconds of the lyric start time.

        :rtype: int

        >>> line = LrcLine(start_timedelta=timedelta(seconds=25, milliseconds=485), text='')
        >>> int(line)
        25485

        """
        time = self.get_time()
        return (
            time["minutes"] * (60 * 1000)
            + time["seconds"] * 1000
            + time["microseconds"] // 1000
        )

    def __float__(self) -> float:
        """
        __float__ returns the total microseconds of the lyric start time.

        :rtype: float

        >>> line = LrcLine(start_timedelta=timedelta(seconds=25, microseconds=48525), text='')
        >>> float(line)
        25048.525

        """
        time = self.get_time()
        return (
            time["minutes"] * (60 * 1000)
            + time["seconds"] * 1000
            + time["microseconds"] / 1000
        )

    def __hash__(self) -> int:
        unique_str = (
            repr(self.start_timedelta) + self.text + "".join(self.translations or [])
        )
        return hash(unique_str)

    def __eq__(self, other: object) -> bool:
        return (
            self.__hash__() == other.__hash__()
            if isinstance(other, self.__class__)
            else False
        )

    def __lt__(self, other: object) -> bool:
        return (
            self.__float__() < other.__float__()
            if isinstance(other, self.__class__)
            else False
        )
