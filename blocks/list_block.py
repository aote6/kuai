import os
from core.state import State


def _do_list(state: State) -> State:
    target_dir = state["当前路径"]
    items = []

    for fname in sorted(os.listdir(target_dir)):
        fpath = os.path.join(target_dir, fname)
        if os.path.isfile(fpath):
            ftype = "文件"
        elif os.path.isdir(fpath):
            ftype = "目录"
        else:
            ftype = "其他"
        size = os.path.getsize(fpath)
        items.append(f"{fname} ({ftype}, {size}字节)")

    return state.with_updates(文件列表=items, 文件数量=len(items))
