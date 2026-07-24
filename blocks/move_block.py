import os
import shutil
from core.state import State


def _do_move(state: State) -> State:
    target = state["当前对象"]
    dest_dir = state["目标目录"]

    if not os.path.isdir(dest_dir):
        raise FileNotFoundError(f"移动: 目标目录不存在: {dest_dir}")

    if isinstance(target, list):
        new_paths = []
        for f in target:
            if not os.path.exists(f):
                raise FileNotFoundError(f"移动: 源路径不存在: {f}")
            name = os.path.basename(f)
            dest = os.path.join(dest_dir, name)
            shutil.move(f, dest)
            new_paths.append(dest)
        return state.with_updates(当前对象=new_paths)

    if not os.path.exists(target):
        raise FileNotFoundError(f"移动: 源路径不存在: {target}")

    name = os.path.basename(target)
    dest = os.path.join(dest_dir, name)
    shutil.move(target, dest)

    return state.with_updates(当前对象=dest)
