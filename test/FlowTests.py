#!/usr/bin/env python3.6

import sys
import logging
import unittest
import tempfile
from pathlib import Path
sys.path.append(str(Path('.').cwd().parent))
import swen
from swen import flow


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.INFO
)


YAML_1_STEP = """---
version: 1.0
id: "id-test"
doc: "doc-test"
flow:
- id: s_1
  step: ./s_1.py
  doc: "step-test"
"""


YAML_2_STEPS = """---
version: 1.0
id: "id-test"
doc: "doc-test"
flow:
- id: s_1
  step: ./s_1.py
- id: s_2
  step: ./s_2.py
"""


YAML_3_STEPS = """---
version: 1.0
id: "id-test"
doc: "doc-test"
flow:
- id: s_1
  step: ./s_1.py
- id: s_2
  step: ./s_2.py
- id: s_3
  step: ./s_3.py
"""

YAML_4_STEPS = """---
version: 1.0
id: "id-test"
doc: "doc-test"
flow:
- id: s_1
  step: ./s_1.py
  on_failure: s_3
- id: s_2
  step: ./s_2.py
  on_success: s_1
- id: s_3
  step: ./s_3.py
  on_failure: s_2
  with_stdin: yes
"""


YAML_NO_STEPS = """---
version: 1.0
id: "id-test"
doc: "doc-test"
flow:
"""


YAML_NO_FLOW = """---
version: 1.0
id: "id-test"
doc: "doc-test"
"""

EMPTY_FLOW = """
version: 1.0
"""

PARSED_YAML_0 = {
    'version': 1.0,
    'doc': 'doc-test',
    'flow': [{'doc': 'step-test', 'id': 's_1', 'step': './s_1.py'}],
    'id': 'id-test'
}


YAML = [
    (YAML_1_STEP, PARSED_YAML_0),
    (YAML_NO_STEPS, None)
]


class FlowTests(unittest.TestCase):
    def test_yaml_as_string(self):
        f = flow.Flow(YAML[0][0])
        self.assertEqual(f.parsed_yaml, YAML[0][1])

    def test_empty_flow(self):
        f = flow.Flow(EMPTY_FLOW)
        print("Flow {} as JSON:\n".format(f._id))
        print(str(f))

    def test_yaml_as_file(self):
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(YAML_1_STEP.encode('utf-8'))
            tmp_file.seek(0)
            f = flow.Flow(tmp_file)
            self.assertEqual(f.parsed_yaml, YAML[0][1])

    def test_flow_with_no_flow(self):
        f = flow.Flow(YAML_NO_FLOW)
        self.assertEqual(f._steps, {})

    def test_flow_with_no_steps(self):
        f = flow.Flow(YAML_NO_STEPS)
        self.assertEqual(f._steps, {})

    def test_next_step_with_no_flow(self):
        f = flow.Flow(YAML_NO_FLOW)
        self.assertEqual(list(f.next_step()), [])

    def test_next_step_with_no_steps(self):
        f = flow.Flow(YAML_NO_STEPS)
        self.assertEqual(list(f.next_step()), [])

    def test_next_step_with_1_step(self):
        f = flow.Flow(YAML_1_STEP)
        s = None
        for step in f.next_step():
            s = step
        self.assertNotEqual(s, None)
        self.assertIsInstance(s, swen.step.Step)

    def test_flow_as_json_1_step(self):
        f = flow.Flow(YAML_1_STEP)
        print("Flow {} as JSON:\n".format(f._id))
        print(str(f))

    def test_flow_as_json_2_steps(self):
        f = flow.Flow(YAML_2_STEPS)
        print("Flow {} as JSON:\n".format(f._id))
        print(str(f))

    def test_flow_as_json_3_steps(self):
        f = flow.Flow(YAML_3_STEPS)
        print("Flow {} as JSON:\n".format(f._id))
        print(str(f))

    def test_flow_as_json_4_steps(self):
        f = flow.Flow(YAML_4_STEPS)
        print("Flow {} as JSON:\n".format(f._id))
        print(str(f))

if __name__ == '__main__':
    unittest.main()
