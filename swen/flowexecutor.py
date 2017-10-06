from . import flow
import logging


class FlowExecutor:
    """
    This class is responsible for flow execution
    """

    def __init__(self, yaml_data):
        self.flow = flow.Flow(yaml_data)
        self._execution_graph = []

    def execute(self):
        (exit_code, stdout, stderr) = None, None, None

        for step in self.flow.next_step():
            self._execution_graph.append(step)

            if step.step is not None:
                (exit_code, stdout, stderr) = step.execute(exit_code=exit_code, stdout=stdout, stderr=stderr)
                
                logging.debug("Executed step: {}, exit_code={!r}, stdout={!r}, stderr={!r}".format(step.id, exit_code, stdout, stderr))

                # Terminate the flow if the step exit code is not success
                # and we don't have on_failure transition set explicitly on that step
                if exit_code != 0 and step.on_failure is None:
                    break

        return (exit_code, stdout, stderr)

    @property
    def execution_graph(self):
        return self._execution_graph
