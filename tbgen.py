# Usage: python tbgen.py <ruleset-file> <num of pos.tests> <num of neg.tests>
#
# Output : test packets for given rules in XML-format
#
# Note :
# 1) Bounds for minimal and maximal number of tests are defined in section:
#    "CONSTANTS" below.
# 2) Rule format should have a following form :
#    <src-net> <dst-net> <src-port> <dst-port> <protocol> "->" <action>
#
#    all first 5 fields can be negated via '!' character
#
#    Example :
#         !192.151.11.17/32 15.0.120.4/32 !10 : 655 1221 : 1221 !6  -> DROP

import os
import pytest
import errno
from sys import argv
# from pdb import set_trace
from random import randint
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
from xml.dom import minidom

skip = pytest.mark.skipif

# -------------- CONSTANTS --------------------------------------
# Firewall actions
PASS = 1
DROP = 2

# minimal/maximal IP-address in int-representation
MIN_ADDR = 0
MAX_ADDR = int(2 ** 32 - 1)

# minimal/maximal port number
MIN_PORT = 0
MAX_PORT = int(2 ** 16 - 1)

# minimal/maximal protocol number
MIN_PROT = 0
MAX_PROT = int(2 ** 8 - 1)

# minimal/maximal number of tests
NMIN = 0
NMAX = 1000

OK = 'ok'

# Error strings for Class "TBGenError"
ERROR_STR1 = "Error : some args are not in allowed range\
        (%i, %i)" % (NMIN, NMAX)
ERROR_STR2 = 'Error : you haven\'t specified any valid number of tests...'
ERROR_STR3 = "Error : Invalid args!\n"

ERROR_STR41 = '<Num of positive Tests> <Num of negative Tests>'
ERROR_STR4 = 'Usage: python %s <Firewall-Rule-Set-File> ' % argv[0]+ERROR_STR41

ERROR_STR5 = 'Error : File doesn\'t exist or is empty!\n'
ERROR_STR6 = 'Error : Invalid Rule Structure in Rule : '
ERROR_STR7 = "Error : Wrong argument type!\n"

counter = 0 # Counter of rule difs (Used only for Debug and statistics)
# --------------------------------------------------------------------


class TBGenError(Exception):
    """ Class "TBGenError" defines custom exceptions.
    """
    def __init__(self, m):
        self.m = m

    def __str__(self):
        return self.m


class Interval(object):
    """ Class "Interval" defines a closed interval of form [a, b] and methods
        for working with intervals like union, difference, intersection, etc.
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return '[%s:%s]' % (self.a, self.b)

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
                    return [Interval(self.a, other.a - 1),
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
        """ returns an intersection between 2 intervals.
            if no intersection, it returns an empty list.  """
        if self.has_intersection(other):
            if self == other or self.is_subinterval(other):
                return [self]
            elif other.is_subinterval(self):
                return [other]
            if self.a < other.a:
                return [Interval(other.a, self.b)]
            else:
                return [Interval(self.a, other.b)]
        else:
            return []

    def negate(self, range_min, range_max):
        """Negates interval according to Range-Borders a, b. """
        return Interval(range_min, range_max).dif(self)

    def interval_len(self):
        return self.b - self.a + 1

    def random_value(self):
        return randint(self.a, self.b)

    def random_neg_value(self, range_min, range_max):
        if self == Interval(range_min, range_max):
            return False, self.random_value()
        i = self.negate(range_min, range_max)
        return True, i[0].random_value()


class IntervalList(object):
    """ Class "IntervalList" makes possible to operate with lists of intervals,
        Operators are addition, difference, etc.
    """

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
        return '%s' % (self.intervals)

    def __repr__(self):
        return '%s' % (self.intervals)


class Parser(object):
    """ Class "Parser" gets a list of raw lines from a ruleset-file and returns
        a list of Rawrule-objects.
    """

    def __init__(self, lines, ):
        self.lines = lines

    def parse(self):
        file_lines = self.lines
        rules = []
        for rule_id, line in enumerate(file_lines):
            parts = line.split()

            if len(parts) != 7:
                raise TBGenError(ERROR_STR6 + str(rule_id))
            no_negs_list, negs = self.check_negs(parts)

            args = self.fields_to_intervals(no_negs_list, rule_id) + negs +\
                [str(rule_id)]

            rules.append(RawRule(*args))
        return rules

    def check_negs(self, parts):
        """ Check for Field-Negators, remove them and return a boolean list of
            negated and not negated fields
        """
        res = []
        for i in (0, 1, 2, 3, 4):   # Index-Set of negatable fields
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
                    raise TBGenError(msg + rule_str)
            if parts[-1] < 0 or parts[-1] > 32:
                raise TBGenError(msg + "Invalid Mask" + rule_str)

        def check_port(parts, msg):
            for i in parts:
                if i < MIN_PORT or i > MAX_PORT:
                    raise TBGenError(msg + rule_str)

        def check_protocol(p):
            if p < MIN_PROT or p > MAX_PROT:
                raise TBGenError("Error : Invalid Procotol Number" + rule_str)

        src_host = split_subnet_str(fields[0])
        check_subnet(src_host, "Error : Invalid Source Net! ")

        dst_host = split_subnet_str(fields[1])
        check_subnet(dst_host, "Error : Invalid Destination Net! ")

        src_port = [int(i) for i in fields[2].split(':')]
        check_port(src_port, "Error : Invalid Source Port")

        dst_port = [int(i) for i in fields[3].split(':')]
        check_port(dst_port, "Error : Invalid Destination Port")

        prot_nr = int(fields[4])
        check_protocol(prot_nr)

        _action = fields[6]
        if _action == 'DROP':
            action = DROP
        elif _action == 'PASS':
            action = PASS
        else:
            raise TBGenError("Error : '%s' is an unknown rule action!"
                             % _action + rule_str)

        return [src_host, dst_host, src_port, dst_port, prot_nr, action]

    def protocol_to_interval(self, prot_nr):
        return Interval(prot_nr, prot_nr)

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
    """ Class "RawRule" takes a parsed rule data and normalizes it. "normalize"
        means a rule will be transformed to an equivalent rule/rules
        without negations. We get a list of Rule-objects as output.
    """

    def __init__(self, src_host, dst_host, src_port, dst_port, protocol,
                 action, src_host_neg, dst_host_neg, src_port_neg,
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
        self.prot_neg = prot_neg
        self.rule_id = rule_id

    def _negate(self, field, min_value, max_value, neg_state):
        if neg_state is False:
            return [field]
        return field.negate(min_value, max_value)

    def normalize(self):
        """ Returns a list of normalized Rule objects.
        """
        rules = []
        src_nets = self._negate(self.src_host, MIN_ADDR, MAX_ADDR,
                                self.src_host_neg)
        dst_nets = self._negate(self.dst_host, MIN_ADDR, MAX_ADDR,
                                self.dst_host_neg)
        src_ports = self._negate(self.src_port, MIN_PORT, MAX_PORT,
                                 self.src_port_neg)
        dst_ports = self._negate(self.dst_port, MIN_PORT, MAX_PORT,
                                 self.dst_port_neg)
        prots = self._negate(self.protocol, MIN_PROT, MAX_PROT,
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
        return (self.src_host == other.src_host and
                self.dst_host == other.dst_host and
                self.src_port == other.src_port and
                self.dst_port == other.dst_port and
                self.protocol == other.protocol and
                self.action == other.action and
                self.src_host_neg == other.src_host_neg and
                self.dst_host_neg == other.dst_host_neg and
                self.src_port_neg == other.src_port_neg and
                self.dst_port_neg == other.dst_port_neg and
                self.prot_neg == other.prot_neg and
                self.rule_id == other.rule_id)

    def __ne__(self, other):
        return not self == other

class Rule2(object):
    """ Represents a 2d-Rule and used for testing sub-function. """ 

    def __init__(self, src_ports, dst_ports):
        self.i1 = src_ports
        self.i2 = dst_ports

    def __eq__(self, other):
        return (self.i1 == other.i1 and self.i2 == other.i2)

    def __ne__(self, other):
        return not self == other
    
    def __str__(self):
        return "Rule2:  %s  %s" % (self.i1, self.i2)

    def __repr__(self):
        return str(self)

    def __sub__(self, other):
        i1_intersect = self.i1.intersect(other.i1)
        i2_intersect = self.i2.intersect(other.i2)
        if (len(i1_intersect) & len(i2_intersect)) == 0:
            return [self]

        r1 = [Rule2(i, self.i2) for i in (self.i1 - other.i1)]

        r2 = [Rule2(i1_intersect[0], i) for i in (self.i2 - other.i2)]

        return r1 + r2


class Rule(object):
    """ Represents a normalized firewall rule, i.e. there are no more negated
        fields.
    """

    def __init__(self, src_net, dst_net, src_ports, dst_ports, prots, action,
                 rule_id):
        self.i1 = src_net
        self.i2 = dst_net
        self.i3 = src_ports
        self.i4 = dst_ports
        self.i5 = prots
        self.action = action
        self.rule_id = rule_id

    def __eq__(self, other):
        return (self.i1 == other.i1 and
                self.i2 == other.i2 and
                self.i3 == other.i3 and
                self.i4 == other.i4 and
                self.i5 == other.i5 and
                self.rule_id == other.rule_id and
                self.action == other.action)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "Rule:  %s %s %s %s %s %s %s"\
               % (self.i1, self.i2, self.i3, self.i4, self.i5, self.action,
                  self.rule_id)

    def __repr__(self):
        return str(self)

    def __sub__(self, other):
        """ Difference of two 5-dim-sets. """

        global counter
        counter += 1

        # if no intersection in at least one dimension =>No intersection at all
        # => function returns a list with a self-rule
        i1_intersect = self.i1.intersect(other.i1)
        i2_intersect = self.i2.intersect(other.i2)
        i3_intersect = self.i3.intersect(other.i3)
        i4_intersect = self.i4.intersect(other.i4)
        i5_intersect = self.i5.intersect(other.i5)
        if (len(i1_intersect) & len(i2_intersect) & len(i3_intersect) & 
                len(i4_intersect) & len(i5_intersect)) == 0:
            return [self]


        r1 = [Rule(i, self.i2, self.i3, self.i4, self.i5,
              self.action, self.rule_id) for i in (self.i1 - other.i1)]

        r2 = [Rule(i1_intersect[0], i, self.i3, self.i4, self.i5,
              self.action, self.rule_id) for i in (self.i2 - other.i2)]

        r3 = [Rule(i1_intersect[0], i2_intersect[0], i, self.i4, self.i5,
              self.action, self.rule_id) for i in (self.i3 - other.i3)]

        r4 = [Rule(i1_intersect[0], i2_intersect[0], i3_intersect[0], i,
              self.i5, self.action, self.rule_id) for i in
              (self.i4 - other.i4)]

        r5 = [Rule(i1_intersect[0], i2_intersect[0], i3_intersect[0],
              i4_intersect[0], i, self.action, self.rule_id) for i in
              (self.i5 - other.i5)]
        return r1 + r2 + r3 + r4 + r5

    def sample_packet(self):
        sa = self.i1.random_value()
        da = self.i2.random_value()
        sp = self.i3.random_value()
        dp = self.i4.random_value()
        pr = self.i5.random_value()
        return Packet(sa, da, sp, dp, pr, self.action, self.rule_id)

    def sample_neg_packet(self):
        ok_sa, sa = self.i1.random_neg_value(MIN_ADDR, MAX_ADDR)
        ok_da, da = self.i2.random_neg_value(MIN_ADDR, MAX_ADDR)
        ok_sp, sp = self.i3.random_neg_value(MIN_PORT, MAX_PORT)
        ok_dp, dp = self.i4.random_neg_value(MIN_PORT, MAX_PORT)
        ok_pr, pr = self.i5.random_neg_value(MIN_PROT, MAX_PROT)

        if ok_sa or ok_da or ok_sp or ok_dp or ok_pr:
            return Packet(sa, da, sp, dp, pr, self.action, self.rule_id)
        raise TBGenError("Error : couldn't generate a negative packet\
                         for rule ")


class Packet(object):
    """ Class "Packet" defines a single packet in a firewall rule and
        its characteristics, like source/destination, protocol, action,
        rule id.
    """

    def __init__(self, sa, da, sp, dp, pr, ac, rid):
        self.sa = sa    # source address
        self.da = da    # destination address
        self.sp = sp    # source port
        self.dp = dp    # destination port
        self.pr = pr    # protocol
        self.ac = ac    # action
        self.rid = rid  # rule id for this packet

    def __str__(self):
        return "Packet:  %s %s %s %s %s %s %s" %\
               (self.sa, self.da, self.sp, self.dp, self.pr, self.ac, self.rid)

    def __repr__(self):
        return str(self)

    def in_rule(self, rule):
        I = Interval
        return (I(self.sa, self.sa).is_subinterval(rule.i1) and
                I(self.da, self.da).is_subinterval(rule.i2) and
                I(self.sp, self.sp).is_subinterval(rule.i3) and
                I(self.dp, self.dp).is_subinterval(rule.i4) and
                I(self.pr, self.pr).is_subinterval(rule.i5) and
                self.ac == rule.action and
                self.rid == rule.rule_id)


class Tools(object):
    """ Class "Tools" has some extra class-independent functions, which can't
        be assigned to other classes.
    """
    def check_nums_of_tests(self, a, b):
        """ Checks args, defining amount of pos. & neg. tests.  """
        trange = range(NMIN, NMAX)
        if a == b == 0:
            raise TBGenError(ERROR_STR2)
        if a not in trange or b not in trange:
            raise TBGenError(ERROR_STR1)

    def print_error_and_exit(self, message, error_num):
        print message
        exit(error_num)

    def check_args(self, argv):
        fname = None
        pos_tests = 0
        neg_tests = 0

        if len(argv) == 4:
            fname = argv[1]
            if not argv[2].isdigit() or not argv[3].isdigit():
                raise TBGenError(ERROR_STR7 + ERROR_STR4)
            else:
                pos_tests = int(argv[2])
                neg_tests = int(argv[3])
                self.check_nums_of_tests(pos_tests, neg_tests)

                if not (os.path.exists(fname) and os.stat(fname).st_size != 0):
                    raise TBGenError(ERROR_STR5)
        else:
            raise TBGenError(ERROR_STR3 + ERROR_STR4)

        return fname, pos_tests, neg_tests

    def make_flat(self, l):
        """ makes l, which is a list of lists a flat list """
        return [item for sublist in l for item in sublist]

    def dif(self, index, rset):
        """ Difference of a rule at given index "index" in rset with rules of rset
            between index 0 and "index". rset is a Flat-List!
            As output we get an unnested list of rules like :
            [... [[[r-r1]-r2]-r3]-... - rn]
            where r is a rule at index "index" and
            r1 .. rn are rules between index 0 and index "index"
        """
        if index > 0:
            return_set = [rset[index]]
            for i in rset[:index]:
                try:
                    return_set = filter(None, [rule - i for
                                        rule in return_set])[0]
                except IndexError:
                    return_set = []
            return return_set
        else:
            return [rset[0]]

    def make_independent(self, index, rset):
        """ Like Tools.dif, but rset is not a Flat-List. Thus, we have to
            handle lists of lists.
        """
        if index == 0:
            return rset[0]
        ret_set = []
        target_rules = rset[index]
        operator_rules = rset[:index]

        for rule in target_rules:
            flat_set = self.make_flat(operator_rules + [[rule]])
            try:
                ret_set.append(self.dif(len(flat_set) - 1, flat_set)[0])
            except IndexError:
                ret_set = []
        return ret_set


class XML(object):
    """ Class "XML" creates an XML-file for a given rules and packets.
    """

    def write_xml_to_file(self, root, fname):
        """ wrap root in an ElementTree instance, and save as XML. """
        tree = ElementTree(root)
        tree.write(fname)

    def raw_xml_format(self, e):
        """ Returns a raw-formatted XML for Element e. """
        return tostring(e, 'utf-8')

    def pretty_xml_format(self, e):
        """ Returns a pretty-formated XML for Element e.  """
        rough_string = tostring(e, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")

    def create_xml_rule(self, parent, rid):
        """ Creates an XML Element 'rule' for given parent and rule id"""
        rule = SubElement(parent, 'rule')
        rule.set('id', rid)
        return rule

    def create_xml_packet(self, parent, pid, sa, da, sp, dp, pr, ac, ma):
        """ Creates an XML Element 'packet' for given args. """
        packet = SubElement(parent, 'packet')
        packet.set('id', pid)
        SubElement(packet, 'src_addr').text = sa
        SubElement(packet, 'dst_addr').text = da
        SubElement(packet, 'src_port').text = sp
        SubElement(packet, 'dst_port').text = dp
        SubElement(packet, 'protocol').text = pr

        if ac == 1:
            act = 'PASS'
        elif ac == 2:
            act = 'DROP'
        else:
            act = str(ac)
        SubElement(packet, 'action').text = act

        SubElement(packet, 'match').text = ma

    def generate_xml_packets_for_rule(self, parent, rule, n, rule_affinity):
        """ Generates n positive or negative Packets (via rule_affinity)
            for rule 'rule' and Node 'parent'. """
        for i in xrange(1, n+1):
            if rule_affinity is True:
                packet_aff = 'p'  # positive Packet
                p = rule.sample_packet()
            else:
                packet_aff = 'n'  # negative Packet
                p = rule.sample_neg_packet()

            self.create_xml_packet(parent, packet_aff + str(i), str(p.sa),
                                   str(p.da), str(p.sp), str(p.dp), str(p.pr),
                                   p.ac, str(rule_affinity))


# ------------------------ MAIN ---------------------------------------------

def main():

    T = Tools()

    # Getting input parameters
    try:
        fname, pos, neg = T.check_args(argv)
    except TBGenError as e:
        T.print_error_and_exit(e.m, errno.EINVAL)

    with open(fname) as f:
        lines = f.readlines()

    try:
        P = Parser(lines)
        lines = P.parse()
    except TBGenError as e:
        T.print_error_and_exit(e.m, errno.EINVAL)

    # Normalize rules : negate all rule-fields with the negation mark.
    norm_rules = [l.normalize() for l in lines]

    _xml = XML()
    # Create a root Element
    root = Element('tests')

    for i in xrange(len(norm_rules)):
        # ------- Generate Tests for ONLY one rule in initial rule-set ----

        result_rules = T.make_independent(i, norm_rules)

        if result_rules != []:
            # At this point we got a result-set of independent rules and
            # ready for XML-Output

            # choose a random rule from a result-set
            q = randint(0, len(result_rules)-1)
            rule = result_rules[q]

            # Create a rule Element
            r = _xml.create_xml_rule(root, str(rule.rule_id))
            # Generate pos number of positive packets for a rule
            _xml.generate_xml_packets_for_rule(r, rule, pos, True)
            # Generate neg number of negative packets for a rule
            _xml.generate_xml_packets_for_rule(r, rule, neg, False)

    print _xml.pretty_xml_format(root)

def test_counter():
    I = Interval
    r1 = Rule(I(3, 5), I(3, 5), I(3, 5), I(3, 5), I(3, 5), DROP, 1)
    r2 = Rule(I(1, 9), I(1, 9), I(1, 9), I(1, 9), I(1, 9), DROP, 1)
    for i in range(10):
        r1-r2                         
    assert counter == 10 

def main_debug():
    """ used for perfomance analysis """
    T = Tools()

    try:
        fname, pos, neg = T.check_args(argv)
    except TBGenError as e:
        T.print_error_and_exit(e.m, errno.EINVAL)

    with open(fname) as f:
        lines = f.readlines()

    try:
        P = Parser(lines)
        lines = P.parse()
    except TBGenError as e:
        T.print_error_and_exit(e.m, errno.EINVAL)

    norm_rules = [l.normalize() for l in lines]

#     print "\nNum of lines in original ruleset: ", len(lines)
#     print "\nNum of lines in normalized ruleset: ", len(norm_rules)
# 
#     print "\nID, Num of independ. rules for this ID: \n"
# 
#     new_rules = 0
    for i in xrange(len(norm_rules)):
        # ------- Generate Tests for ONLY one rule in initial rule-set ----

        result_rules = T.make_independent(i, norm_rules)
    print counter
        # print ID of parent rule and corresponding 'independent' rules
#         num_rules = len(result_rules)
#         new_rules += num_rules
#         print i, num_rules
#     print "\nNum of new rules: ", new_rules 
#     print "Num of rule difs: ", counter



if __name__ == '__main__': 
    main()
