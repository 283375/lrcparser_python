from lrcparser import LrcLine, LrcParser, LrcTime, LrcText, LrcTextSegment

with open("example.lrc", "r", encoding="utf-8") as lrc_file:
    example = lrc_file.read()


class Test_LrcParser_General:
    result = LrcParser.parse(example)
    result_translation = LrcParser.parse(example, parse_translations=True)

    timestamps = [
        LrcTime(0, 0, 20),
        LrcTime(0, 0, 280),
        LrcTime(0, 2, 830),
        LrcTime(0, 28, 330),
        LrcTime(0, 28, 330),
        LrcTime(0, 28, 330),
        LrcTime(28, 33, 750),
    ]

    def test_parse_attributes(self):
        assert self.result["offset"] == 250
        assert self.result["attributes"] == {
            "ti": "test_lyric",
            "al": "TEST ~AVOIDING ERRORS~",
            "by": "283375",
            "offset": "250",
        }

    def test_parse_lrc_lines(self):
        lrc_lines = self.result["lrc_lines"]

        assert len(lrc_lines) == 7
        for i, line in enumerate(lrc_lines):
            assert line.start_time == self.timestamps[i]
            assert line.translations is None

    def test_parse_lrc_lines_translations(self):
        lrc_lines = self.result_translation["lrc_lines"]

        assert len(lrc_lines) == 5
        assert lrc_lines[3].text == LrcText(
            LrcTextSegment(self.timestamps[3], "Line 4 with translation")
        )
        assert lrc_lines[3].translations is not None
        assert lrc_lines[3].translations == [
            LrcText(LrcTextSegment(self.timestamps[3], "一般大家都这么打翻译")),
            LrcText(LrcTextSegment(self.timestamps[3], "可惜我更喜欢换行")),
            LrcText(LrcTextSegment(self.timestamps[3], "你说得对，但是《lrcparser》是由……")),
        ]

    def test_find_duplicate(self):
        dups = LrcParser.find_duplicate(self.result["lrc_lines"])
        assert dups == [
            [
                LrcLine(
                    start_time=LrcTime(0, 28, 330),
                    text="Line 4 with translation | 一般大家都这么打翻译",
                ),
                LrcLine(
                    start_time=LrcTime(0, 28, 330),
                    text="可惜我更喜欢换行",
                ),
                LrcLine(
                    start_time=LrcTime(0, 28, 330),
                    text="你说得对，但是《lrcparser》是由……",
                ),
            ]
        ]

    def test_combine_translation(self):
        translations = LrcParser.combine_translation(self.result["lrc_lines"])
        assert translations == [
            LrcLine(
                start_time=LrcTime(0, 28, 330),
                text="Line 4 with translation | 一般大家都这么打翻译",
                translations=["可惜我更喜欢换行", "你说得对，但是《lrcparser》是由……"],
            )
        ]


with open("example_spec.lrc", "r", encoding="utf-8") as lrc_file:
    example_spec = lrc_file.read()


class Test_LrcParser_Special:
    result = LrcParser.parse(example_spec)
    result_translations = LrcParser.parse(example_spec, parse_translations=True)

    timestamps = [
        LrcTime(1, 23, 456),
        LrcTime(1, 23, 456),
        LrcTime(2, 34, 560),
        LrcTime(2, 34, 560),
        LrcTime(2, 37, 500),
        LrcTime(2, 37, 500),
        LrcTime(3, 23, 370),
        LrcTime(3, 23, 375),
        LrcTime(3, 23, 375),
        LrcTime(3, 45, 678),
        LrcTime(3, 45, 678),
        LrcTime(8, 33, 750),
    ]

    def test_parse_attributes(self):
        assert self.result["offset"] == 75
        assert self.result["attributes"] == {
            "ti": "Special LRC File Test",
            "al": "TEST",
            "by": "283375",
            "offset": "75",
        }

    def test_parse_lrc_lines(self):
        lrc_lines = self.result["lrc_lines"]

        assert len(lrc_lines) == 12

        for i, line in enumerate(lrc_lines):
            assert line.start_time == self.timestamps[i]

        assert (
            lrc_lines[0].text.to_str()[-5:]
            == lrc_lines[2].text.to_str()[-5:]
            == lrc_lines[9].text.to_str()[-5:]
            == "yrics"
        )
        assert (
            len(lrc_lines[4].text) < len(lrc_lines[6].text) == len(lrc_lines[11].text)
        )

        _4_word_timestamps = [
            LrcTime(2, 37, 500),
            LrcTime(2, 37, 520),
            LrcTime(2, 37, 550),
        ]

        for i, segment in enumerate(lrc_lines[4].text):
            assert isinstance(segment, LrcTextSegment)
            assert segment.time == _4_word_timestamps[i]

    def test_parse_lrc_lines_translations(self):
        lrc_lines = self.result_translations["lrc_lines"]

        assert (
            lrc_lines[3].text.to_str(force_word_timestamp=False)
            == "Totally outrageous line"
        )
        assert lrc_lines[3].translations is not None
        assert lrc_lines[3].translations == [
            LrcText(
                LrcTextSegment(LrcTime(3, 23, 375), "？"),
                LrcTextSegment(LrcTime(3, 24, 475), "？"),
                LrcTextSegment(LrcTime(3, 25, 575), "？"),
            ),
        ]
