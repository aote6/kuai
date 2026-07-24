import os
import shutil
from core.state import State


def _do_send(state: State) -> State:
    src = state["当前对象"]
    dest_dir = state.get("目标目录", os.path.expanduser("~/storage/downloads"))

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, os.path.basename(src))
    shutil.copy2(src, dest_path)

    # 最小修改原则：发送是复制到外部目标，不改变对象类型
    return state.with_updates(当前对象=dest_path, 完成=True)
