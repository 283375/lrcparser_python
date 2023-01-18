import lrcparser

import doctest

class Test_Docstring():
    def test_docstring(self):
        fail, total = doctest.testmod(lrcparser)
        assert fail == 0
