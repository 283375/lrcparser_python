import re
from datetime import timedelta
from typing import Literal, TypedDict

LRC_REGEX = r"(?P<time>\[(?P<minutes>\d{2}):(?P<seconds>\d{2})\.(?P<milliseconds>\d{2,3})\])(?P<text>.*)"
ATTR_REGEX = r"\[(?P<name>[^\d]+):[\x20]*(?P<value>.+)\]"
TRANSLATION_DIVIDER = " | "


class LrcLine:
    """
    Represents a lyric line

    Take `[00:01.26]Lyric text` for example.
    :param start_timedelta: The start time of the lyric, `[00:01.26]`Lyric text
    :type start_timedelta: timedelta
    :param text: The text of the lyric. [00:01.26]`Lyric text`
    :type text: str
    :param offset_ms: The offset of the lyric line, defaults to `0`
    :type offset_ms: int, optional
    :param translations: The translations, defaults to None
    :type translations: list or None, optional
    """

    def __init__(
        self,
        start_timedelta: timedelta,
        text: str,
        offset_ms: int = 0,
        translations: list[str] | None = None,
    ):
        self.start_timedelta = start_timedelta
        self.text = text
        self.offset_ms = offset_ms
        self.translations = translations

    # This is something like computed(() => ...) in Vue.js, which I like a lot.
    @property
    def offset_timedelta(self):
        return self.start_timedelta + timedelta(milliseconds=self.offset_ms)

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
        ms_digits: int = 2,
        translations: bool = False,
        translation_divider: str = TRANSLATION_DIVIDER,
    ) -> str:
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
        >>> line.to_str(ms_digits=3, translations=True, translation_divider='///')
        '[00:25.478]Line 1///行 1'

        """
        time = self.get_time()
        time_str = "{}:{}.{}".format(
            str(time["minutes"]).zfill(2),
            str(time["seconds"]).zfill(2),
            str(time["microseconds"] // int("1".ljust(7 - ms_digits, "0"))).rjust(
                ms_digits, "0"
            ),
        )
        translation_str = ""

        if translations and self.translations:
            for translation in self.translations:
                translation_str += f"{translation_divider}{translation}"
        return f"[{time_str}]{self.text}{translation_str}"

    def __repr__(self) -> str:
        return f"LrcLine(start_timedelta={repr(self.start_timedelta)}, text={repr(self.text)}, offset_ms={self.offset_ms}, translations={repr(self.translations)})"

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
            repr(self.start_timedelta)
            + self.text
            + str(self.offset_ms)
            + "".join(self.translations or [])
        )
        return hash(unique_str)

    def __eq__(self, other: object) -> bool:
        return (
            self.__hash__() == other.__hash__()
            if isinstance(other, self.__class__)
            else False
        )


class LrcParser:
    class ParseResult(TypedDict):
        global_offset: int
        lrc_lines: list[LrcLine]
        attributes: list[dict[Literal["name", "value"], str]]

    @classmethod
    def parse(
        cls,
        s: str,
        parse_translations: bool = False,
        translation_divider: str = TRANSLATION_DIVIDER,
    ) -> ParseResult:
        """
        Parse lyrics from a string.

        :param s: The lyric string, e.g.'[00:01.25]Lyric'.
        :type s: str
        :param parse_translations: Defaults to False, see examples for details
        :type parse_translations: bool, optional
        :param translation_divider: Defaults to TRANSLATION_DIVIDER, see examples for details
        :type translation_divider: str, optional
        :return: A dictionary contains `lyricLines` and `attributes` of the lyric.
        :rtype: dict

        >>> s = '''[ti: TEST]
        ... [ar: 283375]
        ... [al: TEST ~AN EXAMPLE FOR YOU~]
        ... [by: 283375]
        ...
        ... [00:05.26]Line 1 example
        ... [00:07.36]Line 2 example | 翻译示例
        ... [00:09.54]Line 3 divider example /// 分隔符示例'''

        >>> LrcParser.parse(s) == {
        ...     'global_offset': 0,
        ...     'lrc_lines': [
        ...         LrcLine(text="Line 1 example", start_timedelta=timedelta(seconds=5, milliseconds=260), ),
        ...         LrcLine(text="Line 2 example | 翻译示例", start_timedelta=timedelta(seconds=7, milliseconds=360), ),
        ...         LrcLine(text="Line 3 divider example /// 分隔符示例", start_timedelta=timedelta(seconds=9, milliseconds=540), )
        ...     ],
        ...     'attributes': [
        ...         {'name': 'ti', 'value': 'TEST'},
        ...         {'name': 'ar', 'value': '283375'},
        ...         {'name': 'al', 'value': 'TEST ~AN EXAMPLE FOR YOU~'},
        ...         {'name': 'by', 'value': '283375'}
        ...     ]
        ... }
        True

        >>> LrcParser.parse(s, parse_translations=True)['lrc_lines'] == [
        ...     LrcLine(text="Line 1 example", start_timedelta=timedelta(seconds=5, milliseconds=260)),
        ...     LrcLine(text="Line 2 example", translations=['翻译示例'], start_timedelta=timedelta(seconds=7, milliseconds=360)),
        ...     LrcLine(text="Line 3 divider example /// 分隔符示例", start_timedelta=timedelta(seconds=9, milliseconds=540))
        ... ]
        True

        >>> LrcParser.parse(s, parse_translations=True, translation_divider=' /// ')['lrc_lines'] == [
        ...     LrcLine(text="Line 1 example", start_timedelta=timedelta(seconds=5, milliseconds=260)),
        ...     LrcLine(text="Line 2 example | 翻译示例", start_timedelta=timedelta(seconds=7, milliseconds=360)),
        ...     LrcLine(text="Line 3 divider example", translations=['分隔符示例'], start_timedelta=timedelta(seconds=9, milliseconds=540))
        ... ]
        True

        """
        lines = s.splitlines()
        lrc_lines = []
        attributes = []
        global_offset = 0

        for line in lines:
            attribute_re_result = re.match(ATTR_REGEX, line)
            lrc_re_result = re.match(LRC_REGEX, line)

            if attribute_re_result:
                if attribute_re_result["name"].lower() == "offset":
                    global_offset = int(attribute_re_result["value"])

                attributes.append(
                    {
                        "name": attribute_re_result["name"],
                        "value": attribute_re_result["value"],
                    }
                )

            if lrc_re_result:
                # adapt lyrics like [01:02.345678] (will this kind of lyric even exist?)
                milliseconds = lrc_re_result["milliseconds"]
                if len(milliseconds) <= 3:
                    microseconds = milliseconds.ljust(6, "0")
                else:
                    microseconds = milliseconds

                start_timedelta = timedelta(
                    minutes=int(lrc_re_result["minutes"]),
                    seconds=int(lrc_re_result["seconds"]),
                    microseconds=int(microseconds),
                )
                orig_text = lrc_re_result["text"]

                if parse_translations:
                    splited_text = orig_text.split(translation_divider)
                    lrc_lines.append(
                        LrcLine(
                            start_timedelta=start_timedelta,
                            text=splited_text[0],
                            translations=splited_text[1:] or None,
                        )
                    )
                else:
                    lrc_line = LrcLine(
                        start_timedelta=start_timedelta,
                        text=orig_text,
                    )
                    lrc_lines.append(lrc_line)

        if parse_translations:
            lrc_lines = cls.combine_translation(lrc_lines)

        return {
            "global_offset": global_offset,
            "lrc_lines": lrc_lines,
            "attributes": attributes,
        }

    @classmethod
    def apply_global_offset(
        cls, lrc_lines: list[LrcLine], offset: int
    ) -> list[LrcLine]:
        ret = []
        for lrc_line in lrc_lines:
            lrc_line.offset_ms = offset
            ret.append(lrc_line)
        return ret

    @classmethod
    def find_duplicate(cls, lrc_lines: list[LrcLine]) -> list[list[LrcLine]]:
        """
        find_duplicate finds duplicate lyrics.

        :param lrc_lines: A list of LyricLine.
        :type lrc_lines: list
        :return: A list of duplicate groups, see example for details.
        :rtype: list

        >>> LrcParser.find_duplicate([
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 1'),
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 2'),
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 3'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 4'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 5'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 6'),
        ... ]) == [
        ...      [
        ...          LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 1'),
        ...          LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 2'),
        ...          LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 3'),
        ...      ],
        ...      [
        ...          LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 4'),
        ...          LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 5'),
        ...          LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 6'),
        ...      ]
        ...  ]
        True

        """

        timedelta_dict: dict[timedelta, list[LrcLine]] = {}

        for lrc_line in lrc_lines:
            if timedelta_dict.get(lrc_line.start_timedelta) is None:
                timedelta_dict[lrc_line.start_timedelta] = [lrc_line]
            else:
                timedelta_dict[lrc_line.start_timedelta].append(lrc_line)

        timedelta_dict = dict(filter(lambda x: len(x[1]) > 1, timedelta_dict.items()))
        return list(dict(sorted(timedelta_dict.items(), key=lambda i: i[0])).values())

    @classmethod
    def combine_translation(cls, lrc_lines: list[LrcLine]) -> list[LrcLine]:
        """
        combine_translation analyzes the translation of the lyric.

        :param lrc_lines: A list of LyricLine.
        :type lrc_lines: list
        :return: Processed list of LyricLine, see example for details.
        :rtype: list

        >>> LrcParser.combine_translation([
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 1'),
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='翻译 1'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 2'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='翻译 2'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='これは2行目です'),
        ... ]) == [
        ...     LrcLine(
        ...         start_timedelta=timedelta(seconds=1, milliseconds=589),
        ...         text='Line 1',
        ...         offset_ms=0,
        ...         translations=['翻译 1']),
        ...     LrcLine(
        ...         start_timedelta=timedelta(seconds=2,milliseconds=589),
        ...         text='Line 2',
        ...         offset_ms=0,
        ...         translations=['翻译 2', 'これは2行目です'])
        ... ]
        True

        """
        duplicates = cls.find_duplicate(lrc_lines)
        if len(duplicates) == 0:
            return lrc_lines

        combined_lrcs = []
        for duplicate in duplicates:
            main_lrc_line = duplicate[0]
            lrc_line = LrcLine(
                start_timedelta=main_lrc_line.start_timedelta,
                text=main_lrc_line.text,
                offset_ms=main_lrc_line.offset_ms,
                translations=[lrc_line.text for lrc_line in duplicate[1:]],
            )
            combined_lrcs.append(lrc_line)

        return combined_lrcs
