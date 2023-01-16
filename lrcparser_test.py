import unittest
import doctest
from datetime import timedelta

import lrcparser
from lrcparser import LrcLine, LrcParser, TRANSLATION_DIVIDER


class TestCase_LrcLine(unittest.TestCase):
    test_LrcLine = LrcLine(
        start_timedelta=timedelta(seconds=5, milliseconds=593),
        text="This is a test line.",
        translations=["这是测试。"],
    )

    def test_get_time(self):
        self.assertDictEqual(
            self.test_LrcLine.get_time(),
            {
                "minutes": 0,
                "seconds": 5,
                "microseconds": 593000,
            },
        )

    def test_to_str(self):
        self.assertEqual(self.test_LrcLine.to_str(), "[00:05.59]This is a test line.")
        self.assertEqual(
            self.test_LrcLine.to_str(ms_digits=3, translations=True),
            f"[00:05.593]This is a test line.{TRANSLATION_DIVIDER}这是测试。",
        )
        self.assertEqual(
            self.test_LrcLine.to_str(
                ms_digits=5, translations=True, translation_divider=" /|\\"
            ),
            "[00:05.59300]This is a test line. /|\\这是测试。",
        )

    def test_format_functions(self):
        self.assertEqual(str(self.test_LrcLine), self.test_LrcLine.to_str())
        self.assertEqual(int(self.test_LrcLine), 5593)
        self.assertEqual(float(self.test_LrcLine), 5593.000)


with open("example.lrc", "r", encoding="utf-8") as lrc_file:
    result = LrcParser.parse(lrc_file.read())


class TestCase_LrcParser(unittest.TestCase):
    def test_parse(self):
        expected_lrc_line = LrcLine(
            start_timedelta=timedelta(seconds=28, microseconds=330000),
            text="Line 4 with TRANSLATION! COOL!!!",
        )
        self.assertEqual(result["lrc_lines"][3], expected_lrc_line)
        self.assertEqual(
            result["lrc_lines"][5].start_timedelta,
            result["lrc_lines"][6].start_timedelta,
        )
        self.assertDictEqual(
            result["attributes"],
            {
                "ti": "test_lyric",
                "ar": "283375",
                "al": "TEST ~エラーを回避するための最良の方法~",
                "by": "283375",
                "offset": "250",
            },
        )

    def test_find_duplicate(self):
        dups = LrcParser.find_duplicate(result["lrc_lines"])
        self.assertEqual(dups[0][0].text, "Line 4 with TRANSLATION! COOL!!!")
        self.assertEqual(
            dups[0][1].start_timedelta, timedelta(seconds=28, microseconds=330000)
        )
        self.assertEqual(dups[1][0].text, "Sad because secs < 60")

    def test_combine_translation(self):
        translations = LrcParser.combine_translation(result["lrc_lines"])
        self.assertEqual(translations[0].text, "Line 4 with TRANSLATION! COOL!!!")
        self.assertEqual(translations[0].translations, ["这行有翻译！真他妈的酷！！！"])
        self.assertEqual(translations[1].text, "Sad because secs < 60")
        self.assertEqual(
            translations[1].translations,
            [
                "But we can change the rules :)",
                "我只是来凑数的",
            ],
        )


class TestCase_Docstring(unittest.TestCase):
    def test_docstring(self):
        fail_count, test_count = doctest.testmod(lrcparser)
        self.assertEqual(fail_count, 0)


if __name__ == "__main__":
    unittest.main()
