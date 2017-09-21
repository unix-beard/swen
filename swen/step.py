import logging
import json
import copy
import shlex

from subprocess import Popen, PIPE
from enum import IntEnum


class Status(IntEnum):
    READY = 0
    RUNNING = 1
    TERMINATED = 2
    # TIMED_OUT = 3


class StepEncoder(json.JSONEncoder):
    status = 'status'
    on_status_change = 'on_status_change'

    def encode(self, obj):
        obj_copy = copy.copy(obj)

        for k in obj.keys():
            if k.startswith('_'):
                obj_copy[k.replace('_', '', 1)] = obj_copy.pop(k)

        if StepEncoder.status in obj_copy and type(obj_copy[StepEncoder.status]) is Status:
            obj_copy[StepEncoder.status] = str(obj_copy[StepEncoder.status].name)
        if StepEncoder.on_status_change in obj_copy and callable(obj_copy[StepEncoder.on_status_change]):
            obj_copy[StepEncoder.on_status_change] = obj_copy[StepEncoder.on_status_change].__name__

        return json.JSONEncoder.encode(self, obj_copy)


class Step:
    """
    This class represents a step in a flow
    """

    def __init__(self, id=None, step=None, doc=None, with_stdin=False,
                 on_success=None, on_failure=None, on_exit_code=None):
        self._id = id
        self._step = None if step is None else shlex.split(step)
        self._doc = doc
        self._with_stdin = with_stdin
        self._on_success = on_success
        self._on_failure = on_failure
        self._on_exit_code = on_exit_code
        self._exit_code = None
        self._status = Status.READY
        self._on_status_change = None

    @property
    def id(self):
        return self._id

    @property
    def step(self):
        return self._step

    @property
    def doc(self):
        return self._doc

    @property
    def with_stdin(self):
        return self._with_stdin

    @property
    def on_success(self):
        return self._on_success

    @property
    def on_failure(self):
        return self._on_failure

    @property
    def on_exit_code(self):
        return self._on_exit_code

    @property
    def exit_code(self):
        return self._exit_code

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        """
        Don't just set new status value.
        First notify whoever might be intrested in the state transition.
        """

        if self.on_status_change is not None:
            self.on_status_change(current_status=self.status, new_status=value)
        self._status = value

    @property
    def on_status_change(self):
        return self._on_status_change

    @on_status_change.setter
    def on_status_change(self, callback):
        self._on_status_change = callback

    def execute(self, exit_code=None, stdout=None, stderr=None):
        logging.debug("Executing step: {}, exit_code={!r}, stdout={!r}, stderr={!r}".format(self, exit_code, stdout, stderr))

        self.status = Status.RUNNING

        if self.with_stdin:
            return self._execute_with_communicate(stdout)
        return self._execute_normally()

    def _execute_with_communicate(self, stdout):
        p = Popen(self.step, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        tup = p.communicate(input=stdout)

        self._set_exit_code_and_status(p.returncode, Status.TERMINATED)

        return (self.exit_code, tup[0], tup[1])

    def _execute_normally(self):
        with Popen(self.step, stdout=PIPE, stderr=PIPE) as p:
            stdout = None if p.stdout is None else p.stdout.read()
            stderr = None if p.stderr is None else p.stderr.read()

        self._set_exit_code_and_status(p.returncode, Status.TERMINATED)

        return (self.exit_code, stdout, stderr)

    def _set_exit_code_and_status(self, code, status):
        self._exit_code = code
        self.status = status

    def __str__(self):
        return json.dumps(self.__dict__, cls=StepEncoder, indent=4)
