from lrcparser import LrcLine, TRANSLATION_DIVIDER
from datetime import timedelta


class Test_LrcLine:
    test_LrcLine = LrcLine(
        start_timedelta=timedelta(seconds=5, milliseconds=593),
        text="This is a test line.",
        translations=["这是测试。"],
    )

    def test_get_time(self):
        assert self.test_LrcLine.get_time() == {
            "minutes": 0,
            "seconds": 5,
            "microseconds": 593000,
        }

    def test_to_str(self):
        assert self.test_LrcLine.to_str() == "[00:05.59]This is a test line."
        assert (
            self.test_LrcLine.to_str(ms_digits=3, translations=True)
            == f"[00:05.593]This is a test line.{TRANSLATION_DIVIDER}这是测试。"
        )

        assert (
            self.test_LrcLine.to_str(translations=True, translation_divider=" /|\\")
            == "[00:05.59]This is a test line. /|\\这是测试。"
        )

    def test_format_functions(self):
        assert str(self.test_LrcLine) == self.test_LrcLine.to_str()
        assert int(self.test_LrcLine) == 5593
        assert float(self.test_LrcLine) == 5593.000
