#
# This Script transforms a ruleset with rules like
#        @204.152.184.32/27 0.0.0.0/0 0 : 65535 0 : 65535 0x06/0xff
# into :
#        204.152.184.32/27 0.0.0.0/0 0 : 65535 0 : 65535 0x06/0xff DROP/PASS
# 
# more precisely :
#     1)   '@'-Character will be removed at the begin of line 
#     2)   'DROP' or 'PASS' will be added to the end of line
# 

import pytest, random
from sys import argv

skip = pytest.mark.skipif



def convert(lines):
    removed_first_ch = [line[1:].rstrip() for line in lines]
#     import pdb; pdb.set_trace()
    return [line + ' ' + random_action() for line in removed_first_ch]

def random_action():
    """ Returns at random either 'PASS' or 'DROP' """
    return random.choice(['PASS', 'DROP'])



def main():
    if len(argv) == 2:
        fname = argv[1]
    else:
        raise SyntaxError

    with open(fname) as f:
        before_lines = f.readlines()

    after_lines = convert(before_lines)

#     import pdb; pdb.set_trace()
    for line in after_lines:
        print line


if __name__ == '__main__': main()

# ---------------- TESTS -------------------------------------------------

def test_random():
    random1 = random_action()
    random2 = random_action()
    assert (random1 == 'PASS' or random1 == 'DROP')
    assert (random2 == 'PASS' or random2 == 'DROP')

def test_convert():
    r1 = "@204.152.184.32/27 0.0.0.0/0 0 : 65535 10 : 65535 0x06/0xff"
    r2 = "@204.152.184.32/27 0.0.0.0/0 0 : 65535 0 : 65535 0x06/0xff"
    before = [r1, r2]

    v1a = "204.152.184.32/27 0.0.0.0/0 0 : 65535 10 : 65535 0x06/0xff DROP"
    v1b = "204.152.184.32/27 0.0.0.0/0 0 : 65535 10 : 65535 0x06/0xff PASS"
    v2a = "204.152.184.32/27 0.0.0.0/0 0 : 65535 0 : 65535 0x06/0xff DROP"
    v2b = "204.152.184.32/27 0.0.0.0/0 0 : 65535 0 : 65535 0x06/0xff PASS"

    after1 = [v1a , v2a]
    after2 = [v1a , v2b]
    after3 = [v1b , v2a]
    after4 = [v1b , v2b]

    after = convert(before) 
    assert after == after1 or after == after2 or after == after3 or after == after4


