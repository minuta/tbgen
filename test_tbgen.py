from tbgen import Parser, RawRule, Rule, PASS, DROP
from interval import Interval

import pytest
skip = pytest.mark.skipif


class TestParser():

    p = Parser('test_rules.txt')
    TESTFILE = "abc.txt"

    def teardown_method(self, method):
        try:
            os.unlink(self.TESTFILE)
        except OSError:
            pass

    def test_check_negs(self):
        new_line, negs = self.p.check_negs( ['!192.151.11.17/32', \
                '15.0.120.4/32', '!10', ':', '655',\
                '1221', ':', '1221', '0x06/0xff'] )
        assert new_line == ['192.151.11.17/32', '15.0.120.4/32',\
                           '10', ':', '655', '1221', ':', '1221',\
                           '0x06/0xff']
        assert negs == [True, False, True, False, False]

        new_line, negs = self.p.check_negs( ['192.151.11.17/32',\
                '15.0.120.4/32', '10', ':', '655',\
                '1221', ':', '1221', '0x06/0xff'] ) 
        assert new_line == ['192.151.11.17/32', '15.0.120.4/32',\
                           '10', ':', '655', '1221', ':', '1221',\
                           '0x06/0xff'] 
        assert negs == [False, False, False, False, False]

        new_line, negs = self.p.check_negs( ['!192.151.11.17/32',\
                '!15.0.120.4/32', '!10', ':', '655',\
                '!1221', ':', '1221', '!0x06/0xff'] ) 
        assert new_line == ['192.151.11.17/32', '15.0.120.4/32',\
                           '10', ':', '655', '1221', ':', '1221',\
                           '0x06/0xff']
        assert negs == [True, True, True, True, True]

    def test_fields_to_intervals(self):
        f = ['192.151.11.17/32', '15.0.120.4/32',\
                           '10', ':', '655', '1221', ':', '1221',\
                           '0x06/0xff', 'DROP'] 
        assert self.p.fields_to_intervals(f) ==\
                [ Interval(3231124241, 3231124241),\
                  Interval(251688964, 251688964), Interval(10, 655),\
                  Interval(1221, 1221), Interval(6, 6), DROP ]

    def test_get_fields(self):
        rule = """192.151.11.17/32 15.0.120.4/32 10 : 655 1221 : 1221\
                0x06/0xff DROP"""
        parts = rule.split()
        assert self.p.get_fields(parts) == [ [192, 151, 11, 17, 32],
                                            [15, 0, 120, 4, 32],
                                            [10, 655],
                                            [1221, 1221],
                                            [6, 255],
                                            DROP ]

    def test_read_file(self):
        fname = 'test_rules.txt'
        s1 = '!192.151.11.17/32 15.0.120.4/32 !10 : 655 1221 : 1221 0x06/0xff DROP\n'
        s2 = '192.151.11.17/0 15.0.120.4/24 1 : 100 1221 : 1221 0x06/0xff PASS\n'
        assert self.p.read_file() == [s1, s2]

    def test_parse(self):
        sh = Interval(3231124241, 3231124241)
        dh = Interval(251688964, 251688964)
        sp = Interval(10, 655) 
        dp = Interval(1221, 1221)
        prot = Interval(6, 6)
        r_id = '0'
        action = DROP
        neg = [1, 0, 1, 0, 0]

        r1 = RawRule(sh, dh, sp, dp, prot, action, neg[0], neg[1],\
                neg[2], neg[3], neg[4], r_id)

        assert self.p.parse()[0] == r1

    def test_protocol_to_interval(self):
        assert self.p.protocol_to_interval([6, 255]) == Interval(6, 6)

    def test_port_to_interval(self):
        assert self.p.port_to_interval([1221, 1221]) == Interval(1221, 1221)

    def test_subnet_to_interval(self):
        # check subnet '1.2.3.4/5'
        f1 = [1, 2, 3, 4, 5]
        assert self.p.subnet_to_interval(f1) == Interval(0, 134217727)
        # check subnet '5.6.7.8/0'

        f2 = [5, 6, 7, 8, 0]
        assert self.p.subnet_to_interval(f2) == Interval(0, 2 ** 32 - 1)
        
        f3 = [24, 102, 18, 97, 17]
        assert self.p.subnet_to_interval(f3) == Interval(409337856, 409370623)

    def test_broken_input_for_parser(self):
        src = "oawdasiduasiodaspodipoasd"
        with open(self.TESTFILE, "w") as f:
            f.write(src)
        p = Parser(self.TESTFILE)
        with py.test.raises(ParseError) as e:
            p.parse()

class TestRawRule(object):

    r = RawRule([192, 151, 11, 17, 32], [15, 0, 120, 4, 32],\
                     [10, 655], [1221, 1221], [6, 255],\
                      DROP, 1, 0, 1, 0, 0, 0)

    def test_eq(self):
        assert self.r == self.r    

    def test_negate(self):
        i = Interval(3, 5)
        assert self.r._negate(i, 0, 10, False) == [i]
        assert self.r._negate(i, 0, 10, True) ==\
                [Interval(0, 2), Interval(6, 10)]

    def test_normalize(self):
        action = PASS
        r_id = 13
        m = 2 ** 16 - 1
        M = 2 ** 32 - 1
        i1 = Interval(1, 2)
        i3 = Interval(5, 6)
        i5 = Interval(9, 9)

        r1 = RawRule(i1, Interval(3, 4),\
                     i3, Interval(7, 8),
                     i5, action,\
                     False, True, False, True, False, r_id)
        rules = r1.normalize()

        assert len(rules) == 4
        assert rules[0] == Rule(i1, Interval(0, 2), i3, Interval(0, 6),\
                i5, action, r_id)
        assert rules[1] == Rule(i1, Interval(0, 2), i3, Interval(9, m),\
                i5, action, r_id)
        assert rules[2] == Rule(i1, Interval(5, M), i3, Interval(0, 6),\
                i5, action, r_id)
        assert rules[3] == Rule(i1, Interval(5, M), i3, Interval(9, m),\
                i5, action, r_id)


    def test_normalize_worst_case_num_rules(self):
        raw_rule = RawRule(Interval(1, 2), Interval(3, 4), Interval(5, 6),
                Interval(7, 8), Interval(9, 10), DROP, True, True, True, True,
                True, 1)
        normalized_rules = raw_rule.normalize()
        assert len(normalized_rules) == 32

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


