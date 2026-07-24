import os
from core.state import State


def _do_pick(state: State) -> State:
    base_dir = state["当前路径"]
    fname = state["_待选文件"]
    full_path = os.path.join(base_dir, fname)
    new_state = State({k: v for k, v in state.items() if k != "_待选文件"})
    return new_state.with_updates(当前对象=full_path, 对象类型="文件")
