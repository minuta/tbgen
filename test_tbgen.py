from tbgen import (Parser)

import pytest
skip = pytest.mark.skipif

class TestParser():


    p = Parser('test_rules.txt')
    def test_check_negs(self):

        assert self.p.check_negs(['!192.151.11.17/32', '15.0.120.4/32',\
                           '!10', ':', '655', '1221', ':', '1221',\
                           '0x06/0xff']) == [True, False, True, False, False]
        assert self.p.check_negs(['192.151.11.17/32', '15.0.120.4/32',\
                           '10', ':', '655', '1221', ':', '1221',\
                           '0x06/0xff']) == [False, False, False, False, False]
        assert self.p.check_negs(['!192.151.11.17/32', '!15.0.120.4/32',\
                           '!10', ':', '655', '!1221', ':', '1221',\
                           '!0x06/0xff']) == [True, True, True, True, True]

    def parse(self):
        assert self.p.parse() 


@skip
def test_subnet_to_interval():
    # check subnet '1.2.3.4/5'
    assert subnet_to_interval(1, 2, 3, 4, 5) == Interval(0, 134217727)
    # check subnet '5.6.7.8/0'
    assert subnet_to_interval(5, 6, 7, 8, 0) == Interval(0, 2 ** 32 - 1)
    assert subnet_to_interval(24, 102, 18, 97, 17) == Interval(409337856,
            409370623)

@skip
class TestRawRule(object):

    def test_normalize(self):
        r1 = RawRule(Interval(1, 2), Interval(3, 4),
                          Interval(5, 6), Interval(7, 8),
                          Interval(9, 9), False, True, False,
                          True, False, 1000)
        rules = r1.normalize()
        assert len(rules) == 4
#         assert rules[0] == ...
#         assert rules[1] == ...
#         ...
@skip        
class TestRule(object):

    def test_eq(self):
        i1 = Interval(1, 2)
        i2 = Interval(3, 4)
        i3 = Interval(5, 6)
        i4 = Interval(7, 8)
        i5 = Interval(9, 10)
        r1 = Rule(i1, i2, i3, i4, i5, 1000, PASS)
        assert Rule(i1, i2, i3, i4, i5, 1000, PASS) == r1
        assert r1 != Rule(i1, i1, i1, i1, i1, 1000, DROP)
