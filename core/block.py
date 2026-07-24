from core.state import State, StateMismatchError


class Block:
    def __init__(self, name, input_schema, output_schema, execute_func):
        self.name = name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self._execute = execute_func

    def _check_input(self, input_state: State):
        missing = [k for k in self.input_schema if k not in input_state]
        if missing:
            raise StateMismatchError(
                f"[{self.name}] 缺少必需字段: {missing}，"
                f"当前State字段: {list(input_state.keys())}"
            )

    def execute(self, input_state: State) -> State:
        self._check_input(input_state)
        result = self._execute(input_state)
        if not isinstance(result, State):
            raise TypeError(
                f"[{self.name}] execute_func必须返回State对象，实际返回: {type(result)}"
            )
        if result is input_state:
            raise ValueError(
                f"[{self.name}] execute_func不能原地返回同一个State对象，"
                f"必须用 input_state.with_updates(...) 产生新对象"
            )
        return result
