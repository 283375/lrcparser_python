from lrcparser import LrcTime
from datetime import timedelta


class Test_LrcTime:
    time_tuple = LrcTime((0, 3, 750))
    time_int = LrcTime(0, 3, 750)
    time_int_microsecond = LrcTime(0, 3, 750000, microsecond=True)
    time_timedelta = LrcTime(timedelta(seconds=3, milliseconds=750))
    time_str = LrcTime("00:03.75")
    time_str_alt = LrcTime("00:03.750")
    time_str_tag = LrcTime("[00:03.750]")

    time_repr = LrcTime(0, 3, 750)
    time_repr_microsecond = LrcTime(0, 3, 750, microsecond=True)

    def test_init(self):
        assert (
            self.time_tuple
            == self.time_int
            == self.time_int_microsecond
            == self.time_timedelta
            == self.time_str
            == self.time_str_alt
            == self.time_str_tag
        )

    def test_repr(self):
        assert repr(self.time_repr) == "LrcTime(0, 3, 750)"
        assert (
            repr(self.time_repr_microsecond) == "LrcTime(0, 3, 750, microsecond=True)"
        )
