# Wrapper reads a file and checks for wrong data
from sys import argv
import os

NMIN = 0
NMAX = 1000
OK_STR = 'ok'
ERROR_STR1 = "Error : some args are not in allowed range (%i, %i)" %(NMIN, NMAX)
ERROR_STR2 = 'Error : you haven\'t specified any valid number of tests...'
ERROR_STR3 = "Error : Invalid args!\n"
ERROR_STR4 = 'Usage: python %s <Firewall-Rule-Set-File> <Num of positive Tests> <Num of negative Tests>' % argv[0]
ERROR_STR5 = 'Error : File "%s" doesn\'t exist or is empty!\n' %argv[1]

def check_args(a, b):
    r = True
    message = OK_STR
    trange = range(NMIN, NMAX)
    if a == b == 0:
        message = ERROR_STR2
        r = False
    if a not in trange or b not in trange:
        message = ERROR_STR1
        r = False
    return r, message

def print_error_and_exit(message):
    print message
    exit(0)

def read_file():
    if len(argv) == 4:
        fname = argv[1]
        pos_tests = int(argv[2])
        neg_tests = int(argv[3])

        ok, message = check_args(pos_tests, neg_tests)
        if ok != True:
            print_error_and_exit(message)
        if os.path.exists(fname) and os.stat(fname).st_size != 0:
            file(fname, 'r')
        else:
            print_error_and_exit(ERROR_STR5)
    else:
        print_error_and_exit(ERROR_STR3 + ERROR_STR4)

if __name__ == "__main__":
    print "-"*70

    f  = read_file()

# --------------------- Tests -----------------------------------
def check_rule_syntax()
    assert check_rule_syntax(Interval(10, 10), Interval(20:50), Interval(1, 50),\
            Interval(30, 40), Interval(12, 12), 'DROP')

    pass
def test_check_args():
    assert check_args(0, 0) == (False, ERROR_STR2)
    assert check_args(1, -1) == (False, ERROR_STR1)
    assert check_args(50000, 10) == (False, ERROR_STR1)
    assert check_args(10, 10) == (True, OK_STR)
    assert check_args(0, 5) == (True, OK_STR)
