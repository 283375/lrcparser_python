import re
from pathlib import Path

from lrcparser.scanner import (
    find_timestamp,
    parse_timestamp,
    scan_line,
    scan_word_segments,
)

FILES_DIR = Path(__file__).parent / "files"


class TestParseTimestamp:
    def test_standard(self):
        assert parse_timestamp("00:12.345") == (0, 12, 345000)
        assert parse_timestamp("01:02.03") == (1, 2, 30000)

    def test_loose(self):
        assert parse_timestamp("00:12") == (0, 12, 0)
        assert parse_timestamp("1:02") == (1, 2, 0)
        assert parse_timestamp("1:2.5") == (1, 2, 500000)
        assert parse_timestamp("0:0.1") == (0, 0, 100000)
        assert parse_timestamp("75:33.75") == (75, 33, 750000)

    def test_whitespace(self):
        assert parse_timestamp(" 00:12.34 ") == (0, 12, 340000)

    def test_invalid(self):
        assert parse_timestamp("ti: test") is None
        assert parse_timestamp("") is None
        assert parse_timestamp("00") is None
        assert parse_timestamp("00:") is None
        assert parse_timestamp(":12") is None
        assert parse_timestamp("00:12.") is None
        assert parse_timestamp("00:12.1234567") is None
        assert parse_timestamp("aa:bb.cc") is None


class TestFindTimestamp:
    def test_search_semantics(self):
        assert find_timestamp("[00:03.750]") == (0, 3, 750000)
        assert find_timestamp("junk 1:02.5 junk") == (1, 2, 500000)

    def test_not_found(self):
        assert find_timestamp("no timestamp here") is None
        assert find_timestamp("") is None


class TestScanLine:
    def test_plain_line(self):
        scanned = scan_line("just text")
        assert scanned.timestamps == ()
        assert scanned.attributes == ()
        assert scanned.content == "just text"

    def test_timestamp_and_content(self):
        scanned = scan_line("[00:01.23]hello")
        assert scanned.timestamps == ((0, 1, 230000),)
        assert scanned.content == "hello"

    def test_stacked_timestamps(self):
        scanned = scan_line("[01:02.03][02:03.04][03:07.75]Same lyrics")
        assert scanned.timestamps == (
            (1, 2, 30000),
            (2, 3, 40000),
            (3, 7, 750000),
        )
        assert scanned.content == "Same lyrics"

    def test_attribute(self):
        scanned = scan_line("[ti: test]")
        assert scanned.attributes == (("ti", "test"),)

    def test_attribute_and_timestamp_on_one_line(self):
        scanned = scan_line("[ti:x][00:01.00]foo")
        assert scanned.attributes == (("ti", "x"),)
        assert scanned.timestamps == ((0, 1, 0),)
        assert scanned.content == "foo"

    def test_unterminated_bracket(self):
        scanned = scan_line("[00:01.00]text [unclosed")
        assert scanned.timestamps == ((0, 1, 0),)
        assert scanned.content == "text [unclosed"

        scanned = scan_line("[unclosed only")
        assert scanned.timestamps == ()
        assert scanned.attributes == ()
        assert scanned.content == "[unclosed only"

    def test_brackets_in_content(self):
        scanned = scan_line("[00:01.00]Hello [World] (ok)")
        assert scanned.timestamps == ((0, 1, 0),)
        assert scanned.content == "Hello [World] (ok)"

    def test_empty_content(self):
        scanned = scan_line("[00:03.24]")
        assert scanned.timestamps == ((0, 3, 240000),)
        assert scanned.content == ""

    def test_bom_stripped(self):
        scanned = scan_line("\ufeff[by:kuoie]")
        assert scanned.attributes == (("by", "kuoie"),)

    def test_empty_attribute_value_ignored(self):
        scanned = scan_line("[ti:]")
        assert scanned.attributes == ()


class TestScanWordSegments:
    def test_word_timestamps(self):
        segments = scan_word_segments("<00:01.00>a <00:02.00>b")
        assert segments == [((0, 1, 0), "a "), ((0, 2, 0), "b")]

    def test_plain_content(self):
        assert scan_word_segments("plain text") == [(None, "plain text")]

    def test_leading_text_kept_with_line_time(self):
        segments = scan_word_segments("Intro <00:01.00>word")
        assert segments == [(None, "Intro "), ((0, 1, 0), "word")]

    def test_unterminated_angle_is_literal(self):
        segments = scan_word_segments("<00:01.00>a <tail")
        assert segments == [((0, 1, 0), "a "), (None, "<tail")]

    def test_non_timestamp_angle_is_literal(self):
        segments = scan_word_segments("<not-a-time>text")
        assert segments == [(None, "<not-a-time>text")]


class OldRegexBaseline:
    """旧正则扫描的参考实现，作为差分安全网；确认稳定后可删。"""

    LRC_LINE = re.compile(r"(?P<time>\[\d{2}:\d{2}\.\d{2,6}\])(?P<content>.*)")
    LRC_WORD = re.compile(
        r"(?P<time><\d{2}:\d{2}\.\d{2,6}>)(?P<content>.*?)(?=<|\n|$){1}"
    )

    @staticmethod
    def old_timestamps_and_content(line):
        match = OldRegexBaseline.LRC_LINE.match(line)
        if not match:
            return None
        timestamps = [parse_timestamp(match["time"][1:-1])]
        content = match["content"]
        while extra := OldRegexBaseline.LRC_LINE.match(content):
            timestamps.append(parse_timestamp(extra["time"][1:-1]))
            content = extra["content"]
        return timestamps, content

    @staticmethod
    def old_word_segments(content):
        return [
            (parse_timestamp(time[1:-1]), text)
            for time, text in OldRegexBaseline.LRC_WORD.findall(content)
        ]


def test_differential_against_old_regexes():
    for fixture in sorted(FILES_DIR.glob("*.lrc")):
        for line in fixture.read_text(encoding="utf-8").splitlines():
            scanned = scan_line(line)
            old = OldRegexBaseline.old_timestamps_and_content(line)
            if old is None:
                continue
            old_timestamps, old_content = old
            assert list(scanned.timestamps) == old_timestamps, (
                fixture.name + ": " + line
            )
            assert scanned.content == old_content, fixture.name + ": " + line
            old_words = OldRegexBaseline.old_word_segments(old_content)
            new_words = [
                (ts, text)
                for ts, text in scan_word_segments(old_content)
                if ts is not None
            ]
            assert new_words == old_words, fixture.name + ": " + line
