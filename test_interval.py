import pytest, pdb
from interval import Interval, IntervalList

skip = pytest.mark.skipif

# def test_is_empty():
#     a = Interval(1, 5)
#     x = a - a
#     assert x.is_empty()
#     y = Interval(4,4)
#     assert not y.is_empty()

def test_has_intersection():
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

def test_has_identical_borders():
    x = Interval(5, 10)
    y = Interval(5, 8)
    z = Interval(6, 10)
    assert x.has_identical_borders(y)
    assert x.has_identical_borders(z)
    assert x.has_identical_borders(x)

def test_dif():
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

# FIXME: Result is always a List!
    # subtract two identical interval
    i1 = Interval(1, 2)
    assert i1 - i1 == []

    i2 = Interval(1, 3)
    assert i2 - i1 == [Interval(3, 3)]

    i3 = Interval(0, 5)
    assert i3 - i1 == [Interval(0, 0), Interval(3, 5)]
    assert i1 - i3 == []


def test_is_subinterval():
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

def test__un():
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

def test_union():
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

def test_intersect():
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


def test_negate():
    x  = Interval(10, 15)
    assert x.negate(0, 20) == [Interval(0, 9), Interval(16, 20)]

    x = Interval(10, 10)
    assert x.negate(0, 20) == [Interval(0, 9), Interval(11, 20)]

@skip
def test_empty_Intervals():
    x = []
    y = Interval(4, 8)
    assert x.has_intersection(x)
    assert x.has_identical_borders(x)
    assert y - x == [y]
    assert x - y == [x]
    assert x - x == [x]
    assert x.is_subinterval(x)
    assert x + y == [y]
    assert x.intersect(y) == y.intersect(x) == []
    assert x.negate() == [Interval(x.range_min, x.range_max)]

@skip
def test_sub():         # see test_dif() for more
    x = Interval(1, 10)
    y = Interval(5, 10)
    z = Interval(8, 10)
    w = Interval(6, 8)
    assert (x - y) == [Interval(1, 4)]
    assert (x - z - w) == [Interval(1, 5)]
    assert (x - w) == [Interval(1, 5), Interval(9, 10)]

@skip
def test_add():         # see test_union() for more
    x = Interval(1, 5)
    y = Interval(3, 9)
    z = Interval(10, 15)
    assert x + y ==  x + y + x == Interval(1, 9)
    assert x + y + z == (Interval(1, 9), Interval(10, 15))


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


