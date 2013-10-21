from sys import argv
from pdb import set_trace


class Parser(object):
    """ Parses the given input file and creates a list of RawRules.
    """
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        """ Reads the contents of the given input file,
            and returns a list of RawRules.
        """

        file_lines = self.read_file()
        line = file_lines[0]
        self.get_fields(line)


    def get_fields(self, rule_line):
        return 0
        ###fields = rule.split()
        ###self.source_host = fields[0][1:]
        ###self.dest_host = fields[1]
        ###self.source_port = fields[2] + fields[3] + fields[4]
        ###self.dest_port = fields[5] + fields[6] + fields[7]
        ###self.protocol = fields[8]
        ###self.action = action


    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines


# class RawRule(object):
#     def __init__(self, src_net, src_net_negated, dst_net, dst_net_negated, ...):
#         """ Saves input information in instance variables.
#         """
#         assert 0, "not implemented yet"
# 
#     def __str__(self):
#         return self.raw_rule
# 
#     def __repr__(self):
#         return self.raw_rule
# 
#     def normalize(self):
#         """ Returns a list of Rule objects, which do not contain any negations.
#         """
#         assert 0, "not implemented yet"
# 


# ------------------------ MAIN ---------------------------------------------
def main():
#     if len(argv)>=2:
#         filename = argv[1]
#     else:
#         exit('Usage: %s <Firewall-Rule-Set-File>' % argv[0])
    filename = 'rules'
    a = Parser(filename)

__name__ == '__main__' and main()


