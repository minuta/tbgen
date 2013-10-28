from sys import argv
from pdb import set_trace
import sys 
sys.path.append('/home/qp/Dropbox/Projects/Interval') 

from interval import (Interval, IntervalList)

class Parser(object):
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        file_lines = self.read_file()
        splitted_rules = []
        for id, line in enumerate(file_lines):
            l = self.get_fields(line)
            l.extend([self.neg_state(l), id + 1])
            splitted_rules.append(l)

        return splitted_rules

    def get_fields(self, rule_line):
        fields = rule_line.split()
        self.src_host = fields[0][1:]
        self.dst_host = fields[1]
        self.src_port = fields[2] + fields[3] + fields[4]
        self.dst_port = fields[5] + fields[6] + fields[7]
        self.protocol = fields[8]
#         self.action = action

        return [self.src_host, self.dst_host, self.src_port,\
               self.dst_port, self.protocol]
               
    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines

    def is_negated(self, field):
        if field[0] == '!':
            return True
        return False

    def neg_state(self, rule_fields):
        state = [0, 0, 0, 0, 0]
        for i, field in enumerate(rule_fields):
            if self.is_negated(field):
                state[i] = 1
        return state


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

    def get_subnet_minhost(self):
        return self.net_part + 1

    def get_subnet_maxhost(self):
        host_bits = 32 - self.mask
        max_host = 1 << host_bits
        return self.net_part + max_host - 1

    def num_to_bin(self, x):
        return bin(x)[2:]

    def num_to_ip(self, num):
        return ".".join(map(lambda n: str(num>>n & 0xFF), [24,16,8,0]))


class Abstract_Rule(object):
    def port_to_interval(self, field):
        low_port, high_port = field.split(':')
        return Interval(low_port, high_port)


    def subnet_to_interval(self, field):
        pass

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

    r = Abstract_Rule()
    ip = '1.1.1.1/24'

    
    s = IP_CALC('1.1.1.1/24')
    print s.num_to_ip(16843009)
    print s.num_to_ip(4294967040L)

#     a = s.get_subnet_minhost()
#     b = s.get_subnet_maxhost()
# 
#     print a, b
#     for i in range(a, b+1):
#         print s.num_to_bin(i)
# 
#     m = r.get_subnet_min(ip)
#     print r.int_to_bin(m)
# 
#     ip = '192.168.1.1'
#     print ''.join([bin(int(x)+256)[3:] for x in ip.split('.')])

__name__ == '__main__' and main()


# --------------------- TESTS ----------------------------------------------
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

def test_mask():
    s = IP_CALC('1.1.1.1/24')
    assert s.long_mask() == 4294967040L

def test_num_to_bin():
    s = IP_CALC('1.1.1.1/24')
    assert s.num_to_bin(16843009) == '1000000010000000100000001'
    assert s.num_to_bin(4294967040L) =='11111111111111111111111100000000'

def test_get_subnet_minhost():
    s = IP_CALC('1.1.1.1/24')
    assert s.num_to_ip(s.get_subnet_minhost()) == '1.1.1.1'

    s = IP_CALC('11.12.13.14/7')
    assert s.num_to_ip(s.get_subnet_minhost()) == '10.0.0.1'

def test_get_subnet_maxhost():
    s = IP_CALC('1.1.1.1/24')
    assert s.num_to_ip(s.get_subnet_maxhost()) == '1.1.1.255'

    s = IP_CALC('11.12.13.14/7')
    assert s.num_to_ip(s.get_subnet_maxhost()) == '11.255.255.255'

