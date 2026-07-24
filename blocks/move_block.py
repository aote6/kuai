import os
import shutil
from core.block import Block
from core.state import State


def _do_move(state: State) -> State:
    src = state["当前对象"]
    dest_dir = state["目标目录"]

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, os.path.basename(src))
    shutil.move(src, dest_path)

    return state.with_updates(当前对象=dest_path)
