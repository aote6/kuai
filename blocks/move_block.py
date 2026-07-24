import os
import shutil
from core.state import State


def _do_move(state: State) -> State:
    target = state["当前对象"]
    dest_dir = state["目标目录"]

    if not os.path.exists(target):
        raise FileNotFoundError(f"移动: 源路径不存在: {target}")
    if not os.path.isdir(dest_dir):
        raise FileNotFoundError(f"移动: 目标目录不存在: {dest_dir}")

    name = os.path.basename(target)
    dest = os.path.join(dest_dir, name)
    shutil.move(target, dest)

    # 最小修改原则：移动只变更位置，不触碰语义字段
    return state.with_updates(当前对象=dest)
