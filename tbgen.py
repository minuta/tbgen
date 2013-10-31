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

class Parser(object):

    def __init__(self, filename, ):
        self.filename = filename

    def parse(self):
        file_lines = self.read_file()
        rules = []
        for rule_id, line in enumerate(file_lines):
            parts = line[1:].split()
            args = self.get_fields(line) + self.check_negs(parts) + list(str(rule_id))
            rule = RawRule(*args)
            rules.append(rule)
        return rules

    def check_negs(self, parts):
#         set_trace()
        f = (0, 1, 2, 5, 8)   # Index-Set of negatable fields
        res = []
        for i in f:
            if parts[i][0] == '!':
                res.append(True)
            else:
                res.append(False)
        return res

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


class RawRule(object):

    def __init__(self, src_host, dst_host, src_port, dst_port, protocol,\
                 src_host_neg, dst_host_neg, src_port_neg, dst_port_neg,\
                 prot_neg, rule_id):
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
        a, b = field
        return Interval(a, b)

    def subnet_to_interval(self, field):
        subnet, mask = field
        x = IP_CALC(subnet + '/' + mask)
        a, b = x.get_subnet_minmax()
        return Interval(a, b)

    def normalize(self):
        """ Returns a list of normalized Rule objects.
        """

    def __str__(self):
        return "RawRule(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"\
                % (self.src_host, self.dst_host, self.src_port, self.dst_port,\
                   self.protocol, self.src_host_neg, self.dst_host_neg,\
                   self.src_port_neg, self.dst_port_neg, self.prot_neg,\
                   self.rule_id)

    def __repr__(self):
        return str(self)


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
#     if len(argv)>=2:;U
#         filename = argv[1]
#     else:
#         exit('Usage: %s <Firewall-Rule-Set-File>' % argv[0])
    filename = 'test_rules.txt'
    a = Parser(filename)
    raw_rules = a.parse()
    print "-"*70
    for x in raw_rules:
        print x
#         q = RawRule(x[0], x[1], x[2], x[3], x[4], x[5], x[6])
#         print q.create()
# 
#     print "-"*70
#     x = raw_rules[0]
#     q = RawRule(x[0], x[1], x[2], x[3], x[4], x[5], x[6])
#     print q.create() 
#     n = NORMALIZER(q.create())
# 
#     print "Norm : ", n.run_for_one(2)
# 
__name__ == '__main__' and main()


