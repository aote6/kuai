import os
import re
import shutil
from core.state import State


def _do_date_sort(state: State) -> State:
    files = state["筛选结果"]
    base_dir = state["当前路径"]
    moved = 0

    for fpath in files:
        fname = os.path.basename(fpath)
        # 尝试提取日期模式 IMG_20240101
        m = re.search(r'(\d{8})', fname)
        if m:
            date_str = m.group(1)
            year = date_str[:4]
            month = date_str[4:6]
            subdir = os.path.join(base_dir, f"{year}年{month}月")
        else:
            subdir = os.path.join(base_dir, "未分类")

        os.makedirs(subdir, exist_ok=True)
        dest = os.path.join(subdir, fname)
        shutil.move(fpath, dest)
        moved += 1

    return state.with_updates(分类数量=moved)
