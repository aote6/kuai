import os
from core.state import State


def _do_filter(state: State) -> State:
    target_dir = state["当前路径"]
    ext = state["扩展名"]
    matched = []

    for fname in sorted(os.listdir(target_dir)):
        if fname.endswith(f".{ext}"):
            matched.append(os.path.join(target_dir, fname))

    return state.with_updates(筛选结果=matched, 筛选数量=len(matched))
