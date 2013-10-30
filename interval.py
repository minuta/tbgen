# Class Interval
# 
# Essential Features :
#    1. Union
#    2- Difference
#    3. Intersection
#    4. Negation
#    5. works correctly with empty Intervals
#    6. check for an empty Intervals
#    7- check for a subinterval
#    8. check for intersection
# 
# Notes:
# use [] for a an empty interval 

import pdb, pytest

skip = pytest.mark.skipif

class Interval(object):


    # TODO:
    #   * make return values of relevant Interval operations of
    #     IntervalList type
    #   * start implementation of class Rule as sketched in meeting
    #   * start implement Rule parser
    #   * recommendation: write two rule classes:
    #     - RawRule (parser output)
    #     - Rule (normalier output)
    #   * fix tests
    #   * implement functiob subnet_to_range

    def __init__(self, a, b):
#         self.range_min = 1
#         self.range_max = 20
        self.a = a
        self.b = b

    def __repr__(self):
#         if self == []:
#             return '[]'
        return '[%s : %s]' %(self.a, self.b)

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other

    def _un(self, other):
        """self.a <= other.a."""
        if other.is_subinterval(self):
            return [Interval(self.a, self.b)]
        if self.b < other.a:
            return [Interval(self.a, self.b), Interval(other.a, other.b)]
        return [Interval(self.a, other.b)]

    def __sub__(self, other):
        if isinstance(self, list):
            return self[0].dif(other)
        return self.dif(other)

#     def sub(self, other):
#         if isinstance(self, list):
#             for i in self:
    def __add__(self, other):
        return self.union(other)

    def is_subinterval(self, other):
        return self.a >= other.a and self.b <= other.b

    def has_intersection(self, other):
        return not (self.b < other.a or other.b < self.a)

    def has_identical_borders(self, other):
        return (self.a == other.a or self.b == other.b)

    def union(self, other):
        if self == []:
            return [other]
        if self == other or other == []:
            return [self]
        if self.a <= other.a:
            return self._un(other)
        elif self.a > other.a:
            return other._un(self)

    def dif(self, other):
        if self.has_intersection(other):        # Interssection
            if self == other or self.is_subinterval(other):
                return []

            if other.is_subinterval(self):      # other is Subinterval of self
                if not self.has_identical_borders(other):
                    return [Interval(self.a, other.a - 1), \
                           Interval(other.b + 1, self.b)]
                elif self.a == other.a:
                    return [Interval(other.b + 1, self.b)]
                else:
                    return [Interval(self.a, other.a - 1)]

            if self.a < other.a:
                return [Interval(self.a, other.a - 1)]
            if self.b > other.b:
                return [Interval(other.b + 1, self.b)]

        else:  # no intersection
            return [self]

    def intersect(self, other):
        if self.has_intersection(other):
            if self == other or self.is_subinterval(other):
                return [self]
            elif other.is_subinterval(self):
                return [other]
            if self.a < other.a:
                return [Interval(other.a, self.b)]
            else :
                return [Interval(self.a, other.b)]
        else:
            return []

    def negate(self, range_min, range_max):
        """Negates interval according to Range-Borders a, b. """
        return Interval(range_min, range_max).dif(self)

    def interval_len(self):
        return self.b - self.a + 1

# ------------------------------------------------------------------------

class IntervalList(object):

    def __init__(self, intervals):
        # intervals is a Python list of Interval objects
        self.intervals = intervals

    def __sub__(self, interval):
        new_list = []
        for my_interval in self.intervals:
            for i in range(0, len(interval)):
                difference_list = my_interval - interval.get_interval(i)
                new_list.extend(difference_list)
        return IntervalList(new_list)

    def __add__(self, other):
        res = []
        for i in self.intervals:
            for a in other.intervals:
                res.extend(i.union(a))
        return IntervalList(res)

    def remove_duplicates(self):
        res = []
        for i in self.intervals:
            if i not in res:
                res.append(i)
        return res

    def __len__(self):
        return len(self.intervals)

    def get_interval(self, index):
        return self.intervals[index]

    def __eq__(self, other):
        if not isinstance(other, IntervalList):
            raise ValueError("%s cannot be compared to IntervalList object!"
                    % other)
        if len(self) != len(other):
            return False
        for i in range(0, len(self)):
            if self.get_interval(i) not in other.intervals: 
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '%s' %(self.intervals)

    def __repr__(self):
        return '%s' %(self.intervals)

# ------------------- MAIN  -------------------------------------------------

def main():

    a = IntervalList([Interval(1, 10), Interval(8, 12)])
    b = IntervalList([Interval(14, 16), Interval(20, 30)])

    print (a + b).remove_duplicates()

__name__ == "__main__" and main()
