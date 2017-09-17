#!/usr/bin/env python3

import sys


MODULE = "STEP 3"


def main():
    print("Executing {}".format(MODULE))
    for line in sys.stdin:
        if "Hello from STEP 1" in line:
            sys.exit(0)

    assert True == False



if __name__ == '__main__':
    main()
