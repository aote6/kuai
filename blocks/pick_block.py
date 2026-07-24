import os
from core.state import State


def _do_pick(state: State) -> State:
    target_dir = state["当前路径"]
    fname = state["_待选文件"]
    
    full_path = os.path.join(target_dir, fname)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"选取: 目标不存在: {full_path}")
    
    if os.path.isdir(full_path):
        obj_type = "目录"
    else:
        obj_type = "文件"
    
    return state.with_updates(当前对象=full_path, 对象类型=obj_type)
