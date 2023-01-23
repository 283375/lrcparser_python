from lrcparser import LrcLine, LrcParser, LrcTime, LrcText, LrcTextSegment
from datetime import timedelta

with open("example.lrc", "r", encoding="utf-8") as lrc_file:
    example = lrc_file.read()

with open("example_spec.lrc", "r", encoding="utf-8") as lrc_file:
    example_spec = LrcParser.parse(lrc_file.read())

result = LrcParser.parse(example)


class Test_LrcParser_General:
    def test_parse(self):
        assert result["offset"] == 250
        print(result["lrc_lines"][6])
        assert result["lrc_lines"][6] == LrcLine(
            start_time=LrcTime(28, 33, 750),
            text="Line 6",
        )
        assert result["lrc_lines"][4].start_time == result["lrc_lines"][5].start_time
        assert result["attributes"] == {
            "ti": "test_lyric",
            "al": "TEST ~エラーを回避するための最良の方法~",
            "by": "283375",
            "offset": "250",
        }

    def test_find_duplicate(self):
        dups = LrcParser.find_duplicate(result["lrc_lines"])
        assert dups == [
            [
                LrcLine(
                    start_time=LrcTime(0, 28, 330),
                    text="Line 4 with TRANSLATION! COOL!!!",
                ),
                LrcLine(
                    start_time=LrcTime(0, 28, 330),
                    text="这行有翻译！真他妈的酷！！！",
                ),
                LrcLine(
                    start_time=LrcTime(0, 28, 330),
                    text="你说得对，但是《lrcparser》是由……",
                ),
            ]
        ]

    def test_combine_translation(self):
        translations = LrcParser.combine_translation(result["lrc_lines"])
        assert translations == [
            LrcLine(
                start_time=LrcTime(0, 28, 330),
                text="Line 4 with TRANSLATION! COOL!!!",
                translations=["这行有翻译！真他妈的酷！！！", "你说得对，但是《lrcparser》是由……"],
            )
        ]


class Test_LrcParser_Special:
    def test_parse(self):
        pass
