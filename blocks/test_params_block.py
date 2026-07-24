from core.state import State

def _do_test(state: State) -> State:
    return state.with_updates(参数结果=f"{state['_a']},{state['_b']},{state['_c']}")
