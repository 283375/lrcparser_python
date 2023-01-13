import pytest

from lrcparser import LyricLine, LrcParser, TRANSLATION_DIVIDER
from datetime import timedelta

test_LyricLine = LyricLine(
    start_timedelta=timedelta(seconds=5, milliseconds=593),
    text="This is a test line.",
    offset_ms=50,
    translations=["这是测试。"],
)


class TestLyricLine:
    def test_get_time(self):
        assert test_LyricLine.get_time() == {
            "minutes": 0,
            "seconds": 5,
            "microseconds": 593000,
        }

    def test_to_str(self):
        assert test_LyricLine.to_str() == "[00:05.59]This is a test line."
        assert (
            test_LyricLine.to_str(ms_digits=3, translations=True)
            == f"[00:05.593]This is a test line.{TRANSLATION_DIVIDER}这是测试。"
        )
        assert (
            test_LyricLine.to_str(
                ms_digits=5, translations=True, translation_divider=" /|\\"
            )
            == "[00:05.59300]This is a test line. /|\\这是测试。"
        )

    def test_format_functions(self):
        assert str(test_LyricLine) == test_LyricLine.to_str()
        assert int(test_LyricLine) == 5593
        assert float(test_LyricLine) == 5593.000


parser = LrcParser()
with open("example.lrc", "r", encoding="utf-8") as lrcFile:
    result = parser.parse(lrcFile.read())


class TestParser:
    def test_parse(self):
        expectedLyricLine = LyricLine(
            start_timedelta=timedelta(seconds=28, microseconds=330000),
            text="Line 4 with TRANSLATION! COOL!!!",
        )
        assert result["lyric_lines"][3].text == expectedLyricLine.text
        assert (
            result["lyric_lines"][3].start_timedelta
            == expectedLyricLine.start_timedelta
        )
        assert (
            result["lyric_lines"][5].start_timedelta
            == result["lyric_lines"][6].start_timedelta
        )
        assert result["attributes"] == [
            {"name": "ti", "value": "test_lyric"},
            {"name": "ar", "value": "283375"},
            {"name": "al", "value": "TEST ~エラーを回避するための最良の方法~"},
            {"name": "by", "value": "283375"},
            {"name": "OFFset", "value": "250"},
        ]

    def test_offset(self):
        offsetLines = parser.apply_global_offset(
            result["lyric_lines"], result["global_offset"]
        )
        assert offsetLines[0].offset_ms == 250
        assert offsetLines[0].offset_timedelta == timedelta(
            seconds=0, milliseconds=20 + 250
        )

    def test_find_duplicate(self):
        dups = parser.find_duplicate(result["lyric_lines"])
        assert dups[0][0].text == "Line 4 with TRANSLATION! COOL!!!"
        assert dups[0][1].start_timedelta == timedelta(seconds=28, microseconds=330000)
        assert dups[1][0].text == "Sad because secs < 60"

    def test_combine_translation(self):
        translations = parser.combine_translation(result["lyric_lines"])
        assert translations[0].text == "Line 4 with TRANSLATION! COOL!!!"
        assert translations[0].translations == ["这行有翻译！真他妈的酷！！！"]
        assert translations[1].text == "Sad because secs < 60"
        assert translations[1].translations == [
            "But we can change the rules :)",
            "我只是来凑数的",
        ]
