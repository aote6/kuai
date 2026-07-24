from core.state import State

def _do_hello(state: State) -> State:
    name = state.get("名字", "World")
    return state.with_updates(问候语=f"Hello {name} from Kuai!")
