import re
from datetime import timedelta
from typing import Literal, TypedDict

LRC_REGEX = r"(?P<time>\[(?P<minutes>\d{2}):(?P<seconds>\d{2})\.(?P<milliseconds>\d{2,3})\])(?P<text>.*)"
ATTR_REGEX = r"\[(?P<name>[^\d]+):(?P<value>.+)\]"
TRANSLATION_DIVIDER = " | "


class LyricLine:
    """
    Represents a lyric line

    Take `[00:01.26]Lyric text` for example.
    :param startTimedelta: The start time of the lyric, `[00:01.26]`Lyric text
    :type startTimedelta: datetime.timedelta
    :param text: The text of the lyric. [00:01.26]`Lyric text`
    :type text: str
    :param offsetMs: The offset of the lyric line, defaults to `0`
    :type offsetMs: int, optional
    :param translation: The translation , defaults to None
    :type translation: list, optional
    """

    def __init__(
        self,
        start_timedelta: timedelta,
        text: str,
        offset_ms: int = 0,
        translations: list[str] = None,
    ):
        self.start_timedelta = start_timedelta
        self.text = text
        self.offset_ms = offset_ms
        self.translations = translations

    # This is something like computed(() => ...) in Vue.js, which I like a lot.
    @property
    def offset_timedelta(self):
        return self.start_timedelta + timedelta(milliseconds=self.offset_ms)

    def get_time(self) -> dict:
        """
        getTime returns a dictionary that contains the time of the lyric.

        :return: A dictionary contains `minutes`, `seconds`, and `microseconds`(micro, *not* milli) of the lyric
        :rtype: dict

        >>> getTime(LyricLine(startTimedelta=datetime.timedelta(minutes=3, seconds=28, milliseconds=492)))
        {"minutes": 3, "seconds": 28, "microseconds": 492000}

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
        toStr returns the string format of the lyric.

        :param msDigits: The digits of the microseconds, defaults to 2
        :type msDigits: int, optional
        :param withTranslation: Whether display translation or not, defaults to False
        :type withTranslation: bool, optional
        :param translationDivider: The translation divider, defaults to None
        :type translationDivider: str, optional
        :return: The string format of the lyric
        :rtype: str

        >>> l = LyricLine(text='Line 1', startTimedelta=datetime.timedelta(seconds=25, milliseconds=478), translation='行 1')
        >>> toStr(l)
        '[00:25.47]Line 1'
        >>> toStr(l, msDigits=3, withTranslation=True, translationDivider='///')
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

        if translations:
            for translation in self.translations:
                translation_str += f"{translation_divider}{translation}"
        return f"[{time_str}]{self.text}{translation_str}"

    def __repr__(self) -> str:
        return_str = "LyricLine("
        if self.text:
            return_str += f'text="{self.text}", '
        if self.start_timedelta:
            return_str += f"startTimedelta={repr(self.start_timedelta)}, "
        if self.offset_ms:
            return_str += f"offsetMs={self.offset_ms}, "
        if self.translations:
            return_str += f'translation="{self.translations}", '
        return f"{return_str})"

    def __str__(self) -> str:
        return self.to_str()

    def __int__(self) -> int:
        """
        __int__ returns the total milliseconds of the lyric start time.

        :rtype: int

        >>> l = LyricLine(startTimedelta=datetime.timedelta(seconds=25, milliseconds=485))
        >>> int(l)
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

        >>> l = LyricLine(startTimedelta=datetime.timedelta(seconds=25, microseconds=48525))
        >>> float(l)
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
            str(self.start_timedelta)
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
        lyric_lines: list[LyricLine]
        attributes: list[dict[Literal["name", "value"], str]]

    def parse(
        self,
        contents: str,
        parse_translations: bool = False,
        translation_divider: str = TRANSLATION_DIVIDER,
        translations_at_left: bool = False,
    ) -> ParseResult:
        """
        Parses lyrics from a string.

        * If you want to custom the translation divider, please change the DEFAULT_TRANSLATION_DIVIDER variable.

        :param contents: The lyric string, e.g.'[00:01.25]Lyric'.
        :type contents: str
        :param parseTranslation: Defaults to False, see examples for details
        :type parseTranslation: bool, optional
        :param translationAtLeft: Defaults to False, see examples for details
        :type translationAtLeft: bool, optional
        :return: A dictionary contains `lyricLines` and `attributes` of the lyric.
        :rtype: dict

        >>> lStr = '[ti: TEST]\\n[ar: 283375]\\n[al: TEST ~AN EXAMPLE FOR YOU~]\\n[by:283375]\\n'
        >>> lStr += '[00:05.26]Line 1 example\\n[00:07.36]Line 2 example | 翻译示例\\n'
        >>> lStr += '[00:09.34]换个位置 | Line 3 example\\n'
        >>> parse(lStr)
        {"lyricLines": [
            LyricLine(startTimedelta=..., text='Line 1 example', offsetMs=0),
            LyricLine(startTimedelta=..., text='Line 2 example | 翻译示例', offsetMs=0),
            LyricLine(startTimedelta=..., text='[00:09.34]换个位置 | Line 3 example')
        ], "attributes": [
            {"name": "ti", "values": "TEST"},
            {"name": "ar", "values": "283375"},
            {"name": "al", "values": "TEST ~AN EXAMPLE FOR YOU~"},
            {"name": "by", "values": "283375"},
        ]}

        >>> parse(lStr, parseTranslation=True)
        {"lyricLines": [
            LyricLine(startTimedelta=..., text='Line 1 example', offsetMs=0),
            LyricLine(startTimedelta=..., text='Line 2 example', offsetMs=0, translation='翻译示例'),
            LyricLine(startTimedelta=..., text='换个位置', offsetMs=0, translation='Line 3 example')
        ], "attributes": [...]}

        >>> parse(lStr, parseTranslation=True, translationAtLeft=True)
        {"lyricLines": [
            LyricLine(startTimedelta=..., text='Line 1 example', offsetMs=0),
            LyricLine(startTimedelta=..., text='翻译示例', offsetMs=0, translation='Line 2 example'),
            LyricLine(startTimedelta=..., text='Line 3 example', offsetMs=0, translation='换个位置')
        ], "attributes": [...]}

        """
        contents: list[str] = contents.splitlines()
        lrc_lines = []
        attributes = []
        parsed_lrc_lines = []

        # First loop: find all lyrics and remove them from line array
        for content in contents:
            content_re_result = re.match(LRC_REGEX, content)
            if content_re_result:
                parsed_lrc_lines.append(content)

                if parse_translations:
                    text = content_re_result["text"].split(translation_divider)
                    translation = (
                        text[int(not translations_at_left)] if len(text) > 1 else None
                    )
                    text = text[int(translations_at_left)]
                else:
                    translation = None
                    text = content_re_result["text"]

                # adapt lyrics like [01:02.345678] (will this kind of lyric even exist?)
                milliseconds = content_re_result["milliseconds"]
                if len(milliseconds) <= 3:
                    microseconds = milliseconds.ljust(6, "0")
                else:
                    microseconds = milliseconds

                lrc_line = LyricLine(
                    start_timedelta=timedelta(
                        minutes=int(content_re_result["minutes"]),
                        seconds=int(content_re_result["seconds"]),
                        microseconds=int(microseconds),
                    ),
                    text=text,
                    translations=translation,
                )
                lrc_lines.append(lrc_line)

        global_offset = 0
        # Second loop: find all attributes
        [contents.remove(i) for i in parsed_lrc_lines]
        for content in contents:
            attr = re.match(ATTR_REGEX, content)
            if attr:
                if attr["name"].lower() == "offset":
                    global_offset = int(attr["value"])
                attributes.append({"name": attr["name"], "value": attr["value"]})

        return {
            "global_offset": global_offset,
            "lyric_lines": lrc_lines,
            "attributes": attributes,
        }

    def apply_global_offset(
        self, lyricLines: list[LyricLine], globalOffset: int
    ) -> list[LyricLine]:
        ret = []
        for lyricLine in lyricLines:
            lyricLine.offset_ms = globalOffset
            ret.append(lyricLine)
        return ret

    def find_duplicate(self, lyricLines: list[LyricLine]) -> list[list[LyricLine]]:
        """
        findDuplicate finds duplicate lyrics.

        :param lyricLines: A list of LyricLine.
        :type lyricLines: list
        :return: A list of duplicate groups, see example for details.
        :rtype: list

        >>> findDuplicate([
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 1'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 2'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 3'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 4'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 5'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 6'),
        ])
        [
            [
                LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 1'),
                LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 2'),
                LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 3'),
            ],
            [
                LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 4'),
                LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 5'),
                LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 6'),
            ]
        ]

        """
        parsedLyrics = []
        duplicateGroup = []

        for lyric in lyricLines:
            dupLrc = [
                lyric2
                for lyric2 in lyricLines
                if (
                    lyric != lyric2
                    and lyric2 not in parsedLyrics
                    and lyric.start_timedelta == lyric2.start_timedelta
                )
            ]
            if dupLrc:
                duplicateGroup.append([lyric] + dupLrc)
            parsedLyrics.append(lyric)

        return duplicateGroup

    def combine_translation(self, lyricLines: list[LyricLine]) -> list[LyricLine]:
        """
        combineTranslation analyzes the translation of the lyric.
        * Requires findDuplicate().

        :param lyricLines: A list of LyricLine.
        :type lyricLines: list
        :return: Processed list of LyricLine, see example for details.
        :rtype: list

        >>> combineTranslation([
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 1'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='翻译 1'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 2'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='翻译 2'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='これは2行目です'),
        ])
        [
            LyricLine(
                startTimedelta=datetime.timedelta(seconds=1, milliseconds=589),
                text='Line 1',
                offsetMs=0,
                translation='翻译 1'),
            LyricLine(
                startTimedelta=datetime.timedelta(seconds=2,milliseconds=589),
                text='Line 2',
                offsetMs=0,
                translation=['翻译 2', 'これは2行目です'])
        ]

        """
        duplicates = self.find_duplicate(lyricLines)
        if len(duplicates) == 0:
            return
        # Avoid duplicates
        parsed_lrc_texts = []
        combined_lrcs = []

        for duplicate_group in duplicates:

            is_duplicate = any(
                lyricLine.text in parsed_lrc_texts for lyricLine in duplicate_group
            )
            if is_duplicate:
                continue

            l = LyricLine(
                start_timedelta=duplicate_group[0].start_timedelta,
                text=duplicate_group[0].text,
                offset_ms=duplicate_group[0].offset_ms,
            )

            # Analyze translation
            # if duplicate group contains more than 2 items, that means this line have multiple translations
            translation = []
            for lyricLine in duplicate_group[1:]:
                translationText = lyricLine.text
                translation.append(translationText)
                parsed_lrc_texts.append(translationText)

            l.translations = translation

            combined_lrcs.append(l)
        return combined_lrcs
