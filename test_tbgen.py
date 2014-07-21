from tbgen import Tools, Interval, IntervalList, Parser, RawRule,\
        Rule, Packet, XML, TBGenError, PASS, DROP, ERROR_STR1, ERROR_STR2,ERROR_STR3,\
        ERROR_STR4, ERROR_STR5, ERROR_STR7, OK, NMIN, NMAX

from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring

import os, errno, pytest

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

        assert x.has_intersection(v) and v.has_intersection(x)

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

    def test_random_value1(self):
        I = Interval(1, 1)
        x = I.random_value()
        assert x == 1
  
    def test_random_value2(self):
        I = Interval(1, 3)
        x = I.random_value()
        assert x in [1, 2, 3]
    
    def test_random_neg_value1(self):
        I = Interval(2, 4)
        ok, x = I.random_neg_value(1, 6)
        assert ok == True and x in [1, 5, 6]

    def test_random_neg_value2(self):
        I = Interval(2, 4)
        ok, x = I.random_neg_value(2, 4)
        assert ok == False and x in [2, 3, 4]


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


class TestParser():

    p = Parser('in this case not important string')
    TESTFILE = "abc.txt"

    def teardown_method(self, method):
        try:
            os.unlink(self.TESTFILE)
        except OSError:
            pass

    def test_check_negs1(self):
        new_line, negs = self.p.check_negs( ['!192.151.11.17/32', \
                '15.0.120.4/32', '!10:655',\
                '1221:1221', '6', '->', 'PASS'] )


        assert new_line == ['192.151.11.17/32', '15.0.120.4/32',\
                           '10:655', '1221:1221', '6', '->', 'PASS']
        assert negs == [True, False, True, False, False]

    def test_check_negs2(self):
        new_line, negs = self.p.check_negs( ['192.151.11.17/32',\
                '15.0.120.4/32', '10:655', '1221:1221', '6',\
                '->', 'PASS'] )
        assert new_line == ['192.151.11.17/32', '15.0.120.4/32',\
                           '10:655', '1221:1221', '6', '->', 'PASS']
        assert negs == [False, False, False, False, False]

    def test_check_negs3(self):
        new_line, negs = self.p.check_negs( ['!192.151.11.17/32',\
                '!15.0.120.4/32', '!10:655', '!1221:1221', '!6', '->', 'DROP'] )
        assert new_line == ['192.151.11.17/32', '15.0.120.4/32',\
                '10:655', '1221:1221', '6', '->', 'DROP']
        assert negs == [True, True, True, True, True]


    def test_fields_to_intervals(self):
        f = ['192.151.11.17/32', '15.0.120.4/32', '10:655', '1221:1221',\
                           '6', '->', 'DROP']
        assert self.p.fields_to_intervals(f, '1') ==\
                [ Interval(3231124241, 3231124241),\
                  Interval(251688964, 251688964), Interval(10, 655),\
                  Interval(1221, 1221), Interval(6, 6), DROP ]

    def test_get_fields(self):
        rule = "192.151.11.17/32 15.0.120.4/32 10:655 1221:1221 6 -> DROP"
        parts = rule.split()
        assert self.p.get_fields(parts, '1') == [ [192, 151, 11, 17, 32],
                                            [15, 0, 120, 4, 32],
                                            [10, 655],
                                            [1221, 1221],
                                            6,
                                            DROP ]


    def test_parse(self):
        lines = ["!192.151.11.17/32 15.0.120.4/32 !10:655 1221:1221 6 -> DROP"]
        P = Parser(lines)
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

        assert P.parse() == [r1]

    def test_protocol_to_interval(self):
        assert self.p.protocol_to_interval(6) == Interval(6, 6)

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

    def test_sample_packet1(self):
        I = Interval
        rule = Rule(I(1, 5000), I(1, 6000), I(1, 30), I(1, 30), I(4, 4), PASS, '2') 
        p = rule.sample_packet()
        assert (p.sa in xrange(1, 5000 + 1)) and (p.da in xrange(1, 6000 + 1)) and \
               (p.sp in xrange(1, 30 + 1)) and (p.dp in xrange(1, 30 + 1)) and \
               p.pr == 4 and p.ac == PASS and p.rid == '2'

    def test_sample_packet2(self):
        I = Interval
        rule = Rule(I(1, 2), I(1, 2), I(1, 2), I(1, 2), I(4, 4), PASS, '2') 
        p = rule.sample_packet()
        assert (p.sa in xrange(1, 2 + 1)) and (p.da in xrange(1, 2 + 1)) and \
               (p.sp in xrange(1, 2 + 1)) and (p.dp in xrange(1, 2 + 1)) and \
               p.pr == 4 and p.ac == PASS and p.rid == '2'

    def test_sample_neg_packet(self):
        I = Interval
        rule = Rule(I(1, 2), I(1, 2), I(1, 2), I(1, 2), I(4, 4), PASS, '2') 
        p = rule.sample_neg_packet()
        assert (p.sa not in xrange(1, 2 + 1)) or \
               (p.da not in xrange(1, 2 + 1)) or \
               (p.sp not in xrange(1, 2 + 1)) or \
               (p.dp not in xrange(1, 2 + 1)) or \
               p.pr != 4 or p.ac != PASS or  p.rid == '2'


class TestTools(object):

    def test_check_nums_of_tests(self):
        T = Tools()
        allowed = NMIN + 1
        # Test 1
        T.check_nums_of_tests(allowed, allowed)

        # Test 2
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(NMAX + 1, NMAX + 1) 
        assert ERROR_STR1 in str(e)
        
        # Test 3
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(NMAX + 1, NMAX + 1) 
        assert ERROR_STR1 in str(e)

        # Test 4
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(NMIN - 1, NMIN - 1)
        assert ERROR_STR1 in str(e)

        # Test 5
        T.check_nums_of_tests(NMIN, allowed)

        # Test 6
        T.check_nums_of_tests(allowed, NMIN)

        # Test 7
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(allowed, NMIN - 1)
        assert ERROR_STR1 in str(e)

        # Test 8
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(NMAX + 1, allowed)
        assert ERROR_STR1 in str(e)

        # Test 9
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(allowed, NMAX + 1)
        assert ERROR_STR1 in str(e)

        # Test 10
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(NMIN, NMIN)
        assert ERROR_STR2 in str(e)

    def test_check_args(self):
        T = Tools()
        prog_name = 'tbgen.py'
        ok = 'ok'

        line1 = "!192.151.11.17/32 15.0.120.4/32 !10 : 655 1221 : 1221 0x06/0xff DROP\n"
        line2 = "192.151.11.17/0 15.0.120.4/24 1 : 100 1221 : 1221 0x06/0xff PASS\n"

        fname = "just_a_temporary_test_ruleset"
        with open(fname, "w+") as f:
            f.write(line1+line2)
            f.close()

        # valid args
        args = [prog_name, fname, '10', '10']
        assert T.check_args(args) == (fname, 10, 10)

        # too many args 
        args = [prog_name, fname, '10', '10', '3']
        with pytest.raises(TBGenError) as e:
            T.check_args(args)
        assert ERROR_STR3.rstrip(), ERROR_STR4 in str(e)

        # too few args
        args = [prog_name, fname, '10']
        with pytest.raises(TBGenError) as e:
            T.check_args(args)
        assert ERROR_STR3.rstrip(), ERROR_STR4 in str(e)

        # num-test-args are not numbers
        args = [prog_name, fname, 'a', 'b']
        with pytest.raises(TBGenError) as e:
            T.check_args(args)
        assert ERROR_STR7.rstrip(), ERROR_STR4 in str(e)

        # File doesn't exist or is empty
        new_fname = 'foo_ruleset'   # a non existent file
        args = [prog_name, new_fname, '10', '10']
        with pytest.raises(TBGenError) as e:
            T.check_args(args)
        assert ERROR_STR5.rstrip() in str(e)

        from os import remove
        remove(fname)

    def test_check_nums_of_tests1(self):
        T = Tools()
        # Argument is NOT in a valid range
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(100000, 12)
        assert ERROR_STR1 in str(e)

    def test_check_nums_of_tests2(self):
        T = Tools()
        # Case a == b == 0
        with pytest.raises(TBGenError) as e:
            T.check_nums_of_tests(0, 0)
        assert ERROR_STR2 in str(e)


    # Test at Index 0
    def test_dif1(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        rset = [r1, r2, r3]
        assert T.dif(0, rset) == [r1]

    # Test at Index 1
    def test_dif2(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        rset = [r1, r2, r3]

        v1 = Rule(I(1, 1), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        v2 = Rule(I(4, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        assert T.dif(1, rset) == [v1, v2]

    # Test at Index 2
    def test_dif3(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        rset = [r1, r2, r3]

        v = Rule(I(6, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        assert T.dif(2, rset)  == [v]

    # Test, where [rule - i for rule in return_set] == []
    def test_dif4(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        rset = [r2, r1]
        assert T.dif(1, rset) == []

#     @skip
    def test_dif5(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)

        rset = [r3, r2, r1]
        assert T.dif(1, rset) == []


    def test_make_flat(self):
        T = Tools()
        li = [[1, 2, 3], [4, 5], [7, 8, 9]]
        assert T.make_flat(li) == [1, 2, 3, 4, 5, 7, 8, 9]

    def test_make_independent_1(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        r4 = Rule(I(10, 15), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        r5 = Rule(I(1, 15), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 3)

        rset = [[r1, r2], [r3, r4], [r5]]

        assert T.make_independent(0, rset) == [r1, r2]

    def test_make_independent_2(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        r4 = Rule(I(10, 15), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        r5 = Rule(I(1, 15), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 4)

        rset = [[r1, r2], [r3, r4], [r5]]

        #     p1 = T.dif(2, [r1, r2, r3])
        p1 = Rule(I(6, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        #     p2 = T.dif(2, [r1, r2, r4])
        p2 = r4
        assert T.make_independent(1, rset) == [p1, p2]

    def test_make_independent_3(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 9), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        r4 = Rule(I(10, 15), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 2)
        r5 = Rule(I(1, 20), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 4)

        rset = [[r1, r2], [r3, r4], [r5]]

        r = Rule(I(16, 20), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 4)

        assert T.make_independent(2, rset) == [r]

    # Test, where output is []
    def test_make_independent_4(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        rset = [[r2], [r1]]
        assert T.make_independent(1, rset) == []

    def test_make_independent_5(self):
        I = Interval
        T = Tools()

        r1 = Rule(I(2, 3), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 0)
        r2 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        r3 = Rule(I(1, 5), I(1, 5), I(1, 5), I(1, 5), I(1, 5), DROP, 1)
        rset = [[r3], [r2], [r1]]
        assert T.make_independent(1, rset) == []

class Test_Packet(object):

    def test_in_rule1(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        P = Packet
        p1 = P(3, 3, 3, 3, 3, DROP, 1)
        assert p1.in_rule(r1)

    def test_in_rule2(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        P = Packet
        p1 = P(7, 3, 3, 3, 3, DROP, 1)
        assert not p1.in_rule(r1)

    def test_in_rule3(self):
        I = Interval
        r1 = Rule(I(1, 6), I(1, 6), I(1, 6), I(1, 6), I(1, 6), DROP, 1)
        P = Packet
        p1 = P(3, 3, 3, 3, 3, DROP, 2)
        assert not p1.in_rule(r1)


class Test_XML(object):

    def test_write_xml_to_file(self):
        I = Interval
        r1 = Rule(I(1, 1), I(1, 1), I(1, 1), I(1, 1), I(1, 1), DROP, 1)

        root = Element('tests')
        X = XML()
        r = X.create_xml_rule(root, str(r1.rule_id))
        X.generate_xml_packets_for_rule(r, r1, 1, True)
        fname = 'output.xml'
        X.write_xml_to_file(root, fname)

        f = open(fname)
        assert f.name == fname
        xml_str = '<tests><rule id="1"><packet id="p1"><src_addr>1</src_addr>'+\
        '<dst_addr>1</dst_addr><src_port>1</src_port><dst_port>1</dst_port>'+\
        '<protocol>1</protocol><action>DROP</action><match>True</match>'''+\
        '</packet></rule></tests>'
        assert f.read() == xml_str
        f.close()
        os.remove(fname)

    def test_raw_xml_format(self):
        I = Interval
        r1 = Rule(I(1, 1), I(1, 1), I(1, 1), I(1, 1), I(1, 1), DROP, 1)

        root = Element('tests')
        X = XML()
        r = X.create_xml_rule(root, str(r1.rule_id))
        X.generate_xml_packets_for_rule(r, r1, 1, True)

        xml_str = '<tests><rule id="1"><packet id="p1"><src_addr>1</src_addr>'+\
        '<dst_addr>1</dst_addr><src_port>1</src_port><dst_port>1</dst_port>'+\
        '<protocol>1</protocol><action>DROP</action><match>True</match>'''+\
        '</packet></rule></tests>'
        assert X.raw_xml_format(root) == xml_str

    def test_pretty_format(self):
        I = Interval
        r1 = Rule(I(1, 1), I(1, 1), I(1, 1), I(1, 1), I(1, 1), DROP, 1)

        root = Element('tests')
        X = XML()
        r = X.create_xml_rule(root, str(r1.rule_id))
        X.generate_xml_packets_for_rule(r, r1, 1, True)
        xml_str = """<?xml version="1.0" ?>
<tests>
    <rule id="1">
        <packet id="p1">
            <src_addr>1</src_addr>
            <dst_addr>1</dst_addr>
            <src_port>1</src_port>
            <dst_port>1</dst_port>
            <protocol>1</protocol>
            <action>DROP</action>
            <match>True</match>
        </packet>
    </rule>
</tests>
"""
        assert X.pretty_xml_format(root) == xml_str

    def test_create_xml_rule(self):
        I = Interval
        r1 = Rule(I(1, 1), I(1, 1), I(1, 1), I(1, 1), I(1, 1), DROP, 1)

        root = Element('tests')
        X = XML()
        r = X.create_xml_rule(root, str(r1.rule_id))
        generated = X.raw_xml_format(root) 
        xml_str = '<tests><rule id="1" /></tests>'
        assert xml_str == generated

    def test_create_xml_packet(self):
        I = Interval
        r1 = Rule(I(1, 1), I(1, 1), I(1, 1), I(1, 1), I(1, 1), DROP, 1)

        root = Element('tests')
        X = XML()
        r = X.create_xml_rule(root, str(r1.rule_id))
        X.create_xml_packet(r, 'p' + str(1), str(1), str(1), str(1), str(1),\
                                     str(1), str(r1.action), str(DROP)) 
     
        generated = X.raw_xml_format(root) 
        xml_str = '<tests><rule id="1"><packet id="p1"><src_addr>1</src_addr>' + \
        '<dst_addr>1</dst_addr><src_port>1</src_port><dst_port>1</dst_port>' + \
        '<protocol>1</protocol><action>2</action><match>2</match>' + \
        '</packet></rule></tests>'
        assert xml_str == generated

    def test_generate_xml_packets_for_rule(self):
        I = Interval
        r1 = Rule(I(1, 1), I(1, 1), I(1, 1), I(1, 1), I(1, 1), DROP, 1)

        root = Element('tests')
        X = XML()
        r = X.create_xml_rule(root, str(r1.rule_id))
        
        X.generate_xml_packets_for_rule(r, r1, 2, True) 

        generated = X.raw_xml_format(root) 

        xml_str = \
        '<tests><rule id="1"><packet id="p1"><src_addr>1</src_addr>'+\
        '<dst_addr>1</dst_addr><src_port>1</src_port>' +\
        '<dst_port>1</dst_port><protocol>1</protocol><action>DROP</action>'+\
        '<match>True</match></packet><packet id="p2">' +\
        '<src_addr>1</src_addr><dst_addr>1</dst_addr>' +\
        '<src_port>1</src_port><dst_port>1</dst_port>' +\
        '<protocol>1</protocol><action>DROP</action><match>True</match>'+\
        '</packet></rule></tests>'

        assert xml_str == generated



