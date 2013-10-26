from sys import argv
from pdb import set_trace


class Parser(object):
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        file_lines = self.read_file()
        splitted_rules = []
        for line in file_lines:
            splitted_rules.append(self.get_fields(line))

        return splitted_rules

    def get_fields(self, rule_line):
        fields = rule_line.split()
        self.src_host = fields[0][1:]
        self.dst_host = fields[1]
        self.src_port = fields[2] + fields[3] + fields[4]
        self.dst_port = fields[5] + fields[6] + fields[7]
        self.protocol = fields[8]
#         self.action = action
        return self.src_host, self.dst_host, self.src_port,\
               self.dst_port, self.protocol

    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines

    def is_negated(self, field):
        if field[0] == '!':
            return True
        return False

    def neg_state(self, rule_fields):
        state = [False, False, False, False, False]
        for i, field in enumerate(rule_fields):
            if self.is_negated(field):
                state[i] = True
        return state

# ------------------------ MAIN ---------------------------------------------
def main():
#     if len(argv)>=2:
#         filename = argv[1]
#     else:
#         exit('Usage: %s <Firewall-Rule-Set-File>' % argv[0])
    filename = 'rules'
    a = Parser(filename)
    raw_rules = a.parse()
    print raw_rules[0]

    print a.neg_state(raw_rules[0])

__name__ == '__main__' and main()



