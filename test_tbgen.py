
import pytest
from tbgen import (Parser)

skip = pytest.mark.skipif


class Test_Parser(object):

    o = Parser('test_rules')

    def test_neg_state(self):
        rf1 = ('!192.151.11.17/32', '15.0.120.4/32', \
                       '!0:65535', '1221:1221', '0x06/0xff')
        rf2 = ('192.151.11.17/32', '15.0.120.4/32', \
                       '0:65535', '1221:1221', '0x06/0xff')
        rf3 = ('!192.151.11.17/32', '!15.0.120.4/32', \
                       '!0:65535', '!1221:1221', '!0x06/0xff')

        assert self.o.neg_state(rf1) == [1, 0, 1, 0, 0]
        assert self.o.neg_state(rf2) == [0, 0, 0, 0, 0]
        assert self.o.neg_state(rf3) == [1, 1, 1, 1, 1]
