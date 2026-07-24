import os
import shutil
from core.block import Block
from core.state import State


def _do_send(state: State) -> State:
    src = state["当前对象"]
    dest_dir = state.get("目标目录", os.path.expanduser("~/storage/downloads"))

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, os.path.basename(src))
    shutil.copy2(src, dest_path)

    return state.with_updates(当前对象=dest_path, 对象类型="已发送文件", 完成=True)


SendBlock = Block(
    name="发送",
    input_schema=["当前对象", "对象类型"],
    output_schema=["当前对象", "完成"],
    execute_func=_do_send,
)
