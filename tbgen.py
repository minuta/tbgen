from sys import argv
from pdb import set_trace

from interval import (Interval, IntervalList)

class Action(object):
    
    def __init__(self, action_id):
        self.action_id = action_id

    def __eq__(self, other):
        return self.action_id == other.action_id

    def __ne__(self, other):
        return not self == other

PASS = Action(1)
DROP = Action(2)


# TODO
# - implement normalize
# - finish parser
# - implement Rule subtraction

class PARSER(object):

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        file_lines = self.read_file()
        splitted_rules = []
        for rule_id, line in enumerate(file_lines):
            # XXX 
            # first check negations, then inspect semantic parts of the line

            # parts = line.split()
            # negations = self.check_negations(parts)
            # field_info = self.get_fields(parts)
            # rule = RawRule(negations, field_info)


            l = self.get_fields(line)
            negs = self.neg_state(l)
            l = self.remove_negators(l)
            l.extend([negs, rule_id + 1])
            splitted_rules.append(l)
        return splitted_rules

    def get_fields(self, rule_line):
        fields = rule_line.split()
        src_host = fields[0][1:].split('/')
        dst_host = fields[1].split('/')
        src_port = [fields[2], fields[4]]
        dst_port = [fields[5], fields[7]]
        protocol = fields[8].split('/')
#         TODO: rule_action
        return [src_host, dst_host, src_port, dst_port, protocol]
               
    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines

    def is_negated(self, field):
        test_obj = field[0]
        if len(field)!=1:
            test_obj = field[0][0]
        if test_obj == '!':
            return True
        return False

    def neg_state(self, rule_fields):
        return [i for i, field in enumerate(rule_fields) \
                if self.is_negated(field)]

    def remove_negators(self, fields):
        neg_status = self.neg_state(fields)
        for i in neg_status:
            fields[i][0]=fields[i][0][1:]
        return fields

def subnet_to_interval(a, b, c, d, mask_bits):
    """ Transforms a subnet of the form 'a.b.c.d/mask_bits'
        to an Interval object.
    """
    base_addr = (a << 24) | (b << 16) | (c << 8) | d
    zero_bits = 32 - mask_bits
    # zero out rightmost bits according to mask
    base_addr = (base_addr >> zero_bits) << zero_bits
    high_addr = base_addr + (2 ** zero_bits) - 1
    return Interval(base_addr, high_addr)

class IP_CALC(object):

    def __init__(self, subnet):
        parts = subnet.split('/')
        self.ip = parts[0]
        self.mask = int(parts[1]) 
        self.net_part = self.ip_to_num(self.ip) & self.long_mask()

    def ip_to_num(self, ip):
        b = ''.join([bin(int(x)+256)[3:] for x in ip.split('.')])
        return int(b, 2)

    def long_mask(self):
        return (1 << 32) - (1 << 32 >> self.mask)

    def get_subnet_minmax(self):
        if self.is_wildcard():
            return 0, 2**32 - 1
        if self.is_one_host_subnet():
            return self.ip_to_num(self.ip), self.ip_to_num(self.ip)
        host_bits = 32 - self.mask
        max_host = 1 << host_bits
        return self.net_part + 1, self.net_part + max_host - 1

    def is_one_host_subnet(self):
        return self.mask == 32

    def is_wildcard(self):
        return self.mask == 0

    def num_to_bin(self, x):
        return bin(x)[2:]

    def num_to_ip(self, num):
        return ".".join(map(lambda n: str(num>>n & 0xFF), [24,16,8,0]))


class AbstractRule(object):

    def __init__(self, src_host, dst_host, src_port, dst_port,
                       protocol, src_host_neg, dst_host_neg, src_port_neg,
                       dst_port_neg, prot_neg, rule_id):
        self.src_host = src_host
        self.dst_host = dst_host
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.src_host_neg = src_host_neg
        self.dst_host_neg = dst_host_neg
        self.src_port_neg = src_port_neg
        self.dst_port_neg = dst_port_neg
        self.prot_neg     = prot_neg
        self.rule_id = rule_id

    def create(self):
        return [self.subnet_to_interval(self.src_host),\
                self.subnet_to_interval(self.dst_host),\
                self.port_to_interval(self.src_port),\
                self.port_to_interval(self.dst_port),\
                self.protocol_to_interval(),\
                self.neg_stat,\
                self.rule_id]

    def protocol_to_interval(self):
        protocol =  map(lambda x: int(x, 0), self.protocol)
        if protocol[1] == 0:
            return Interval(0, 255)
        return Interval(protocol[0], protocol[0])

    def port_to_interval(self, field):
        low_port,  high_port = field
        return Interval(low_port, high_port)

    def subnet_to_interval(self, field):
        subnet, mask = field
        x = IP_CALC(subnet + '/' + mask)
        a, b = x.get_subnet_minmax()
        return Interval(a, b)

    def normalize(self):
        """ Returns a list of normalized Rule objects.
        """

        


class Rule(object):
    """ Represents a normalized firewall rule, i.e. there are no more negated
        fields.
    """
    
    def __init__(self, src_net, dst_net, src_ports, dst_ports, prots, rule_id,
            action):
        self.src_net = src_net
        self.dst_net = dst_net
        self.src_ports = src_ports
        self.dst_ports = dst_ports
        self.prots = prots
        self.rule_id = rule_id
        self.action = action

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

class NORMALIZER(object):
    # Normalizes AbstractRule
    def __init__(self, abstract_rule):
        self.src_host, self.dst_host, self.src_port, self.dst_port,\
        self.protocol, self.neg_stat, self.rule_id,\
        = abstract_rule
        self.rule = abstract_rule

    def run_for_all(self):
        if self.neg_stat == []:
            return self.rule
        return self.run_for_one(2) 

    def run_for_one(self, neg_index):
        set_trace()
        max_n = self.get_max_border(neg_index)
        _interval = self.rule[neg_index]
        negated_intervals = _interval.negate(0, max_n)

        new_rules = []
        for i in negated_intervals:
            r = self.rule[:]
            r[neg_index]=i
            new_rules.append(r)
        return new_rules

    def get_max_border(self, i):
        if i in [0, 1]:
            return 2**32 - 1
        if i in [2, 3]:
            return 2**16 - 1
        if i == 4:
            return 255
# ------------------------ MAIN ---------------------------------------------

def main():
#     if len(argv)>=2:
#         filename = argv[1]
#     else:
#         exit('Usage: %s <Firewall-Rule-Set-File>' % argv[0])
    filename = 'rules'
    a = PARSER(filename)
    raw_rules = a.parse()
    print "-"*70
    for x in raw_rules:
        print x
        q = AbstractRule(x[0], x[1], x[2], x[3], x[4], x[5], x[6])
        print q.create()

    print "-"*70
    x = raw_rules[0]
    q = AbstractRule(x[0], x[1], x[2], x[3], x[4], x[5], x[6])
    print q.create() 
    n = NORMALIZER(q.create())

    print "Norm : ", n.run_for_one(2)

__name__ == '__main__' and main()


# --------------------- TESTS ----------------------------------------------
import pytest
skip = pytest.mark.skipif

# NORMALIZER Tests ----------------------
# IPCALC Tests --------------------------
def test_ipcalc_init():
    s = IP_CALC('1.1.1.1/24')
    assert s.ip == '1.1.1.1' and s.mask == 24

def test_num_to_ip():
    s = IP_CALC('1.1.1.1/24')
    assert s.num_to_ip(16843009) == '1.1.1.1'
    assert s.num_to_ip(4294967040L) == '255.255.255.0'

def test_ip_to_num():
    s = IP_CALC('1.1.1.1/24')
    assert s.ip_to_num('1.1.1.1') == 16843009
    assert s.ip_to_num('0.0.0.0') == 0                   # test min-subnet
    assert s.ip_to_num('255.255.255.255') == 2**32 - 1   # test max-subnet

def test_mask():
    s = IP_CALC('1.1.1.1/24')
    assert s.long_mask() == 4294967040L

def test_num_to_bin():
    s = IP_CALC('1.1.1.1/24')
    assert s.num_to_bin(16843009) == '1000000010000000100000001'
    assert s.num_to_bin(4294967040L) =='11111111111111111111111100000000'

def test_get_subnet_minmax():
    s = IP_CALC('1.1.1.1/24')
    a, b = s.get_subnet_minmax()
    assert s.num_to_ip(a) == '1.1.1.1' and s.num_to_ip(b) == '1.1.1.255'

    s = IP_CALC('11.12.13.14/7')
    a, b = s.get_subnet_minmax()
    assert s.num_to_ip(a) == '10.0.0.1' and s.num_to_ip(b) == '11.255.255.255'

    s = IP_CALC('0.0.0.0/0')        # test Wildcard
    a, b = s.get_subnet_minmax()
    assert a == 0 and b == 2**32 - 1 


def test_subnet_to_interval():
    # check subnet '1.2.3.4/5'
    assert subnet_to_interval(1, 2, 3, 4, 5) == Interval(0, 134217727)
    # check subnet '5.6.7.8/0'
    assert subnet_to_interval(5, 6, 7, 8, 0) == Interval(0, 2 ** 32 - 1)
    assert subnet_to_interval(24, 102, 18, 97, 17) == Interval(409337856,
            409370621)


class TestAbstractRule(object):

    def test_normalize(self):
        r1 = AbstractRule(Interval(1, 2), Interval(3, 4),
                          Interval(5, 6), Interval(7, 8),
                          Interval(9, 9), False, True, False,
                          True, False, 1000)
        rules = r1.normalize()
        assert len(rules) == 4
        assert rules[0] == ...
        assert rules[1] == ...
        ...
        

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
