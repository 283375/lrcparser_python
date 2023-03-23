from datetime import timedelta

from lrcparser import TRANSLATION_DIVIDER, LrcLine, LrcText, LrcTextSegment, LrcTime


class Test_LrcLine_General:
    line = LrcLine(
        start_time=LrcTime(0, 5, 593),
        text=LrcText(LrcTextSegment(LrcTime(0, 5, 593), "This is a test line.")),
        translations=[LrcText(LrcTextSegment(LrcTime(0, 5, 593), "这是测试"))],
    )

    def test_to_str(self):
        assert self.line.to_str() == "[00:05.59]This is a test line."
        assert (
            self.line.to_str(ms_digits=3, translations=True)
            == f"[00:05.593]This is a test line.{TRANSLATION_DIVIDER}这是测试"
        )

        assert (
            self.line.to_str(translations=True, translation_divider=" /|\\")
            == "[00:05.59]This is a test line. /|\\这是测试"
        )

        assert (
            self.line.to_str(translations=True, translation_divider="\n")
            == "[00:05.59]This is a test line.\n[00:05.59]这是测试"
        )

    def test_format_functions(self):
        assert str(self.line) == self.line.to_str()
        assert int(self.line) == 5
        assert float(self.line) == 5.593


class Test_LrcLine_Word:
    line = LrcLine(
        start_time=LrcTime(0, 5, 593),
        text=LrcText(
            LrcTextSegment(LrcTime(0, 5, 593), "This "),
            LrcTextSegment(LrcTime(0, 5, 693), "is "),
            LrcTextSegment(LrcTime(0, 5, 793), "a "),
            LrcTextSegment(LrcTime(0, 5, 893), "test "),
            LrcTextSegment(LrcTime(0, 6, 690), "line."),
        ),
        translations=[
            LrcText(
                LrcTextSegment(LrcTime(0, 5, 593), "这"),
                LrcTextSegment(LrcTime(0, 5, 693), "是"),
                LrcTextSegment(LrcTime(0, 5, 793), "个"),
                LrcTextSegment(LrcTime(0, 5, 893), "测"),
                LrcTextSegment(LrcTime(0, 6, 690), "试"),
            ),
            LrcText(LrcTextSegment(LrcTime(0, 5, 793), "これテストです")),
        ],
    )

    def test_to_str(self):
        assert (
            self.line.to_str()
            == "[00:05.59]<00:05.59>This <00:05.69>is <00:05.79>a <00:05.89>test <00:06.69>line."
        )
        assert self.line.to_str(translations=True) == (
            "[00:05.59]<00:05.59>This <00:05.69>is <00:05.79>a <00:05.89>test <00:06.69>line."
            + TRANSLATION_DIVIDER
            + "<00:05.59>这<00:05.69>是<00:05.79>个<00:05.89>测<00:06.69>试"
            + TRANSLATION_DIVIDER
            + "<00:05.79>これテストです"
        )
        assert self.line.to_str(translations=True, translation_divider="\n") == (
            "[00:05.59]<00:05.59>This <00:05.69>is <00:05.79>a <00:05.89>test <00:06.69>line.\n"
            "[00:05.59]<00:05.59>这<00:05.69>是<00:05.79>个<00:05.89>测<00:06.69>试\n"
            "[00:05.59]<00:05.79>これテストです"
        )


# class Test_LrcLine_Shorthand:
#     line = LrcLine(
#         start_timedelta=timedelta(seconds=5, milliseconds=593),
#         text=[(timedelta(seconds=5, milliseconds=593), "This is a test line.")],
#         translations=[[(timedelta(seconds=5, milliseconds=593), "这是测试。")]],
#     )
#     line_short = LrcLine(
#         start_timedelta=timedelta(seconds=5, milliseconds=593),
#         text="This is a test line.",
#         translations=["这是测试。"],
#     )

#     def test_shorthand(self):
#         assert self.line == self.line_short
