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
            parts = line.split()
            args = self.get_fields(line) + self.check_negs(parts) + list(str(rule_id))
            rule = RawRule(*args)
            rules.append(rule)
        return rules

    def check_negs(self, parts):
        res = []
        for i in (0, 1, 2, 5, 8):   # Index-Set of negatable fields
            if parts[i][0] == '!':
                res.append(True)
            else:
                res.append(False)
        return res

    def get_fields(self, rule_line):
        fields = rule_line.split()
        src_host = fields[0].split('/')
        dst_host = fields[1].split('/')
        src_port = [fields[2], fields[4]]
        dst_port = [fields[5], fields[7]]
        protocol = fields[8].split('/')
        action = fields[9]
        return [src_host, dst_host, src_port, dst_port, protocol, action]
               
    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines


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

    def protocol_to_interval(self):
        protocol =  map(lambda x: int(x, 0), self.protocol)
        if protocol[1] == 0:
            return Interval(0, 255)
        return Interval(protocol[0], protocol[0])

    def port_to_interval(self, field):
        a, b = field
        return Interval(a, b)

    def subnet_to_interval(self, field):
        """ Transforms a subnet of the form 'a.b.c.d/mask_bits'
            to an Interval object.
        """
        subnet, mask = field
        mask_bits = int(mask)
        _subnet = subnet
        if subnet[0] == '!':
            _subnet = subnet[1:]
        a, b, c, d = map(int, _subnet.split('.'))
        base_addr = (a << 24) | (b << 16) | (c << 8) | d
        zero_bits = 32 - mask_bits
        # zero out rightmost bits according to mask
        base_addr = (base_addr >> zero_bits) << zero_bits
        high_addr = base_addr + (2 ** zero_bits) - 1
        return Interval(base_addr, high_addr)

    def normalize(self):
        """ Returns a list of normalized Rule objects.
        """
        r = Rule(self.subnet_to_interval(self.src_host),\
                    self.subnet_to_interval(self.dst_host),\
                    self.port_to_interval(self.src_port),\
                    self.port_to_interval(self.dst_port),\
                    self.protocol_to_interval(),\
                    self.action, self.rule_id)

    def __str__(self):
        return "RawRule:  %s  %s  %s  %s  %s  (%i %i %i %i %i)  %s  %s"\
                % (self.src_host, self.dst_host, self.src_port, self.dst_port,\
                   self.protocol, self.src_host_neg, self.dst_host_neg,\
                   self.src_port_neg, self.dst_port_neg, self.prot_neg,\
                   self.action, self.rule_id)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
#         if not isinstance(other, RawRule):
#             return False
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

#     def __ne__(self, other):
#         return not self == other

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
        return "Rule:  %s %s %s %s %s %s %s" % (self.src_net, self.dst_net,\
               self.src_ports, self.dst_ports, self.prots, self.action, self.rule_id)

    def __repr__(self):
        return str(self)

# ------------------------ MAIN ---------------------------------------------

def main():
#     if len(argv)>=2:;U
#         filename = argv[1]
#     else:
#         exit('Usage: %s <Firewall-Rule-Set-File>' % argv[0])
    filename = 'test_rules.txt'
    p = Parser(filename)
    r =  p.parse()[0]
    print r.dst_port
    i1 =  r.port_to_interval(r.dst_port) 
    i2 = Interval(1221, 1221)
    
    print i1.a, i2.a
    print isinstance(i1, Interval)
__name__ == '__main__' and main()


