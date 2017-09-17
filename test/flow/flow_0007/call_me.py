#!/usr/bin/env python3

import sys


MODULE = "CALL ME"


def main():
    for line in sys.stdin:
        n = int(line)
        if n >= 10:
            sys.exit(n)

        print(n + 1)
        sys.exit(0)


if __name__ == '__main__':
    main()
