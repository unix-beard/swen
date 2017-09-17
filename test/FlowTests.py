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

    def test_flow_with_1_step(self):
        f = flow.Flow(YAML_1_STEP)
        self.assertEqual(
            str(f._steps['s_1']),
            '{"id": "s_1", "step": "./s_1.py", "doc": "step-test", "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}'    
        )

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
        self.assertEqual(
            str(s), 
            '{"id": "s_1", "step": "./s_1.py", "doc": "step-test", "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}' 
        )

    def test_next_step_with_2_steps(self):
        s = {
            's_1': '{"id": "s_1", "step": "./s_1.py", "doc": null, "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}',
            's_2': '{"id": "s_2", "step": "./s_2.py", "doc": null, "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}'
        }

        f = flow.Flow(YAML_2_STEPS)
        for step in f.next_step():
            self.assertEqual(str(step), s[step.id])

    def test_next_step_with_3_steps(self):
        s = {
            's_1': '{"id": "s_1", "step": "./s_1.py", "doc": null, "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}',
            's_2': '{"id": "s_2", "step": "./s_2.py", "doc": null, "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}',
            's_3': '{"id": "s_3", "step": "./s_3.py", "doc": null, "with_stdin": false, "on_success": null, "on_failure": null, "on_exit_code": null, "_exit_code": null}'
        }

        f = flow.Flow(YAML_3_STEPS)
        for step in f.next_step():
            self.assertEqual(str(step), s[step.id])
        

if __name__ == '__main__':
    unittest.main()
