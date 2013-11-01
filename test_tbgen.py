from tbgen import (Parser, RawRule)
from interval import Interval

import pytest
skip = pytest.mark.skipif


class TestParser():

    p = Parser('test_rules.txt')

    def test_parse(self):

        r1 = RawRule(['!192.151.11.17', '32'], ['15.0.120.4', '32'],\
                     ['!10', '655'], ['1221', '1221'], ['0x06', '0xff'],\
                      'DROP', 1, 0, 1, 0, 0, '0')
        r2 = RawRule(['192.151.11.17', '0'], ['15.0.120.4', '24'],\
                     ['1', '100'], ['1221', '1221'], ['0x06', '0xff'],\
                      'PASS', 0, 0, 0, 0, 0, '1')

        assert self.p.parse() == [r1, r2]


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

    def test_get_fields(self):
        rule = '!192.151.11.17/32 15.0.120.4/32 !10 : 655 1221 : 1221 0x06/0xff DROP'
        assert self.p.get_fields(rule) == [ ['!192.151.11.17', '32'], \
                                            ['15.0.120.4', '32'],\
                                            ['!10', '655'],\
                                            ['1221', '1221'],\
                                            ['0x06', '0xff'],\
                                             'DROP' ]

    def test_read_file(self):
        fname = 'test_rules.txt'
        s1 = '!192.151.11.17/32 15.0.120.4/32 !10 : 655 1221 : 1221 0x06/0xff DROP\n'
        s2 = '192.151.11.17/0 15.0.120.4/24 1 : 100 1221 : 1221 0x06/0xff PASS\n'

        assert self.p.read_file() == [s1, s2]
        
class TestRawRule(object):

#     r = RawRule('', '', '', '', '', '', '', '', '', '', '', '')
    r = RawRule(['!192.151.11.17', '32'], ['15.0.120.4', '32'],\
                     ['!10', '655'], ['1221', '1221'], ['0x06', '0xff'],\
                      'DROP', 1, 0, 1, 0, 0, '0')

    def test_protocol_to_interval(self):
        assert self.r.protocol_to_interval() == Interval(6, 6)

    @skip
    def test_port_to_interval(self):
        assert self.r.port_to_interval(self.r.dst_port) == Interval(1221, 1221)

    def test_subnet_to_interval(self):
        # check subnet '1.2.3.4/5'
        f1 = ['1.2.3.4', '5']
        assert self.r.subnet_to_interval(f1) == Interval(0, 134217727)
        # check subnet '5.6.7.8/0'

        f2 = ['5.6.7.8', '0']
        assert self.r.subnet_to_interval(f2) == Interval(0, 2 ** 32 - 1)
        
        f3 = ['24.102.18.97', '17']
        assert self.r.subnet_to_interval(f3) == Interval(409337856, 409370623)

    @skip
    def test_normalize(self):
        action = 'PASS'
        r_id = 13
        m = 2 ** 32 - 1
        i1 = Interval(1, 2)
        i3 = Interval(5, 6)
        i5 = Interval(9, 9)
        r1 = RawRule(i1, Interval(3, 4),\
                     i3, Interval(7, 8),
                     i5, action,\
                     False, True, False, True, False, r_id)
        rules = r1.normalize()
        assert len(rules) == 4

        assert rules[0] == Rule(i1, Interval(0, 2), i3, Interval(0, 6), i5, action, r_id)
        assert rules[1] == Rule(i1, Interval(0, 2), i3, Interval(9, m), i5, action, r_id)
        assert rules[2] == Rule(i1, Interval(5, m), i3, Interval(0, 6), i5, action, r_id)
        assert rules[3] == Rule(i1, Interval(5, m), i3, Interval(9, m), i5, action, r_id)

        
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
