import os
from core.state import State


def _do_clean(state: State) -> State:
    target_dir = state["当前路径"]
    cleaned = 0

    for fname in os.listdir(target_dir):
        if fname.endswith(".tmp"):
            fpath = os.path.join(target_dir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
                cleaned += 1

    return state.with_updates(清理数量=cleaned)
