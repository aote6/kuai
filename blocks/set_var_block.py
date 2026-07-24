from core.state import State


def _do_set(state: State) -> State:
    key = state["_设置键"]
    value = state["_设置值"]
    new_state = State({k: v for k, v in state.items() if k not in ("_设置键", "_设置值")})
    return new_state.with_updates(**{key: value})
