import os
import shutil
from core.state import State


def _do_batch_rename(state: State) -> State:
    target_dir = state["当前路径"]
    prefix = state["_前缀"]
    ext = state["_扩展名"]
    renamed = 0
    new_paths = []

    for fname in sorted(os.listdir(target_dir)):
        if not fname.endswith(f".{ext}"):
            continue
        src = os.path.join(target_dir, fname)
        if not os.path.isfile(src):
            continue
        
        # 幂等性检查：已有目标前缀则跳过
        if fname.startswith(prefix):
            new_paths.append(src)
            continue
        
        dst = os.path.join(target_dir, f"{prefix}{fname}")
        shutil.move(src, dst)
        new_paths.append(dst)
        renamed += 1

    return state.with_updates(
        重命名数量=renamed,
        当前对象=new_paths,
        对象类型="文件集合",
    )
