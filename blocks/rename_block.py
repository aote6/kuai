import os
import shutil
from core.state import State


def _do_rename(state: State) -> State:
    src = state["当前对象"]
    new_name = state["新名称"]
    parent = os.path.dirname(src)
    new_path = os.path.join(parent, new_name)

    shutil.move(src, new_path)

    return state.with_updates(当前对象=new_path)
