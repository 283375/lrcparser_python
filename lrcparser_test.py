import pytest

from lrcparser import LyricLine, LrcParser
from _default import LRCPARSER_DEFAULT_TRANSLATION_DIVIDER
from datetime import timedelta

test_LyricLine = LyricLine(
    startTimedelta=timedelta(seconds=5, milliseconds=593),
    text="This is a test line.",
    offsetMs=50,
    translation="这是测试。",
)


class TestLyricLine:
    def test_get_time(self):
        assert test_LyricLine.getTime() == {
            "minutes": 0,
            "seconds": 5,
            "microseconds": 593000,
        }

    def test_to_str(self):
        assert test_LyricLine.toStr() == "[00:05.59]This is a test line."
        assert test_LyricLine.toStr(
            msDigits=3, withTranslation=True
        ) == "[00:05.593]This is a test line.{}这是测试。".format(
            LRCPARSER_DEFAULT_TRANSLATION_DIVIDER
        )
        assert (
            test_LyricLine.toStr(
                msDigits=5, withTranslation=True, translationDivider=" /|\\"
            )
            == "[00:05.59300]This is a test line. /|\\这是测试。"
        )

    def test_format_functions(self):
        assert str(test_LyricLine) == test_LyricLine.toStr()
        assert int(test_LyricLine) == 5593
        assert float(test_LyricLine) == 5593.000


parser = LrcParser()
with open("example.lrc", "r", encoding="utf-8") as lrcFile:
    result = parser.parse(lrcFile.read())


class TestParser:
    def test_parse(self):
        expectedLyricLine = LyricLine(
            startTimedelta=timedelta(seconds=28, microseconds=330000),
            text="Line 4 with TRANSLATION! COOL!!!",
        )
        assert result["lyricLines"][3].text == expectedLyricLine.text
        assert (
            result["lyricLines"][3].startTimedelta == expectedLyricLine.startTimedelta
        )
        assert (
            result["lyricLines"][5].startTimedelta
            == result["lyricLines"][6].startTimedelta
        )
        assert result["attributes"] == [
            {"name": "ti", "attr": "test_lyric"},
            {"name": "ar", "attr": "283375"},
            {"name": "al", "attr": "TEST ~THE BEST WAY TO AVOID ERRORS~"},
            {"name": "by", "attr": "283375"},
        ]

    def test_find_duplicate(self):
        dups = parser.findDuplicate(result["lyricLines"])
        assert dups[0][0].text == "Line 4 with TRANSLATION! COOL!!!"
        assert dups[0][1].startTimedelta == timedelta(seconds=28, microseconds=330000)
        assert dups[1][0].text == "Sad because secs < 60"

    def test_combine_translation(self):
        translations = parser.combineTranslation(result["lyricLines"])
        assert translations[0].text == "Line 4 with TRANSLATION! COOL!!!"
        assert translations[0].translation == "这行有翻译！真他妈的酷！！！"
        assert translations[1].text == "Sad because secs < 60"
        assert translations[1].translation[0] == "But we can change the rules :)"
        assert translations[1].translation[1] == "我只是来凑数的"
