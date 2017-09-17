from . import flow

class FlowExecutor:
    """
    This class is responsible for flow execution
    """

    def __init__(self, yaml_data):
        self.flow = flow.Flow(yaml_data)

    def execute(self):
        (exit_code, stdout, stderr) = None, None, None

        for step in self.flow.next_step():
            if step.step is not None:
                (exit_code, stdout, stderr) = step.execute(exit_code=exit_code, stdout=stdout, stderr=stderr)

        return (exit_code, stdout, stderr)
