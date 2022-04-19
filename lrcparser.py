from _default import (
    LRCPARSER_DEFAULT_TRANSLATION_DIVIDER,
    LRCPARSER_LRC_REGEX,
    LRCPARSER_ATTR_REGEX,
)
import re
from datetime import timedelta


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
    :type translation: str or list, optional
    """

    def __init__(
        self,
        startTimedelta: timedelta,
        text: str,
        offsetMs: int = 0,
        translation: str or list[str] = None,
    ):
        self.startTimedelta = startTimedelta
        self.text = text
        self.offsetMs = offsetMs
        self.offsetTimedelta = self.startTimedelta + timedelta(milliseconds=offsetMs)
        self.translation = translation

    def getTime(self) -> dict:
        """
        getTime returns a dictionary that contains the time of the lyric.

        :return: A dictionary contains `minutes`, `seconds`, and `microseconds`(micro, *not* milli) of the lyric
        :rtype: dict
        ```
        >>> getTime(LyricLine(startTimedelta=datetime.timedelta(minutes=3, seconds=28, milliseconds=492)))
        <<< {"minutes": 3, "seconds": 28, "microseconds": 492000}
        ```
        """
        timed = self.startTimedelta
        hours, minutesAndSeconds = divmod(timed.seconds, 3600)
        hours += timed.days * 24
        minutes, seconds = divmod(minutesAndSeconds, 60)
        minutes += hours * 60
        return {
            "minutes": minutes,
            "seconds": seconds,
            "microseconds": timed.microseconds,
        }

    def toStr(
        self,
        msDigits: int = 2,
        withTranslation: bool = False,
        translationDivider: str = None,
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
        ```
        l = LyricLine(text='Line 1', startTimedelta=datetime.timedelta(seconds=25, milliseconds=478), translation='行 1')
        >>> toStr(l)
        <<< '[00:25.47]Line 1'
        >>> toStr(l, msDigits=3, withTranslation=True, translationDivider='///')
        <<< '[00:25.478]Line 1///行 1'
        ```
        """
        time = self.getTime()
        timeStr = "{}:{}.{}".format(
            str(time["minutes"]).zfill(2),
            str(time["seconds"]).zfill(2),
            str(time["microseconds"] // int("1".ljust(7 - msDigits, "0"))).rjust(
                msDigits, "0"
            ),
        )
        translationStr = (
            ""
            if not withTranslation
            else "{}{}".format(
                translationDivider or LRCPARSER_DEFAULT_TRANSLATION_DIVIDER,
                self.translation,
            )
        )
        return "[{}]{}{}".format(
            timeStr,
            self.text,
            translationStr,
        )

    def __repr__(self) -> str:
        returnStr = "LyricLine("
        if self.text:
            returnStr += 'text="{}", '.format(self.text)
        if self.startTimedelta:
            returnStr += "startTimedelta={}, ".format(repr(self.startTimedelta))
        if self.offsetMs:
            returnStr += "offsetMs={}, ".format(self.offsetMs)
        if self.translation:
            returnStr += 'translation="{}", '.format(self.translation)
        return returnStr + ")"

    def __str__(self) -> str:
        return self.toStr()

    def __int__(self) -> int:
        """
        __int__ returns the total milliseconds of the lyric start time.

        :rtype: int
        ```
        >>> l = LyricLine(startTimedelta=datetime.timedelta(seconds=25, milliseconds=485))
        >>> int(l)
        <<< 25485
        ```
        """
        time = self.getTime()
        return (
            time["minutes"] * (60 * 1000)
            + time["seconds"] * 1000
            + time["microseconds"] // 1000
        )

    def __float__(self) -> float:
        """
        __float__ returns the total microseconds of the lyric start time.

        :rtype: float
        ```
        >>> l = LyricLine(startTimedelta=datetime.timedelta(seconds=25, microseconds=48525))
        >>> float(l)
        <<< 25048.525
        ```
        """
        time = self.getTime()
        return (
            time["minutes"] * (60 * 1000)
            + time["seconds"] * 1000
            + time["microseconds"] / 1000
        )


class LrcParser:
    def parse(
        self,
        contents: str,
        parseTranslation: bool = False,
        translationAtLeft: bool = False,
    ) -> dict[list[LyricLine], list[dict]]:
        """
        Parses lyrics from a string.

        * If you want to custom the translation divider, please change the LRCPARSER_DEFAULT_TRANSLATION_DIVIDER variable.

        :param contents: The lyric string, e.g.'[00:01.25]Lyric'.
        :type contents: str
        :param parseTranslation: Defaults to False, see examples for details
        :type parseTranslation: bool, optional
        :param translationAtLeft: Defaults to False, see examples for details
        :type translationAtLeft: bool, optional
        :return: A dictionary contains `lyricLines` and `attributes` of the lyric.
        :rtype: dict
        ```
        >>> lStr = '[ti: TEST]\\n[ar: 283375]\\n[al: TEST ~AN EXAMPLE FOR YOU~]\\n[by:283375]\\n'
        >>> lStr += '[00:05.26]Line 1 example\\n[00:07.36]Line 2 example | 翻译示例\\n'
        >>> lStr += '[00:09.34]换个位置 | Line 3 example\\n'
        >>> parse(lStr)
        <<< {"lyricLines": [
            LyricLine(startTimedelta=..., text='Line 1 example', offsetMs=0),
            LyricLine(startTimedelta=..., text='Line 2 example | 翻译示例', offsetMs=0),
            LyricLine(startTimedelta=..., text='[00:09.34]换个位置 | Line 3 example')
        ], "attributes": [
            {"name": "ti", "attr": "TEST"},
            {"name": "ar", "attr": "283375"},
            {"name": "al", "attr": "TEST ~AN EXAMPLE FOR YOU~"},
            {"name": "by", "attr": "283375"},
        ]}
        >>> parse(lStr, parseTranslation=True)
        <<< {"lyricLines": [
            LyricLine(startTimedelta=..., text='Line 1 example', offsetMs=0),
            LyricLine(startTimedelta=..., text='Line 2 example', offsetMs=0, translation='翻译示例'),
            LyricLine(startTimedelta=..., text='换个位置', offsetMs=0, translation='Line 3 example')
        ], "attributes": [...]}
        >>> parse(lStr, parseTranslation=True, translationAtLeft=True)
        <<< {"lyricLines": [
            LyricLine(startTimedelta=..., text='Line 1 example', offsetMs=0),
            LyricLine(startTimedelta=..., text='翻译示例', offsetMs=0, translation='Line 2 example'),
            LyricLine(startTimedelta=..., text='Line 3 example', offsetMs=0, translation='换个位置')
        ], "attributes": [...]}
        ```
        """
        # set offset if exists
        offsetMs = 0
        offsetMatch = re.search(r"\[offset:(?P<offset>\d*)\]", contents, re.I)
        if offsetMatch:
            offsetMs = int(offsetMatch.group("offset"))

        contents = contents.splitlines()
        lyricLines = []
        attributes = []
        parsedLyricLines = []

        # First loop: find all lyrics and remove them from line array
        for content in contents:
            contentMatch = re.match(LRCPARSER_LRC_REGEX, content)
            if contentMatch:
                parsedLyricLines.append(content)

                if parseTranslation:
                    text = contentMatch.group("text").split(" | ")
                    translation = (
                        text[int(not translationAtLeft)] if len(text) > 1 else None
                    )
                    text = text[int(translationAtLeft)]
                else:
                    translation = None
                    text = contentMatch.group("text")

                # adapt lyrics like [01:02.345678] (will this kind of lyric even exist?)
                milliseconds = contentMatch.group("milliseconds")
                if len(milliseconds) <= 3:
                    microseconds = milliseconds.ljust(6, "0")
                else:
                    microseconds = milliseconds

                lyricLine = LyricLine(
                    startTimedelta=timedelta(
                        minutes=int(contentMatch.group("minutes")),
                        seconds=int(contentMatch.group("seconds")),
                        microseconds=int(microseconds),
                    ),
                    text=text,
                    offsetMs=offsetMs,
                    translation=translation,
                )
                lyricLines.append(lyricLine)

        # Second loop: find all attributes
        [contents.remove(i) for i in parsedLyricLines]
        for content in contents:
            attr = re.match(LRCPARSER_ATTR_REGEX, content)
            if attr:
                attributes.append(
                    {
                        "name": attr.group("name"),
                        "attr": attr.group("attr"),
                    }
                )

        return {
            "lyricLines": lyricLines,
            "attributes": attributes,
        }

    def findDuplicate(self, lyricLines: list[LyricLine]) -> list[LyricLine]:
        """
        findDuplicate finds duplicate lyrics.

        :param lyricLines: A list of LyricLine.
        :type lyricLines: list
        :return: A list of duplicate groups, see example for details.
        :rtype: list
        ```
        >>> findDuplicate([
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 1'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 2'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 3'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 4'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 5'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 6'),
        ])
        <<< [
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
        ```
        """
        parsedLyrics = []
        duplicateGroup = []

        for lyric in lyricLines:
            dupLrc = []
            for lyric2 in lyricLines:
                if (
                    lyric != lyric2
                    and lyric2 not in parsedLyrics
                    and lyric.startTimedelta == lyric2.startTimedelta
                ):
                    dupLrc.append(lyric2)
            if len(dupLrc) > 0:
                duplicateGroup.append([lyric] + dupLrc)
            parsedLyrics.append(lyric)

        return duplicateGroup

    def combineTranslation(self, lyricLines: list[LyricLine]) -> list[LyricLine]:
        """
        combineTranslation analyzes the translation of the lyric.
        * Requires findDuplicate().

        :param lyricLines: A list of LyricLine.
        :type lyricLines: list
        :return: Processed list of LyricLine, see example for details.
        :rtype: list
        ```
        >>> combineTranslation([
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='Line 1'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=1, milliseconds=589), text='翻译 1'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='Line 2'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='翻译 2'),
            LyricLine(startTimedelta=datetime.timedelta(seconds=2, milliseconds=589), text='これは2行目です'),
        ])
        <<< [
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
        ```
        """
        duplicates = self.findDuplicate(lyricLines)
        # Avoid duplicates
        parsedLyricTexts = []
        combinedLyrics = []

        if len(duplicates) == 0:
            return
        else:
            for duplicateGroup in duplicates:

                isDuplicate = False
                for lyricLine in duplicateGroup:
                    if lyricLine.text in parsedLyricTexts:
                        isDuplicate = True
                        break
                if isDuplicate:
                    continue

                l = LyricLine(
                    startTimedelta=duplicateGroup[0].startTimedelta,
                    text=duplicateGroup[0].text,
                    offsetMs=duplicateGroup[0].offsetMs,
                )

                # Analyze translation
                # if duplicate group contains more than 2 items, that means this line have multiple translations
                if len(duplicateGroup) > 2:
                    translation = []
                    for lyricLine in duplicateGroup[1:]:
                        translationText = lyricLine.text
                        translation.append(translationText)
                        parsedLyricTexts.append(translationText)
                else:
                    translationText = duplicateGroup[1].text
                    translation = translationText
                    parsedLyricTexts.append(translationText)
                l.translation = translation

                combinedLyrics.append(l)
            return combinedLyrics
