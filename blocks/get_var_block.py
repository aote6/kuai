from core.state import State, StateMismatchError


def _do_get_var(state: State) -> State:
    src_key = state["_取键"]
    dst_key = state["_取目标键"]
    if src_key not in state:
        raise StateMismatchError(f"[取变量] State 中不存在字段 '{src_key}'")
    value = state[src_key]
    new_state = State({k: v for k, v in state.items() if k not in ("_取键", "_取目标键")})
    return new_state.with_updates(**{dst_key: value})
