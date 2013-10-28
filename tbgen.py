from sys import argv
from pdb import set_trace
import sys 
sys.path.append('/home/qp/Dropbox/Projects/Interval') 

from interval import (Interval, IntervalList)

class PARSER(object):
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        file_lines = self.read_file()
        splitted_rules = []
        for id, line in enumerate(file_lines):
            l = self.get_fields(line)
            negs = self.neg_state(l)
            l = self.remove_negators(l)
            l.extend([negs, id + 1])
            splitted_rules.append(l)
        return splitted_rules

    def get_fields(self, rule_line):
        fields = rule_line.split()
        src_host = fields[0][1:].split('/')
        dst_host = fields[1].split('/')
        src_port = [fields[2], fields[4]]
        dst_port = [fields[5], fields[7]]
        protocol = fields[8]
#         self.action = action
        return [src_host, dst_host, src_port, dst_port, protocol]
               
    def read_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines

    def is_negated(self, field):
        if len(field)!=1:
            test_obj = field[0][0]
        else :
            test_obj = field[0]
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


class ABSTRACT_RULE(object):
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
    a = PARSER(filename)
    raw_rules = a.parse()
    print "-"*70
    for i in raw_rules:
        print i

__name__ == '__main__' and main()


# --------------------- TESTS ----------------------------------------------
import pytest
skip = pytest.mark.skipif
@skip
def test_remove_negators():
    x = PARSER('rules') 
    raw_rules = x.parse()
    assert x.remove_negators(raw_rules[0]) == ['1']

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

