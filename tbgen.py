
from sys import argv
from pdb import set_trace

from interval import (Interval, IntervalList)

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

# -------------- CONSTANTS --------------------------------------
PASS = 1
DROP = 2


MIN_ADDR = 0
MAX_ADDR = int(2 ** 32 - 1)

MIN_PORT = 0
MAX_PORT = int(2 ** 16 - 1)

MIN_PROT = 0
MAX_PROT = int(2 ** 8 - 1)
# --------------------------------------------------------------


# TODO
# - implement normalize
# - finish parser
# - implement Rule subtraction
# - ONLY the parser does parsing!
# - RawRule objecst shall be instantiated ONLY with Interval objects,
#   NOT with plain strings


class Parser(object):

    def __init__(self, filename, ):
        self.filename = filename

    def parse(self):
        file_lines = self.read_file()
        rules = []
        for rule_id, line in enumerate(file_lines):
            parts = line.split()
            no_negs_list, negs = self.check_negs(parts)

            args = self.get_fields(parts) + negs + list(str(rule_id))
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

    def get_fields(self, fields):
        def split_subnet_str(field):
            a = field.split('/')
            return map(int, a[0].split('.')) + [int(a[1])]

        src_host = split_subnet_str(fields[0])
        dst_host = split_subnet_str(fields[1])
        src_port = [int(fields[2]), int(fields[4])]
        dst_port = [int(fields[5]), int(fields[7])]
        protocol = [int(x, 0) for x in fields[8].split('/')]

        _action = fields[9]
        if _action == 'DROP':
            action = DROP
        elif _action == 'PASS':
            action = PASS
        else:
            raise ValueError("%s is an unknown rule action!" % _action)
        return [src_host, dst_host, src_port, dst_port, protocol, action]
               
    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines


class RawRule(object):

    def __init__(self, src_host, dst_host, src_port, dst_port, protocol,\
                action, src_host_neg, dst_host_neg, src_port_neg,\
                dst_port_neg, prot_neg, rule_id):
#         r = Rule(self.subnet_to_interval(self.src_host),\
#                     self.subnet_to_interval(self.dst_host),\
#                     self.port_to_interval(self.src_port),\
#                     self.port_to_interval(self.dst_port),\
#                     self.protocol_to_interval(),\
#                     self.action, self.rule_id)
#
        self.src_host = src_host
        self.dst_host = dst_host
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = self.protocol_to_interval(protocol)
        self.action = action
        self.src_host_neg = src_host_neg
        self.dst_host_neg = dst_host_neg
        self.src_port_neg = src_port_neg
        self.dst_port_neg = dst_port_neg
        self.prot_neg     = prot_neg
        self.rule_id = rule_id

    def protocol_to_interval(self, protocol):
#         protocol =  map(lambda x: int(x, 0), self.protocol)
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
# 
#     def normalize(self):
#         """ Returns a list of normalized Rule objects.
#         """
#         r = Rule(self.subnet_to_interval(self.src_host),\
#                     self.subnet_to_interval(self.dst_host),\
#                     self.port_to_interval(self.src_port),\
#                     self.port_to_interval(self.dst_port),\
#                     self.protocol_to_interval(),\
#                     self.action, self.rule_id)
#         rules = []
#         src_nets = self.src_host.negate(MIN_ADDR, MAX_ADDR)
#         dst_nets = self.dst_host.negate(MIN_ADDR, MAX_ADDR)
#         src_ports = self.src_port.negate(MIN_PORT, MAX_PORT)
#         dst_ports = self.dst_port.negate(MIN_PORT, MAX_PORT)
#         prots = self.protocol.negate(MIN_PROT, MAX_PROT)
#         for src_net in src_nets:
#             for dst_net in dst_nets:
#                 for src_port in src_ports:
#                     for dst_port in dst_ports:
#                         for prot in prots:
#                             rule = Rule(src_net, dst_net, src_port, dst_port,
#                                     prot, self.action, self.rule_id)
#                             rules.append(rule)
#         return rules

    def __str__(self):
        s1 = "RawRule: sn%s dn%s sp%s dp%s prot%s"\
        % (self.src_host, self.dst_host, self.src_port, self.dst_port,\
                   self.protocol) 
        s2 = "id(%s) action(%s) neg(%i %i %i %i %i)"\
               % (self.rule_id, self.action, self.src_host_neg,\
                   self.dst_host_neg, self.src_port_neg, self.dst_port_neg,\
                   self.prot_neg)
        return s1 + s2

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
    p1, p2 = p.parse()

    r1 = RawRule([192, 151, 11, 17, 32], [15, 0, 120, 4, 32],\
                     [10, 655], [1221, 1221], [6, 255],\
                      DROP, 1, 0, 1, 0, 0, 0)

#     r2 == p.parse()[0]

    assert  r1.dst_host == p1.dst_host

__name__ == '__main__' and main()


