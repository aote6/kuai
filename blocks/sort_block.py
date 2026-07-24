import os
import shutil
from core.state import State


def _do_sort(state: State) -> State:
    target_dir = state["当前路径"]
    moved = 0

    for fname in os.listdir(target_dir):
        fpath = os.path.join(target_dir, fname)
        if not os.path.isfile(fpath):
            continue

        # 取扩展名，没有扩展名的归入"其他文件"
        if "." in fname:
            ext = fname.rsplit(".", 1)[1]
            subdir = f"{ext}文件"
        else:
            subdir = "其他文件"

        dest_dir = os.path.join(target_dir, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, fname)
        shutil.move(fpath, dest_path)
        moved += 1

    return state.with_updates(分类数量=moved)
