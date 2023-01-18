from lrcparser import LrcLine, LrcParser
from datetime import timedelta

with open("example.lrc", "r", encoding="utf-8") as lrc_file:
    result = LrcParser.parse(lrc_file.read())


class Test_LrcParser:
    def test_parse(self):
        expected_lrc_line = LrcLine(
            start_timedelta=timedelta(seconds=28, microseconds=330000),
            text="Line 4 with TRANSLATION! COOL!!!",
        )
        assert result["lrc_lines"][3] == expected_lrc_line
        assert (
            result["lrc_lines"][5].start_timedelta
            == result["lrc_lines"][6].start_timedelta
        )
        assert result["attributes"] == {
            "ti": "test_lyric",
            "ar": "283375",
            "al": "TEST ~エラーを回避するための最良の方法~",
            "by": "283375",
            "offset": "250",
        }

    def test_find_duplicate(self):
        dups = LrcParser.find_duplicate(result["lrc_lines"])
        assert dups[0][0].text == "Line 4 with TRANSLATION! COOL!!!"
        assert dups[0][1].start_timedelta == timedelta(seconds=28, microseconds=330000)
        assert dups[1][0].text == "Sad because secs < 60"

    def test_combine_translation(self):
        translations = LrcParser.combine_translation(result["lrc_lines"])
        assert translations[0].text == "Line 4 with TRANSLATION! COOL!!!"
        assert translations[0].translations == ["这行有翻译！真他妈的酷！！！"]
        assert translations[1].text == "Sad because secs < 60"
        assert translations[1].translations == [
            "But we can change the rules :)",
            "我只是来凑数的",
        ]
