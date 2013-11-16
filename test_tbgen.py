from tbgen import Interval, IntervalList, Parser, RawRule, Rule, PASS, DROP
# from interval import Interval, IntervalList
import os
import pytest

skip = pytest.mark.skipif


class TestInterval(object):

    def test_has_intersection(self):
        x = Interval(3, 10)
        y = Interval(5, 12)
        z = Interval(3, 5)
        w = Interval(12, 30)
        v = Interval(10, 14)

        assert x.has_intersection(y) and y.has_intersection(x)

        assert x.has_intersection(x)

        assert x.has_intersection(z) and z.has_intersection(x)

        assert not (x.has_intersection(w) and w.has_intersection(x))

        assert x.has_intersection(v) and  v.has_intersection(x)

        assert y.has_intersection(w) and w.has_intersection(y)

    def test_has_identical_borders(self):
        x = Interval(5, 10)
        y = Interval(5, 8)
        z = Interval(6, 10)
        assert x.has_identical_borders(y)
        assert x.has_identical_borders(z)
        assert x.has_identical_borders(x)

    def test_dif(self):
        x = Interval(5, 10)
        # Identival Intervals
        assert x - x == []

        # x is Subinterval of y with no identical Borders
        y = Interval(3, 12)
        assert x - y == []

        # x is Subinterval of y and left borders are identical
        y = Interval(5, 12)
        assert x - y == []

        # x is Subinterval of y and right boreders are identical
        y = Interval(3, 10)
        assert x - y == []

        # y is Subinterval of x with no identical borders
        y = Interval(6, 9)
        assert x - y == [Interval(5, 5), Interval(10, 10)]

        # y is Subinterval of x and left borders are identical
        y = Interval(5, 8)
        assert x - y == [Interval(9, 10)]

        # y is Subinterval of x and right borders are identical
        y = Interval(8, 10)
        assert x - y == [Interval(5, 7)]

        # no intersection
        y = Interval(12, 15)
        assert x - y == [x]

        # Intersection with only one element at the right border
        y = Interval(10, 12)
        assert x - y == [Interval(5, 9)]

        # Intersection with only one element at the left border
        y = Interval(1, 5)
        assert x - y == [Interval(6, 10)]

        # Intersection with only one element in the middle
        y = Interval(6, 6)
        assert x - y == [Interval(5, 5), Interval(7, 10)]

        # One Element Intervals and Intersection
        x = Interval(5, 5)
        assert x - x == []
        # One Element intervals and no Intersection
        y = Interval(3, 3)
        assert x - y == [x]

        # subtract two identical interval
        i1 = Interval(1, 2)
        assert i1 - i1 == []

        i2 = Interval(1, 3)
        assert i2 - i1 == [Interval(3, 3)]

        i3 = Interval(0, 5)
        assert i3 - i1 == [Interval(0, 0), Interval(3, 5)]
        assert i1 - i3 == []

    def test_is_subinterval(self):
        i = Interval(3, 7)
        q = Interval(1, 10)
        j = Interval(9, 12)
        k = Interval(3, 5)
        p = Interval(4, 10)
        r = Interval(4, 4)

        assert i.is_subinterval(q)     # is subset
        assert not q.is_subinterval(i)
        assert not j.is_subinterval(q)   # intersection
        assert not i.is_subinterval(j)   # no intersection
        assert k.is_subinterval(i)    # k.a = i.a
        assert not i.is_subinterval(k)
        assert p.is_subinterval(q)    # p.b = q.b
        assert not q.is_subinterval(p)
        assert i.is_subinterval(i)

        # Interval contains only one element
        assert r.is_subinterval(r)
        assert r.is_subinterval(p)
        assert not r.is_subinterval(j)

    def test__un(self):
        x = Interval(5, 10)
        y = Interval(7, 12)
        # with intersection
        assert x._un(y) == [Interval(5, 12)]

        y = Interval(11, 14)
        # no intersection
        assert x._un(y) == [Interval(5, 10), Interval(11, 14)]

        y = Interval(6, 9)
        # one Interval is a subset
        assert x._un(y) == [Interval(5, 10)]

        # some Limits of Intervals are same
        y = Interval(5, 8)
        # check : x.a = y.a
        assert x._un(y) == [Interval(5, 10)]

        y = Interval(7, 10)
        # check x.b = y.b
        assert x._un(y) == [Interval(5, 10)]

        # Interval contains only one element
        # subset/intersection
        y = Interval(5, 5)
        y._un(x) == [Interval(5, 10)]

        # no intersection
        y = Interval(3, 3)
        y._un(x) == [Interval(3, 3), Interval(5, 10)]

    def test_union(self):
        x = Interval(5, 10)
        y = Interval(7, 12)

        #  Intervals are identical
        assert x + x == [x]

        # with intersection
        assert x + y == y + x == [Interval(5, 12)]

        y = Interval(11, 14)    # no intersection
        assert x + y == y + x == [Interval(5, 10), Interval(11, 14)]

        y = Interval(6, 9)    # one Interval is a subset
        assert x + y == y + x == [Interval(5, 10)]

        # some Limits of Intervals are same
        y = Interval(5, 8)
        assert x + y == y + x == [Interval(5, 10)]  # check : x.a = y.a

        y = Interval(7, 10)
        assert x + y == y + x == [Interval(5, 10)]  # check x.b = y.b

        # Interval contains only one element & Intersection
        r = Interval(5, 5)
        assert x + r == r + x == [Interval(5, 10)]

        assert x + r == r + x == [Interval(5, 10)] # intersect

        # Interval contains one element and & NO intersection
        assert r + y == y + r == [Interval(5, 5), Interval(7, 10)]

    def test_intersect(self):
        x = Interval(5, 10)

        # Identical Intervals
        assert x.intersect(x) == [x]

        # No Intersection
        y = Interval(1, 3)
        assert x.intersect(y) == y.intersect(x) == []

        # y is a Subinterval of x
        y = Interval(6, 8)
        assert x.intersect(y) == y.intersect(x) == [Interval(6, 8)]

        # Intersection and Left Borders are identical
        y = Interval(5, 7)
        assert x.intersect(y) == y.intersect(x) == [Interval(5, 7)]

        # Intersection and right Borders are identical
        y = Interval(7, 10)
        assert x.intersect(y) == y.intersect(x) == [Interval(7, 10)]

        # Intersection and self is to the left
        y = Interval(7, 12)
        assert x.intersect(y) == [Interval(7, 10)]

        # Intersection and self is to the right
        y = Interval(3, 7)
        assert x.intersect(y) == [Interval(5, 7)]

        # Intersection of 1-element-Intervals
        y = Interval(3,3)
        assert y.intersect(y) == [y]

    def test_negate(self):
        x  = Interval(10, 15)
        assert x.negate(0, 20) == [Interval(0, 9), Interval(16, 20)]

        x = Interval(10, 10)
        assert x.negate(0, 20) == [Interval(0, 9), Interval(11, 20)]
        
        assert x.negate(10, 30) == [Interval(11, 30)]

    def test_sub(self):         # see test_dif() for more
        x = Interval(1, 10)
        y = Interval(5, 10)
        z = Interval(8, 10)
        w = Interval(6, 8)
        assert (x - y) == [Interval(1, 4)]
        assert (x - w) == [Interval(1, 5), Interval(9, 10)]

    def test_add(self):         # see test_union() for more
        x = Interval(1, 5)
        y = Interval(3, 9)
        z = Interval(10, 15)
        assert x + y ==  y + x  == [Interval(1, 9)]
        assert x + z == [x, z]


class TestIntervalList(object):

    def test_simple(self):
        il = IntervalList([Interval(1, 5), Interval(7, 10)])
        result = il - IntervalList([Interval(2, 8)])
        assert isinstance(result, IntervalList)
        assert result == IntervalList([Interval(1, 1), Interval(9, 10)])
        assert result == IntervalList([Interval(9, 10), Interval(1, 1)])

    def test_eq(self):
        assert IntervalList([]) == IntervalList([])
        assert IntervalList([Interval(1, 2)]) == IntervalList([Interval(1, 2)])
        assert IntervalList([Interval(1, 2)]) != IntervalList([])
        #
        assert IntervalList([Interval(1, 2), Interval(5, 8)]) == \
                IntervalList([Interval(1, 2), Interval(5, 8)])

    def test_interval_len(self):
        a = Interval(4, 10)
        assert a.interval_len() == 7

    def test_remove_duplicates(self):
        a = IntervalList([Interval(1, 5), Interval(8, 13), Interval(1, 5), \
                Interval(8, 13), Interval(1, 5)])
        assert a.remove_duplicates() == [Interval(1, 5), Interval(8, 13)]

    def test_add(self):
        q = IntervalList([Interval(5, 10)])
        r = IntervalList([Interval(8, 15)])
        k = IntervalList([Interval(7, 10)])

        assert q + r == IntervalList([Interval(5, 15)])
        assert q + k == q

        a = IntervalList([Interval(1, 10), Interval(8, 12)])
        b = IntervalList([Interval(14, 16), Interval(20, 30)])
        c = IntervalList([Interval(1, 10)])

        assert a + q == IntervalList([Interval(1, 10), Interval(5, 12)])
        assert a + c == IntervalList([Interval(1, 10), Interval(1, 12)])
#     assert a + b == IntervalList([Interval(1, 10), Interval(8, 12),\
#             Interval(14, 16), Interval(20, 30)])
#     assert a + b == IntervalList([Interval()])

    def test_check_eq(self):
        # check Equality of IntervalList with permutated contetnt
        a = IntervalList([Interval(1, 10), Interval(8, 12)])
        b = IntervalList([Interval(8, 12), Interval(1, 10)])
        c = IntervalList([Interval(1, 10)])
        assert a == a
        assert a == b
        assert not a != b
        assert a != c
        assert not a == c 

    def test_sub(self):
        x = Interval(1, 10)
        y = Interval(5, 10)
        z = Interval(8, 10)
        w = Interval(6, 8)

        a = IntervalList([x, y])
        b = IntervalList([w])
        assert a - b == IntervalList([Interval(1, 5), Interval(9, 10),\
                Interval(5, 5), Interval(9, 10)])

        c = IntervalList([z, w])
        assert a - c == IntervalList([Interval(1, 7), Interval(1, 5),\
                Interval(9, 10), Interval(5, 7),\
                Interval(5, 5), Interval(9, 10)])


@skip
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

    @skip
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


@skip
def test_check_args():
    assert check_args(0, 0) == (False, ERROR_STR2)
    assert check_args(1, -1) == (False, ERROR_STR1)
    assert check_args(50000, 10) == (False, ERROR_STR1)
    assert check_args(10, 10) == (True, OK_STR)
    assert check_args(0, 5) == (True, OK_STR)



class TestRule(object):

    # Other contains Self : no identical borders
    def test_other_contains_self_1(self):
        I = Interval
        r1 = Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(3, 5), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == []

    # Other contains Self : some identical borders
    def test_other_contains_self_2(self):
        I = Interval
        r1 = Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(3, 5), DROP, 1)
        r2 = Rule(I(3, 9), I(3, 9), I(1, 9), I(1, 5), I(1, 5), DROP, 1)
        assert r1 - r2 == []

    # Self has no intersection with Other
    def test_no_intersection_3(self):
        I = Interval
        r1 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r2 = Rule(I(7, 9), I(7, 9), I(7, 9), I(7, 9), I(7, 9), DROP, 1)
        assert r1 - r2 == [r1]


    # Tests, where Self contains Other : 

    # self, other differ in only 1 Dimension  (5 test-functions)
    def test_self_contains_other_4(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(3, 5), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 2), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(6, 9), I(1, 9), I(1, 9),I(1, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == [r3, r4]

    def test_self_contains_other_5(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(3, 5), I(1, 9), I(1, 9), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == [r3, r4]

    def test_self_contains_other_6(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(3, 5), I(1, 9), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 9), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(1, 9), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == [r3, r4]
 
    def test_self_contains_other_7(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(1, 9), I(3, 5), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 2), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(1, 9), I(1, 9), I(6, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == [r3, r4]
 
    def test_self_contains_other_8(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(3, 5), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 2), DROP, 1)
        r4 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(6, 9), DROP, 1)
        assert r1 - r2 == [r3, r4]


    # self, other differ in 2 Dimensions (4 Tests)
    def test_self_contains_other_9(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(3, 5), I(3, 5), I(1, 9), I(1, 9), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 2), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(6, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(3, 5), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(3, 5), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6]

    def test_self_contains_other_10(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(3, 5), I(3, 5), I(1, 9), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(1, 9), I(3, 5), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(1, 9), I(3, 5), I(6, 9), I(1, 9), I(1, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6]

    def test_self_contains_other_11(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(3, 5), I(3, 5), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 9), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(1, 9), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(1, 9), I(1, 9), I(3, 5), I(1, 2), I(1, 9), DROP, 1)
        r6 = Rule(I(1, 9), I(1, 9), I(3, 5), I(6, 9), I(1, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6]

    def test_self_contains_other_12(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(1, 9), I(3, 5), I(3, 5), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 2), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(1, 9), I(1, 9), I(6, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(1, 9), I(1, 9), I(1, 9), I(3, 5), I(1, 2), DROP, 1)
        r6 = Rule(I(1, 9), I(1, 9), I(1, 9), I(3, 5), I(6, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6]

    # self, other differ in 3 Dimensions (3 Tests)
    def test_self_contains_other_13(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(3, 5), I(3, 5), I(3, 5), I(1, 9), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 2), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(6, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(3, 5), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(3, 5), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r7 = Rule(I(3, 5), I(3, 5), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r8 = Rule(I(3, 5), I(3, 5), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == [r3, r4, r5, r6, r7, r8]

    def test_self_contains_other_11(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(3, 5), I(3, 5), I(3, 5), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(1, 9), I(3, 5), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(1, 9), I(3, 5), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        r7 = Rule(I(1, 9), I(3, 5), I(3, 5), I(1, 2), I(1, 9), DROP, 1)
        r8 = Rule(I(1, 9), I(3, 5), I(3, 5), I(6, 9), I(1, 9), DROP, 1)
        assert r1 - r2 == [r3, r4, r5, r6, r7, r8]

    def test_self_contains_other_12(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(1, 9), I(3, 5), I(3, 5), I(3, 5), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 9), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(1, 9), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(1, 9), I(1, 9), I(3, 5), I(1, 2), I(1, 9), DROP, 1)
        r6 = Rule(I(1, 9), I(1, 9), I(3, 5), I(6, 9), I(1, 9), DROP, 1)
        r7 = Rule(I(1, 9), I(1, 9), I(3, 5), I(3, 5), I(1, 2), DROP, 1)
        r8 = Rule(I(1, 9), I(1, 9), I(3, 5), I(3, 5), I(6, 9), DROP, 1)
        assert r1 - r2 == [r3, r4, r5, r6, r7, r8]

    # self, other differ in 4 Dimensions (2 Tests)
    def test_self_contains_other_13(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(1, 9), DROP, 1)

        r3 = Rule(I(1, 2), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(6, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(3, 5), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(3, 5), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r7 = Rule(I(3, 5), I(3, 5), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r8 = Rule(I(3, 5), I(3, 5), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        r9 = Rule(I(3, 5), I(3, 5), I(3, 5), I(1, 2), I(1, 9), DROP, 1)
        r10= Rule(I(3, 5), I(3, 5), I(3, 5), I(6, 9), I(1, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6, r7, r8, r9, r10]

    def test_self_contains_other_14(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(1, 9), I(3, 5), I(3, 5), I(3, 5), I(3, 5), DROP, 1)

        r3 = Rule(I(1, 9), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(1, 9), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(1, 9), I(3, 5), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(1, 9), I(3, 5), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        r7 = Rule(I(1, 9), I(3, 5), I(3, 5), I(1, 2), I(1, 9), DROP, 1)
        r8 = Rule(I(1, 9), I(3, 5), I(3, 5), I(6, 9), I(1, 9), DROP, 1)
        r9 = Rule(I(1, 9), I(3, 5), I(3, 5), I(3, 5), I(1, 2), DROP, 1)
        r10= Rule(I(1, 9), I(3, 5), I(3, 5), I(3, 5), I(6, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6, r7, r8, r9, r10]


    # self, other differ in 5 Dimensions (1 Test)
    def test_self_contains_other_15(self):
        I = Interval
        r1 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r2 = Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(3, 5), DROP, 1)

        r3 = Rule(I(1, 2), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r4 = Rule(I(6, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r5 = Rule(I(3, 5), I(1, 2), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r6 = Rule(I(3, 5), I(6, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
        r7 = Rule(I(3, 5), I(3, 5), I(1, 2), I(1, 9), I(1, 9), DROP, 1)
        r8 = Rule(I(3, 5), I(3, 5), I(6, 9), I(1, 9), I(1, 9), DROP, 1)
        r9 = Rule(I(3, 5), I(3, 5), I(3, 5), I(1, 2), I(1, 9), DROP, 1)
        r10= Rule(I(3, 5), I(3, 5), I(3, 5), I(6, 9), I(1, 9), DROP, 1)
        r11= Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(1, 2), DROP, 1)
        r12= Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(6, 9), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6, r7, r8, r9, r10, r11, r12]


    # Tests, where Self and Other have an Intersection: 
    # in each case we get exactly 5 Rules
    def test_self_contains_other_16(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r2 = Rule(I(4, 9), I(4, 9), I(4, 9), I(4, 9), I(4, 9), DROP, 1)

        r3 = Rule(I(1, 3), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r4 = Rule(I(4, 6), I(1, 3), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r5 = Rule(I(4, 6), I(4, 6), I(1, 3), I(1, 6), I(1, 6), DROP, 1)
        r6 = Rule(I(4, 6), I(4, 6), I(4, 6), I(1, 3), I(1, 6), DROP, 1)
        r7 = Rule(I(4, 6), I(4, 6), I(4, 6), I(4, 6), I(1, 3), DROP, 1)

        assert r1 - r2 == [r3, r4, r5, r6, r7]

    # Intersection in not all 5 Dimensions => No Intersection at all (4 Tests)
    # Intersection in 1 Dimension
    def test_self_contains_other_17(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r2 = Rule(I(3, 9), I(7, 9), I(7, 9), I(7, 9), I(7, 9), DROP, 1)

        assert r1 - r2 == [r1]
    # Intersection in 2 Dimensions
    def test_self_contains_other_18(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r2 = Rule(I(3, 9), I(3, 9), I(7, 9), I(7, 9), I(7, 9), DROP, 1)

        assert r1 - r2 == [r1]

    # Intersection in 3 Dimensions
    def test_self_contains_other_19(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r2 = Rule(I(3, 9), I(3, 9), I(3, 9), I(7, 9), I(7, 9), DROP, 1)

        assert r1 - r2 == [r1]

    # Intersection in 4 Dimensions
    def test_self_contains_other_20(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        r2 = Rule(I(3, 9), I(3, 9), I(3, 9), I(3, 9), I(7, 9), DROP, 1)

        assert r1 - r2 == [r1]


    def test_num_rules_21(self):
        I = Interval
        r1 = Rule(I(1, 5), I(2, 5), I(3, 3), I(4, 4), I(5, 5), DROP, 1)
        r2 = Rule(I(2, 6), I(1, 3), I(3, 3), I(4, 4), I(5, 5), PASS, 2)

        r3 = Rule(I(1, 2), I(1, 5), I(3, 3), I(4, 4), I(5, 5), DROP, 1)

        diff = r2 - r1
        assert len(diff) == 2
        assert diff[0] == Rule(I(6, 6), I(1, 3), I(3, 3), I(4, 4), I(5, 5),
                PASS, 2)
        assert diff[1] == Rule(I(2, 5), I(1, 1), I(3, 3), I(4, 4), I(5, 5),
                PASS, 2)

    def test_eq_22(self):
        i1 = Interval(1, 2)
        i2 = Interval(3, 4)
        i3 = Interval(5, 6)
        i4 = Interval(7, 8)
        i5 = Interval(9, 10)
        r1 = Rule(i1, i2, i3, i4, i5, 1000, PASS)
        assert Rule(i1, i2, i3, i4, i5, 1000, PASS) == r1
        assert r1 != Rule(i1, i1, i1, i1, i1, 1000, DROP)


