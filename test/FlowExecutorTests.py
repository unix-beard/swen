#!/usr/bin/env python3.6

import sys
import os
import stat
import logging
import unittest
import tempfile
import time
from pathlib import Path
sys.path.append(str(Path('.').cwd().parent))
from swen import flowexecutor


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.DEBUG
)


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.flow_dir = "flow"

    def test_flow_0000(self):
        flow_id = "flow_0000"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, None)
        self.assertEqual(stdout, None)
        self.assertEqual(stderr, None)

    def test_flow_0001(self):
        flow_id = "flow_0001"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 0)

    def test_flow_0002(self):
        flow_id = "flow_0002"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 0)

    def test_flow_0003(self):
        flow_id = "flow_0003"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 0)

    def test_flow_0004(self):
        flow_id = "flow_0004"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 0)

    def test_flow_0005(self):
        flow_id = "flow_0005"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 0)

    def test_flow_0006(self):
        flow_id = "flow_0006"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 0)

    def test_flow_0007(self):
        flow_id = "flow_0007"
        (exit_code, stdout, stderr) = self._call_flow_executor(flow_id)
        self.assertEqual(exit_code, 10)

    def _call_flow_executor(self, flow_id):
        yml_path = self.flow_dir + "/" + "{}/{}.yml".format(flow_id, flow_id)
        logging.info("Testing flow: id={!r}, yaml={!r}".format(flow_id, yml_path))
        with open(yml_path) as yml:
            fe = flowexecutor.FlowExecutor(yml) 
            return fe.execute()


if __name__ == '__main__':
    unittest.main()