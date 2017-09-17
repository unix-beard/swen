import logging
import json
from subprocess import Popen, PIPE


class Step:
    """
    This class represents a step in a flow
    """

    def __init__(self, id=None, step=None, doc=None, with_stdin=False, on_success=None, on_failure=None, on_exit_code=None):
        self.id = id
        self.step = step
        self.doc = doc
        self.with_stdin = with_stdin
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_exit_code = on_exit_code
        self._exit_code = None

    def execute(self, exit_code=None, stdout=None, stderr=None):
        logging.debug("Executing step: {}, exit_code={!r}, stdout={!r}, stderr={!r}".format(self, exit_code, stdout, stderr))

        if self.with_stdin:
            return self._execute_with_communicate(stdout)
        else:
            return self._execute_normally()

    def _execute_with_communicate(self, stdout):
        p = Popen(self.step, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        tup = p.communicate(input=stdout)
        self._exit_code = p.returncode

        return (self._exit_code, tup[0], tup[1])

    def _execute_normally(self):
        with Popen(self.step, stdout=PIPE, stderr=PIPE) as p:
            stdout = None if p.stdout is None else p.stdout.read()
            stderr = None if p.stderr is None else p.stderr.read()

        self._exit_code = p.returncode
        return (self._exit_code, stdout, stderr)

    @property
    def exit_code(self):
        return self._exit_code

    def __str__(self):
        return json.dumps(self.__dict__)
