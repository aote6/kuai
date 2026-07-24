import os
import shutil
from core.block import Block
from core.state import State


def _do_copy(state: State) -> State:
    src = state["当前路径"]
    dst = src + "_副本"

    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

    return state.with_updates(当前对象=dst, 对象类型="文件副本")


CopyBlock = Block(
    name="复制",
    input_schema=["当前路径"],
    output_schema=["当前对象", "对象类型"],
    execute_func=_do_copy,
)
