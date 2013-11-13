from sys import argv
from pdb import set_trace
import os, pytest

skip = pytest.mark.skipif

# ------------------- TODO ------------------------------------------
# + NO magic numbers!
# + do error checking in parser and test it
# + fix ALL broken tests
# - implement method on class Rule __sub__ (plenty of tests!)
# - Implement function/method to make rules independent!
#   This function/method should use subtraction of Rule objects!
# - implement Rule subtraction


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

ERROR_STR41 = '<Num of positive Tests> <Num of negative Tests>' 
ERROR_STR4 = 'Usage: python %s <Firewall-Rule-Set-File>' % argv[0] + ERROR_STR41

ERROR_STR5 = 'Error : File doesn\'t exist or is empty!\n'
ERROR_STR6 = 'Error : Invalid Rule Structure in Rule : '


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
    """ Represents  a normalized firewall rule, i.e. there are no more negated
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
        self.x1 = src_net.a
        self.x2 = src_net.b
        self.y1 = dst_net.a
        self.y2 = dst_net.b
        self.z1 = src_ports.a
        self.z2 = src_ports.b
        self.v1 = dst_ports.a
        self.v2 = dst_ports.b
        self.w1 = prots.a
        self.w2 = prots.b

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

    def __sub__(self, other):
        X1 = self.x1
        X2 = self.x2
        Y1 = self.y1
        Y2 = self.y2
        Z1 = self.z1
        Z2 = self.z2
        V1 = self.v1
        V2 = self.v2
        W1 = self.w1
        W2 = self.w2

        x1 = other.x1
        x2 = other.x2
        y1 = other.y1
        y2 = other.y2
        z1 = other.z1
        z2 = other.z2
        v1 = other.v1
        v2 = other.v2
        w1 = other.w1
        w2 = other.w2

        # Left Block
        b1 = Interval(X1, x1), Interval(Y1, Y2), Interval(Z1, Z2),\
             Interval(V1, V2), Interval(W1, W2)
        # Right Block
        b2 = Interval(x2, X2), Interval(Y1, Y2), Interval(Z1, Z2),\
             Interval(V1, V2), Interval(W1, W2)
        # Top Block
        b3 = Interval(x1, x2), Interval(y2, Y2), Interval(Z1, Z2),\
             Interval(V1, V2), Interval(W1, W2)
        # Bottom Block
        b4 = Interval(x1, x2), Interval(Y1, y1), Interval(Z1, Z2),\
             Interval(V1, V2), Interval(W1, W2)
        # Back Block
        b5 = Interval(x1, x2), Interval(y1, y2), Interval(z2, Z2),\
             Interval(V1, V2), Interval(W1, W2)
        # Front Block
        b6 = Interval(x1, x2), Interval(y1, y2), Interval(Z1, z1),\
             Interval(V1, V2), Interval(W1, W2)
        # Right V-Dim
        b7 = Interval(x1, x2), Interval(y1, y2), Interval(z1, z2),\
             Interval(v2, V2), Interval(W1, W2)
        # Left V-Dim
        b8 = Interval(x1, x2), Interval(y1, y2), Interval(z1, z2),\
             Interval(V1, v1), Interval(W1, W2)
        # Right W-Dim
        b9 = Interval(x1, x2), Interval(y1, y2), Interval(z1, z2),\
             Interval(v1, v2), Interval(w2, W2)
        # Left W-Dim
        b10 = Interval(x1, x2), Interval(y1, y2), Interval(z1, z2),\
             Interval(v1, v2), Interval(W1, w1)


        return [ b1[0], b1[1], b1[2], b1[3], b1[4], \
                 b2[0], b2[1], b2[2], b2[3], b2[4], \
                 b3[0], b3[1], b3[2], b3[3], b3[4], \
                 b4[0], b4[1], b4[2], b4[3], b4[4], \
                 b5[0], b5[1], b5[2], b5[3], b5[4], \
                 b6[0], b6[1], b6[2], b6[3], b6[4], \
                 b7[0], b7[1], b7[2], b7[3], b7[4], \
                 b8[0], b8[1], b8[2], b8[3], b8[4], \
                 b9[0], b9[1], b9[2], b9[3], b9[4], \
                 b10[0], b10[1], b10[2], b10[3], b10[4] ]



# ------------------------ MAIN ---------------------------------------------
class Rule1d(object):
    """ Sub of 1-dim-Rules
    """
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return "Rule-1D( %s )" %(self.i)

    def __sub__(self, other):
        return [ Rule1d(i) for i in (self.i - other.i)]

    def __eq__(self, other):
        return self.i == other.i

class Rule2d(object):
    """ Sub of 2-dim-Rules
    """
    def __init__(self, i1, i2):
        self.i1 = i1
        self.i2 = i2

    def __sub__(self, other):
        return [ Rule2d(i, self.i2) for i in (self.i1 - other.i1) ] + \
               [ Rule2d(other.i1, x) for x in (self.i2 - other.i2) ]

    def __repr__(self):
        return "Rule-2D( %s, %s )" %(self.i1, self.i2)

    def __eq__(self, other):
        return self.i1 == other.i1 and self.i2 == other.i2


class Rule3d(object):
    """ Sub of 3-dim-Rules
    """
    def __init__(self, i1, i2, i3):
        self.i1 = i1
        self.i2 = i2
        self.i3 = i3
        self.x1 = i1.a
        self.x2 = i1.b
        self.y1 = i2.a
        self.y2 = i2.b 
        self.z1 = i3.a
        self.z2 = i3.b

    def __repr__(self):
        return "3-dim-rule( %s, %s, %s )" %(self.i1, self.i2, self.i3)

    def __sub__(self, other):
        X1 = self.x1
        X2 = self.x2
        Y1 = self.y1
        Y2 = self.y2
        Z1 = self.z1
        Z2 = self.z2

        x1 = other.x1
        x2 = other.x2
        y1 = other.y1
        y2 = other.y2
        z1 = other.z1
        z2 = other.z2

        # Left Block
        b1 = Interval(X1, x1), Interval(Y1, Y2), Interval(Z1, Z2)
        # Right Block
        b2 = Interval(x2, X2), Interval(Y1, Y2), Interval(Z1, Z2)
        # Top Block
        b3 = Interval(x1, x2), Interval(y2, Y2), Interval(Z1, Z2)
        # Bottom Block
        b4 = Interval(x1, x2), Interval(Y1, y1), Interval(Z1, Z2)
        # Back Block
        b5 = Interval(x1, x2), Interval(y1, y2), Interval(z2, Z2)
        # Front Block
        b6 = Interval(x1, x2), Interval(y1, y2), Interval(Z1, z1)

        return [ b1[0], b1[1], b1[2], \
                 b2[0], b2[1], b2[2], \
                 b3[0], b3[1], b3[2], \
                 b4[0], b4[1], b4[2], \
                 b5[0], b5[1], b5[2], \
                 b6[0], b6[1], b6[2] ]


class TestRule1d(object):
    def test_sub(self):          # no empty blocks
        r1 = Rule1d( Interval(1, 10) )
        r2 = Rule1d( Interval(4, 7) )
        assert r1 - r2 == [ Rule1d(Interval(1, 3)), Rule1d(Interval(8, 10)) ]

    def test_sub2(self):          # left block is empty
        r1 = Rule1d( Interval(1, 10) )
        r2 = Rule1d( Interval(1, 6) )
        assert r1 - r2 == [ Rule1d(Interval(7, 10)) ]


class TestRule2d(object):
    def test_sub(self):
        r1 = Rule2d( Interval(1, 9), Interval(1, 9) )
        r2 = Rule2d( Interval(4, 7), Interval(4, 7) )
        assert r1 - r2 == [ Rule2d(Interval(1, 3), Interval(1, 9)),\
                            Rule2d(Interval(8, 9), Interval(1, 9)),\
                            Rule2d(Interval(4, 7), Interval(1, 3)),\
                            Rule2d(Interval(4, 7), Interval(8, 9)) ]
  
    # Bottom-Block is empty
    def test_sub2(self):
        r1 = Rule2d( Interval(1, 9), Interval(1, 9) )
        r2 = Rule2d( Interval(3, 6), Interval(1, 6) )
        assert r1 - r2 == [ Rule2d(Interval(1, 2), Interval(1, 9)),\
                            Rule2d(Interval(7, 9), Interval(1, 9)),\
                            Rule2d(Interval(3, 6), Interval(7, 9)) ]
        
    # Top-Block and Right-Block are empty
    def test_sub3(self):
        r1 = Rule2d( Interval(1, 9), Interval(1, 9) )
        r2 = Rule2d( Interval(6, 9), Interval(6, 9) )
        assert r1 - r2 == [ Rule2d(Interval(1, 5), Interval(1, 9)),\
                            Rule2d(Interval(6, 9), Interval(1, 5)) ]
  
 
class TestRule3d(object):
    # r2 is in middle of r1 => No empty Blocks
    def test_sub(self):
        r1 = Rule3d( Interval(1, 9), Interval(1, 9), Interval(1, 9) )
        r2 = Rule3d( Interval(4, 6), Interval(4, 6), Interval(4, 6) )

        b1 = [ Interval(1, 4), Interval(1, 9), Interval(1, 9) ]
        b2 = [ Interval(6, 9), Interval(1, 9), Interval(1, 9) ]
        b3 = [ Interval(4, 6), Interval(6, 9), Interval(1, 9) ]
        b4 = [ Interval(4, 6), Interval(1, 4), Interval(1, 9) ]
        b5 = [ Interval(4, 6), Interval(4, 6), Interval(6, 9) ]
        b6 = [ Interval(4, 6), Interval(4, 6), Interval(1, 4) ]

        assert r1 - r2 == [ b1[0], b1[1], b1[2],\
                            b2[0], b2[1], b2[2],\
                            b3[0], b3[1], b3[2],\
                            b4[0], b4[1], b4[2],\
                            b5[0], b5[1], b5[2],\
                            b6[0], b6[1], b6[2] ]



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
    r1 = Rule2d( Interval(1, 9), Interval(1, 9) )
    r2 = Rule2d( Interval(6, 9), Interval(6, 9) )
    v = r1 - r2
    print v

if __name__ == '__main__': main()


