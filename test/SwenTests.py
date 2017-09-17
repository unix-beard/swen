#!/usr/bin/env python3.6

import sys
import os
import logging
import unittest
from pathlib import Path
sys.path.append(str(Path('.').cwd().parent))
from swen import flowexecutor


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.DEBUG
)


class FlowTests(unittest.TestCase):
    """
    Self-testing swen
    """

    def test_swen(self):
        yml_path = "swen_self_tests.yml"
        with open(yml_path) as yml:
            fe = flowexecutor.FlowExecutor(yml) 
            (exit_status, stdout, stderr) = fe.execute()

        self.assertEqual(exit_status, 0)


if __name__ == '__main__':
    unittest.main()
