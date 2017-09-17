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
from swen import step


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.DEBUG
)


class FlowTests(unittest.TestCase):
    def test_step_successful_execution(self):
        s = step.Step(id="Step with successful execution",
                      step="ls",
                      doc="(with_stdin: False)",
                      with_stdin=False,
                      on_success=None,
                      on_failure=None,
                      on_exit_code=None)
        (exit_code, stdout, stderr) = s.execute()
        self.assertEqual(exit_code, 0)

    def test_step_failed_execution(self):
        s = step.Step(id="Step with failed execution",
                      step="false",
                      doc="(with_stdin: False)",
                      with_stdin=False,
                      on_success=None,
                      on_failure=None,
                      on_exit_code=None)
        (exit_code, stdout, stderr) = s.execute()
        self.assertEqual(exit_code, 1)

    def test_step_successful_execution_with_stdin(self):
        sort_stdin = b"John\nSteven\nBob\nAlice\nLucy\nGloria"
        s = step.Step(id="Step with successful execution",
                      step="sort",
                      doc="(with_stdin: True)",
                      with_stdin=True,
                      on_success=None,
                      on_failure=None,
                      on_exit_code=None)
        (exit_code, stdout, stderr) = s.execute(stdout=sort_stdin)
        self.assertEqual(exit_code, 0)
        self.assertEqual(str(stdout, 'utf-8'), 'Alice\nBob\nGloria\nJohn\nLucy\nSteven\n')

    def test_step_failed_execution_with_stdin(self):
        sort_stdin = b"Some input text that will be ignored by `false`"
        s = step.Step(id="Step with failed execution",
                      step="false",
                      doc="(with_stdin: True)",
                      with_stdin=True,
                      on_success=None,
                      on_failure=None,
                      on_exit_code=None)
        (exit_code, stdout, stderr) = s.execute(stdout=sort_stdin)
        self.assertEqual(exit_code, 1)

if __name__ == '__main__':
    unittest.main()
