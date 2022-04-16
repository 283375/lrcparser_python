from _default import LRCPARSER_DEFAULT_TRANSLATION_DIVIDER, LRCPARSER_LRC_REGEX, LRCPARSER_ATTR_REGEX
import re
from datetime import timedelta


class LyricLine:
    def __init__(
        self,
        startTimedelta: timedelta,
        text: str,
        offsetMs: int = 0,
        translation: str = None,
    ) -> None:
        self.startTimedelta = startTimedelta
        self.text = text
        self.offsetMs = offsetMs
        self.offsetTimedelta = self.startTimedelta + timedelta(milliseconds=offsetMs)
        self.translation = translation

    def getTime(self):
        timed = self.startTimedelta
        hours, minutesAndSeconds = divmod(timed.seconds, 3600)
        hours += timed.days * 24
        minutes, seconds = divmod(minutesAndSeconds, 60)
        minutes += hours * 60
        return {
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "microseconds": timed.microseconds,
        }

    def toStr(self, msDigits=2, withTranslation=False, translationDivider=None):
        time = self.getTime()
        timeStr = "{}:{}.{}".format(
            str(time["minutes"]).zfill(2),
            str(time["seconds"]).zfill(2),
            str(time["microseconds"] // (1000 * (6 - msDigits))).rjust(msDigits, "0"),
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

    def __str__(self) -> str:
        return self.toStr()

    def __repr__(self) -> str:
        return self.toStr()

    def __int__(self) -> int:
        time = self.getTime()
        return (
            time["minutes"] * (60 * 1000)
            + time["seconds"] * 1000
            + time["microseconds"] // 1000
        )

    def __float__(self) -> float:
        time = self.getTime()
        return (
            time["minutes"] * (60 * 1000)
            + time["seconds"] * 1000
            + time["microseconds"] / 1000
        )


class LrcParser:
    def __init__(self, **kwargs):
        return

    def parse(
        fileObject,
        parseTranslation: bool = False,
        translationAtLeft: bool = False,
    ):
        contents = fileObject.read()

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

                lyricLine = LyricLine(
                    startTimedelta=timedelta(
                        minutes=int(contentMatch.group("minutes")),
                        seconds=int(contentMatch.group("seconds")),
                        milliseconds=int(contentMatch.group("milliseconds").rjust(3, "0")),
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
                attributes.append({
                    "name": attr.group("name"),
                    "attr": attr.group("attr"),
                })
        

        return {
            "lyricLines": lyricLines,
            "attributes": attributes,
        }


a = LyricLine(
    text="hello world",
    startTimedelta=timedelta(days=1, hours=2, minutes=35, seconds=5, microseconds=5),
    translation="你好世界",
)

with open("example.lrc", "r", encoding="utf-8") as lrcF:
    print(LrcParser.parse(lrcF))
