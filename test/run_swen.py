#!/usr/bin/env python3.6

import logging
import argparse
import yaml
import subprocess
import sys

from pathlib import Path
sys.path.append(str(Path('.').cwd().parent))
from swen import flowexecutor


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.DEBUG
)


def main():
    parser = argparse.ArgumentParser(prog='swen')
    parser.add_argument('-f', '--flow', required=True)

    args = parser.parse_args()

    with open(args.flow) as yml:
        fe = flowexecutor.FlowExecutor(yml) 
        return fe.execute()


if __name__ == '__main__':
    main()
