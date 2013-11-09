
from sys import argv
from pdb import set_trace
import os

# from interval import (Interval, IntervalList)

# -------------- CONSTANTS --------------------------------------
PASS = 1
DROP = 2


MIN_ADDR = 0
MAX_ADDR = int(2 ** 32 - 1)

MIN_PORT = 0
MAX_PORT = int(2 ** 16 - 1)

MIN_PROT = 0
MAX_PROT = int(2 ** 8 - 1)

NMIN = 0          # Minimal number of tests
NMAX = 1000       # Maximal number of tests
OK_STR = 'ok'
ERROR_STR1 = "Error : some args are not in allowed range (%i, %i)" %(NMIN, NMAX)
ERROR_STR2 = 'Error : you haven\'t specified any valid number of tests...'
ERROR_STR3 = "Error : Invalid args!\n"
ERROR_STR4 = 'Usage: python %s <Firewall-Rule-Set-File> <Num of positive Tests> <Num of negative Tests>' % argv[0]
# ERROR_STR5 = 'Error : File "%s" doesn\'t exist or is empty!\n' %argv[1]
ERROR_STR5 = 'Error : File doesn\'t exist or is empty!\n'
ERROR_STR6 = 'Error : Invalid Rule Structure in Rule : '

# --------------------------------------------------------------
# TODO
# + NO magic numbers!
# + do error checking in parser and test it
# + fix ALL broken tests
# - implement method on class Rule __sub__ (plenty of tests!)
# - Implement function/method to make rules independent!
#   This function/method should use subtraction of Rule objects!
# - implement Rule subtraction


# class Action(object):
#     
#     def __init__(self, action_id):
#         self.action_id = action_id
# 
#     def __eq__(self, other):
#         return self.action_id == other.action_id
# 
#     def __ne__(self, other):
#         return not self == other

# Class Interval
# 

class Interval(object):
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


class Parser(object):

    def __init__(self, lines, ):
        self.lines = lines


    def parse(self):
        file_lines = self.lines
        rules = []
        for rule_id, line in enumerate(file_lines):
            parts = line.split()
            if len(parts) != 10:
                print_error_and_exit(ERROR_STR6 + str(rule_id))
            no_negs_list, negs = self.check_negs(parts)

            args = self.fields_to_intervals(no_negs_list, rule_id) +\
                    negs + list(str(rule_id))
            rules.append(RawRule(*args))
        return rules


    def check_negs(self, parts):
        """ Check for Field-Negators, remove them and return a boolean list of
            negated and not negated fields
        """
        res = []
        for i in (0, 1, 2, 5, 8):   # Index-Set of negatable fields
            if parts[i][0] == '!':
                res.append(True)
                parts[i] = parts[i][1:]
            else:
                res.append(False)
        return parts, res

    def fields_to_intervals(self, fields, r_id):
        f = self.get_fields(fields, r_id)
        sh = self.subnet_to_interval(f[0])
        dh = self.subnet_to_interval(f[1])
        sp = self.port_to_interval(f[2])
        dp = self.port_to_interval(f[3])
        pr = self.protocol_to_interval(f[4])
        action = f[5]
        return [sh, dh, sp, dp, pr, action]

    def get_fields(self, fields, r_id):

        rule_str = " in Rule: " + str(r_id)

        def split_subnet_str(field):
            a = field.split('/')
            return map(int, a[0].split('.')) + [int(a[1])]

        def check_subnet(parts, msg):
            for i in parts[:-1]:
                if i < 0 or i > 255:
                    print_error_and_exit(msg + rule_str)
            if parts[-1] <0 or parts[-1]>32:
                print_error_and_exit(msg + "Invalid Mask" + rule_str)

        def check_port(parts, msg):
            for i in parts:
                if i<MIN_PORT or i>MAX_PORT:
                    print_error_and_exit(msg + rule_str)

        def check_protocol(p):
            if p[0] < MIN_PROT or p[0] > MAX_PROT:
                print_error_and_exit("Error : Invalid Procotol Number" + rule_str)
            if p[1] not in [0, 255]:
                print_error_and_exit("Error : Invalid Protocol Mask" + rule_str)


        src_host = split_subnet_str(fields[0])
        check_subnet(src_host, "Error : Invalid Source Net! ")

        dst_host = split_subnet_str(fields[1])
        check_subnet(dst_host, "Error : Invalid Destination Net! ")

        src_port = [int(fields[2]), int(fields[4])]
        check_port(src_port, "Error : Invalid Source Port")

        dst_port = [int(fields[5]), int(fields[7])]
        check_port(dst_port, "Error : Invalid Destination Port")

        protocol = [int(x, 0) for x in fields[8].split('/')]
        check_protocol(protocol)

        _action = fields[9]
        if _action == 'DROP':
            action = DROP
        elif _action == 'PASS':
            action = PASS
        else:
            print_error_and_exit("Error : '%s' is an unknown rule action!"\
                    % _action + rule_str)

        return [src_host, dst_host, src_port, dst_port, protocol, action]
               
    def protocol_to_interval(self, protocol):
        if protocol[1] == 0:
            return Interval(MIN_PROT, MAX_PROT)
        return Interval(protocol[0], protocol[0])

    def port_to_interval(self, field):
        a, b = field
        return Interval(a, b)

    def subnet_to_interval(self, field):
        """ Transforms a subnet of the form 'a.b.c.d/mask_bits'
            to an Interval object.
        """
        a, b, c, d, mask = field
        base_addr = (a << 24) | (b << 16) | (c << 8) | d
        zero_bits = 32 - mask
        # zero out rightmost bits according to mask
        base_addr = (base_addr >> zero_bits) << zero_bits
        high_addr = base_addr + (2 ** zero_bits) - 1
        return Interval(base_addr, high_addr)


class RawRule(object):

    def __init__(self, src_host, dst_host, src_port, dst_port, protocol,\
                action, src_host_neg, dst_host_neg, src_port_neg,\
                dst_port_neg, prot_neg, rule_id):
        self.src_host = src_host
        self.dst_host = dst_host
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.action = action
        self.src_host_neg = src_host_neg
        self.dst_host_neg = dst_host_neg
        self.src_port_neg = src_port_neg
        self.dst_port_neg = dst_port_neg
        self.prot_neg     = prot_neg
        self.rule_id = rule_id

    def _negate(self, field, min_value, max_value, neg_state):
        if neg_state == False:
            return [field]
        return field.negate(min_value, max_value)

    def normalize(self):
        """ Returns a list of normalized Rule objects.
        """
        rules = []
        src_nets = self._negate(self.src_host, MIN_ADDR, MAX_ADDR,\
                self.src_host_neg)
        dst_nets = self._negate(self.dst_host, MIN_ADDR, MAX_ADDR,\
                self.dst_host_neg)
        src_ports = self._negate(self.src_port, MIN_PORT, MAX_PORT,\
                self.src_port_neg)
        dst_ports = self._negate(self.dst_port, MIN_PORT, MAX_PORT,\
                self.dst_port_neg)
        prots = self._negate(self.protocol, MIN_PROT, MAX_PROT,\
                self.prot_neg)
        for src_net in src_nets:
            for dst_net in dst_nets:
                for src_port in src_ports:
                    for dst_port in dst_ports:
                        for prot in prots:
                            rule = Rule(src_net, dst_net, src_port, dst_port,
                                    prot, self.action, self.rule_id)
                            rules.append(rule)
        return rules

    def __str__(self):
        s1 = "RawRule: sn%s dn%s sp%s dp%s prot%s"\
        % (self.src_host, self.dst_host, self.src_port, self.dst_port,
                   self.protocol) 
        s2 = " id(%s) action(%s) neg(%i %i %i %i %i)"\
               % (self.rule_id, self.action, self.src_host_neg,
                   self.dst_host_neg, self.src_port_neg, self.dst_port_neg,
                   self.prot_neg)
        return s1 + s2

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, RawRule):
            return False
        return self.src_host == other.src_host and\
        self.dst_host == other.dst_host and\
        self.src_port == other.src_port and\
        self.dst_port == other.dst_port and\
        self.protocol == other.protocol and\
        self.action == other.action and\
        self.src_host_neg == other.src_host_neg and\
        self.dst_host_neg == other.dst_host_neg and\
        self.src_port_neg == other.src_port_neg and\
        self.dst_port_neg == other.dst_port_neg and\
        self.prot_neg     == other.prot_neg and\
        self.rule_id == other.rule_id 

    def __ne__(self, other):
        return not self == other


class Rule(object):
    """ Represents a normalized firewall rule, i.e. there are no more negated
        fields.
    """
    
    def __init__(self, src_net, dst_net, src_ports, dst_ports, prots,\
                       action, rule_id):
        self.src_net = src_net
        self.dst_net = dst_net
        self.src_ports = src_ports
        self.dst_ports = dst_ports
        self.prots = prots
        self.action = action
        self.rule_id = rule_id

    def __sub__(self, other):
        assert 0, "please implement me!"

    def __eq__(self, other):
        return  self.src_net == other.src_net\
            and self.dst_net == other.dst_net\
            and self.src_ports == other.src_ports\
            and self.dst_ports == other.dst_ports\
            and self.prots == other.prots\
            and self.rule_id == other.rule_id\
            and self.action == other.action

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "Rule:  %s %s %s %s %s %s %s" % (self.src_net, self.dst_net,
               self.src_ports, self.dst_ports, self.prots, self.action,
               self.rule_id)

    def __repr__(self):
        return str(self)

# ------------------------ MAIN ---------------------------------------------
NMIN = 0
NMAX = 1000

def check_args(a, b):
    """ Checks args, defining amount of pos. & neg. tests.
    """
    r = True
    message = OK_STR
    trange = range(NMIN, NMAX)
    if a == b == 0:
        message = ERROR_STR2
        r = False
    if a not in trange or b not in trange:
        message = ERROR_STR1
        r = False
    return r, message

def print_error_and_exit(message):
    print message
    exit(0)

def read_file():
    """ Reads a given file, num of pos. & neg. tests from promt.
        Returns Stringlines, num of pos. & neg. tests
    """ 
#     set_trace()
    if len(argv) == 4:
        fname = argv[1]
        pos_tests = int(argv[2])
        neg_tests = int(argv[3])

        ok, message = check_args(pos_tests, neg_tests)
        if ok != True:
            print_error_and_exit(message)
        if os.path.exists(fname) and os.stat(fname).st_size != 0:
            with open(fname) as f:
                lines = f.readlines()
        else:
            print_error_and_exit(ERROR_STR5)
    else:
        print_error_and_exit(ERROR_STR3 + ERROR_STR4)
    return lines, pos_tests, neg_tests

def main():
    lines, pos, neg = read_file()
    p = Parser(lines)
    p1, p2 = p.parse()
    print p1
    print p2
# 
#     def rawrule_attrs(rule):
#         print rule.src_host
#         print rule.dst_host
#         print rule.src_port
#         print rule.dst_port
#         print rule.protocol
# 
# #     rawrule_attrs(r1)
#     print "\n"
#     for i in p1.normalize():
#         print i
#         

if __name__ == '__main__': main()
