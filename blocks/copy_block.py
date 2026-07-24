import os
import shutil
from core.state import State


def _do_copy(state: State) -> State:
    target = state["当前对象"]
    dest_dir = state["目标目录"]

    if not os.path.exists(target):
        raise FileNotFoundError(f"复制: 源路径不存在: {target}")
    if not os.path.isdir(dest_dir):
        raise FileNotFoundError(f"复制: 目标目录不存在: {dest_dir}")

    name = os.path.basename(target)
    dest = os.path.join(dest_dir, name)

    if os.path.isdir(target):
        shutil.copytree(target, dest)
        obj_type = "目录"
    else:
        shutil.copy2(target, dest)
        obj_type = "文件"

    return state.with_updates(当前对象=dest, 对象类型=obj_type)
