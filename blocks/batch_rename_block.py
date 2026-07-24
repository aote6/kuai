import os
import shutil
from core.state import State


def _do_batch_rename(state: State) -> State:
    target_dir = state["当前路径"]
    prefix = state["_前缀"]
    ext = state["_扩展名"]
    renamed = 0

    for fname in os.listdir(target_dir):
        if not fname.endswith(f".{ext}"):
            continue
        src = os.path.join(target_dir, fname)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(target_dir, f"{prefix}{fname}")
        shutil.move(src, dst)
        renamed += 1

    return state.with_updates(重命名数量=renamed)
