import yaml
import json
import copy
import logging
from . import step


class FlowEncoder(json.JSONEncoder):
    def encode(self, obj):
        obj_copy = copy.copy(obj)

        for k in obj.keys():
            if k.startswith('_'):
                obj_copy[k.replace('_', '', 1)] = obj_copy.pop(k)

        if "steps" in obj_copy: 
            obj_copy["steps"] = {s: json.loads(str(obj_copy["steps"][s])) for s in obj_copy["steps"]}

        return json.JSONEncoder.encode(self, obj_copy)


class Flow:
    """
    This class facilitates access and representation of raw YAML
    """

    def __init__(self, data):
        self._parsed_yaml = self._parse_yaml(data)
        self._id = self._parsed_yaml['id'] if 'id' in self._parsed_yaml else None
        self._doc = self._parsed_yaml['doc'] if 'doc' in self._parsed_yaml else None
        self._steps = self._create_steps(self._parsed_yaml['flow']) if 'flow' in self._parsed_yaml else {}
        self._current_step = None

    @property
    def parsed_yaml(self):
        return self._parsed_yaml

    def _parse_yaml(self, data):
        parsed_yaml = yaml.load(data)
        logging.debug("Parsed YAML: {}".format(parsed_yaml))
        return parsed_yaml

    def _create_steps(self, steps):
        """
        Convert steps in a flow from YAML to internal representation
        """

        created_steps = {}

        if steps is None:
            return created_steps

        for st in steps:
            s = step.Step(**st)
            created_steps[s.id] = s

        logging.debug('Created {} steps:\n{}'.format(len(created_steps), created_steps))
        return created_steps

    def next_step(self):
        """
        Return the next step to execute based
        on the exit code from the previous step
        """

        def _is_last_step(step):
            return list(self._steps.items())[-1][0] == step.id

        def _can_proceed(step):
            return step.on_failure is not None \
                or step.on_success is not None \
                or step.on_exit_code is not None

        def _ready_to_stop(step):
            return _is_last_step(step) and not _can_proceed(step)

        def _next_step_id(step):
            if step.exit_code == 0 and step.on_success is not None:
                return step.on_success

            if step.exit_code != 0 and step.on_failure is not None:
                return step.on_failure

            ids = list(self._steps.keys())
            i = ids.index(step.id)

            try:
                return ids[i + 1]
            except IndexError:
                return None

        while True:
            logging.debug('Determining next step (current-step={!r})...'.format(None if self._current_step is None else self._current_step.id))

            if len(self._steps) == 0:
                return

            if self._current_step is None:
                self._current_step = list(self._steps.items())[0][1]
                logging.debug('Next step: {!r}'.format(self._current_step.id))
                yield self._current_step
                continue

            if _ready_to_stop(self._current_step):
                logging.debug('No more steps to process. Stopping!')
                return

            next_step_id = _next_step_id(self._current_step)

            if next_step_id is None:
                return

            self._current_step = self._steps[next_step_id]
            logging.debug('Next step: {!r}'.format(self._current_step.id))
            yield self._current_step

    def __str__(self):
        return json.dumps(self.__dict__, cls=FlowEncoder, indent=4)
