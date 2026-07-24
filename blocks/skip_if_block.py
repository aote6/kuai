from core.state import State
from core.engine import SkipRemainingSteps


def _do_skip_if(state: State) -> State:
    field = state["_检查字段"]
    expected = state.get("_期望值")

    if field not in state:
        raise KeyError(f"[条件跳过] State 中不存在字段 '{field}'")

    actual = state[field]

    if expected is not None:
        should_skip = str(actual) == str(expected)
    else:
        should_skip = not actual

    cleaned = State({k: v for k, v in state.items()
                      if k not in ("_检查字段", "_期望值")})

    if should_skip:
        raise SkipRemainingSteps(cleaned)

    return cleaned
