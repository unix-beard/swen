#!/usr/bin/env python3

import sys


MODULE = "STEP 1"


def main():
    for l in sys.stdin:
        assert "test with args" in l


if __name__ == '__main__':
    main()
