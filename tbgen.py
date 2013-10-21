from sys import argv
from pdb import set_trace


class RawRule(object):

    def __init__(self, rule, action = True):
    #def __init__(self, src_net, src_net_negated, dst_net, dst_net_negated, ...):
        """ Saves input information in instance variables.
        """
        assert 0, "not implemented yet"
        ###self.raw_rule = rule
        ###fields = rule.split()
        ###self.source_host = fields[0][1:]
        ###self.dest_host = fields[1]
        ###self.source_port = fields[2] + fields[3] + fields[4]
        ###self.dest_port = fields[5] + fields[6] + fields[7]
        ###self.protocol = fields[8]
        ###self.action = action

    def __str__(self):
        return self.raw_rule

    def __repr__(self):
        return self.raw_rule

    def normalize(self):
        """ Returns a list of Rule objects, which do not contain any negations.
        """
        assert 0, "not implemented yet"


class Rule(object):

    def __init__(self, rawrule):
        self.source_host = Subnet(rawrule.source_host)
        self.dest_host = Subnet(rawrule.dest_host)
        self.source_port = PortRange(rawrule.source_port)
        self.dest_port = PortRange(rawrule.dest_port)
        self.protocol = Protocol(rawrule.protocol)
        self.action = rawrule.action


class Parser(object):
    """ Parses the given input file and creates a list of RawRules.
    """
    def __init__(self, input_file):
        assert 0, "not implemented yet"

    def parse(self):
        """ Reads the contents of the given input file,
            and returns a list of RawRules.
        """
        assert 0, "not implemented yet"

def read_file(filename):
    with open(filename) as f:
        lines = f.readlines()
    return lines

# ------------------------ MAIN ---------------------------------------------
def main():
    if len(argv)>=2:
        filename = argv[1]
    else:
        exit('Usage: %s <Firewall-Rule-Set-File>' % argv[0])


__name__ == '__main__' and main()
